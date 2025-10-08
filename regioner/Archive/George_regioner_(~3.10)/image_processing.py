import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage import filters, morphology, measure, util, feature, segmentation, color
from skimage.morphology import binary_closing
from scipy.ndimage import distance_transform_edt
import pandas as pd

_PREPROCESS_CACHE = {}

def preprocess_for_highlighting(page_id, img):
    if page_id in _PREPROCESS_CACHE:
        return _PREPROCESS_CACHE[page_id]
    img_array = np.array(img)
    gray = np.dot(img_array[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.float32)
    mag = filters.sobel(gray)
    closed_binary = binary_closing(mag)
    skel_binary = morphology.skeletonize(closed_binary)
    barrier = np.ones((img.height, img.width), dtype=np.uint8) * 255
    barrier[skel_binary] = 0
    barrier_img = Image.fromarray(barrier, mode="L")
    _PREPROCESS_CACHE[page_id] = barrier_img
    return barrier_img

def clear_preprocess_cache():
    _PREPROCESS_CACHE.clear()

def count_cells_in_zones(background_pil, mask_pil, page_pil, img_x, img_y, zone_counters, zone_names):
    bg_arr = np.array(background_pil)
    if bg_arr.ndim == 3:
        if bg_arr.shape[2] == 4:
            rgb = color.rgba2rgb(bg_arr)
            img2d = color.rgb2gray(rgb)
        else:
            img2d = color.rgb2gray(bg_arr)
    else:
        img2d = bg_arr.astype(float) / 255.0
    intensity = util.img_as_float(img2d)
    intensity = filters.gaussian(intensity, sigma=2.0)
    thresh = filters.threshold_otsu(intensity)
    binary = intensity > thresh
    binary = morphology.remove_small_objects(binary, min_size=20)
    distance = distance_transform_edt(binary)
    coords = feature.peak_local_max(distance, min_distance=5, exclude_border=True)
    markers = np.zeros(distance.shape, dtype=bool)
    if coords.size:
        markers[tuple(coords.T)] = True
    markers = measure.label(markers)
    labels = segmentation.watershed(-distance, markers, mask=binary)
    props = measure.regionprops(labels)
    counts = {}
    max_zone = max(zone_counters.values()) if zone_counters else 0
    for i in range(1, max_zone + 1):
        counts[i] = 0
    filtered_props = []
    mask_arr = np.array(mask_pil)
    for prop in props:
        row, col = prop.centroid
        ax = int(col - img_x)
        ay = int(row - img_y)
        if 0 <= ax < mask_pil.width and 0 <= ay < mask_pil.height:
            zone_id = mask_arr[ay, ax]
            if zone_id > 0:
                counts.setdefault(zone_id, 0)
                counts[zone_id] += 1
                filtered_props.append(prop)
    bg_min = img2d.min()
    bg_max = img2d.max()
    if bg_max > bg_min:
        norm = (img2d - bg_min) / (bg_max - bg_min)
    else:
        norm = np.zeros_like(img2d)
    img_uint8 = (norm * 255).astype('uint8')
    img_rgb = np.stack([img_uint8]*3, axis=-1)
    annotated = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(annotated)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
    for i, prop in enumerate(filtered_props, start=1):
        r, c = prop.centroid
        draw.text((int(c), int(r)), str(i), fill=(255,0,0), font=font)
    annotated = annotated.convert('RGBA')
    zone_list, count_list = [], []
    for zid in sorted(counts.keys()):
        name = zone_names.get(zid, f"Zone {zid}")
        zone_list.append(name)
        count_list.append(counts[zid])
    df = pd.DataFrame({'Zone': zone_list, 'Cell_Count': count_list})
    return annotated, df, counts

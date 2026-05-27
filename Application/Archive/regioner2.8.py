import fitz  # PyMuPDF
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk, messagebox
import numpy as np
from scipy.ndimage import sobel, binary_dilation, binary_erosion, label, gaussian_filter
from skimage import filters, morphology, measure, util, feature, segmentation, color
from scipy import ndimage as ndi
import pandas as pd

class PDFViewer:
    def __init__(self, master):
        self.master = master
        self.master.title('PDF Viewer with Highlighting')
        self.master.geometry('1200x1200')
        self.master.resizable(True, True)
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=0)
        self.master.columnconfigure(0, weight=1)

        self.path = None
        self.doc = None
        self.current_page = 0
        self.num_pages = 0
        self.zoom = 4.0  # Increased for higher quality
        self.page_images = {}
        self.mask_images = {}
        self.zone_counters = {}

        # Crop variables
        self.crop_mode = False
        self.crop_rect = None
        self.start_x = None
        self.start_y = None

        # Edit mode variables
        self.edit_mode = False
        self.img_x = 0
        self.img_y = 0
        self.drag_start_x = None
        self.drag_start_y = None

        # Background image
        self.background_image = None

        # Menu
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)
        filemenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open File", command=self.open_file)
        filemenu.add_command(label="Exit", command=self.master.destroy)

        # Top frame for canvas
        self.top_frame = ttk.Frame(self.master)
        self.top_frame.grid(row=0, column=0, sticky='nsew')
        self.top_frame.rowconfigure(0, weight=1)
        self.top_frame.columnconfigure(0, weight=1)

        # Bottom frame for buttons
        self.bottom_frame = ttk.Frame(self.master)
        self.bottom_frame.grid(row=1, column=0, sticky='ew')

        # Scrollbars
        self.scrolly = tk.Scrollbar(self.top_frame, orient=tk.VERTICAL)
        self.scrolly.grid(row=0, column=1, sticky='ns')
        self.scrollx = tk.Scrollbar(self.top_frame, orient=tk.HORIZONTAL)
        self.scrollx.grid(row=1, column=0, sticky='ew')

        # Canvas
        self.output = tk.Canvas(self.top_frame, bg='#ECE8F3')
        self.output.configure(yscrollcommand=self.scrolly.set, xscrollcommand=self.scrollx.set)
        self.output.grid(row=0, column=0, sticky='nsew')
        self.scrolly.configure(command=self.output.yview)
        self.scrollx.configure(command=self.output.xview)

        # Bind click event for highlighting
        self.output.bind("<Button-1>", self.highlight_region)

        # Navigation buttons (simple prev/next)
        ttk.Button(self.bottom_frame, text="Previous", command=self.previous_page).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(self.bottom_frame, text="Next", command=self.next_page).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(self.bottom_frame, text="Crop", command=self.toggle_crop_mode).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(self.bottom_frame, text="Edit Mode", command=self.toggle_edit_mode).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(self.bottom_frame, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(self.bottom_frame, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(self.bottom_frame, text="Import TIFF", command=self.import_tiff).pack(side=tk.LEFT, padx=10, pady=10)

        # Rotation entry
        self.rotation_label = ttk.Label(self.bottom_frame, text="Rotate (degrees):")
        self.rotation_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.rotation_entry = ttk.Entry(self.bottom_frame, width=10)
        self.rotation_entry.pack(side=tk.LEFT, padx=5, pady=10)
        ttk.Button(self.bottom_frame, text="Rotate", command=self.rotate_custom).pack(side=tk.LEFT, padx=10, pady=10)

        # Resize entry
        self.scale_label = ttk.Label(self.bottom_frame, text="Scale:")
        self.scale_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.scale_entry = ttk.Entry(self.bottom_frame, width=10)
        self.scale_entry.pack(side=tk.LEFT, padx=5, pady=10)
        ttk.Button(self.bottom_frame, text="Resize", command=self.resize_custom).pack(side=tk.LEFT, padx=10, pady=10)

        # Count Cells button (initially not packed)
        self.count_button = ttk.Button(self.bottom_frame, text="Count Cells", command=self.count_cells)
        self.count_button_packed = False

    def toggle_crop_mode(self):
        self.crop_mode = not self.crop_mode
        if self.crop_mode:
            self.output.bind("<Button-1>", self.crop_start)
            self.output.bind("<B1-Motion>", self.crop_drag)
            self.output.bind("<ButtonRelease-1>", self.crop_end)
        else:
            self.output.bind("<Button-1>", self.highlight_region)
            self.output.unbind("<B1-Motion>")
            self.output.unbind("<ButtonRelease-1>")
            if self.crop_rect:
                self.output.delete(self.crop_rect)
                self.crop_rect = None

    def crop_start(self, event):
        self.start_x = self.output.canvasx(event.x)
        self.start_y = self.output.canvasy(event.y)
        if self.crop_rect:
            self.output.delete(self.crop_rect)
        self.crop_rect = self.output.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', dash=(4, 4))

    def crop_drag(self, event):
        cur_x = self.output.canvasx(event.x)
        cur_y = self.output.canvasy(event.y)
        self.output.coords(self.crop_rect, self.start_x, self.start_y, cur_x, cur_y)

    def crop_end(self, event):
        end_x = self.output.canvasx(event.x)
        end_y = self.output.canvasy(event.y)
        # Get crop coordinates
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        right = max(self.start_x, end_x)
        bottom = max(self.start_y, end_y)
        # Crop the image
        img = self.load_page_image()
        cropped_img = img.crop((left, top, right, bottom))
        # Make white background transparent
        cropped_array = np.array(cropped_img)
        white_mask = np.all(cropped_array[:, :, :3] >= 250, axis=-1)  # Near-white pixels
        cropped_array[white_mask, 3] = 0  # Set alpha to 0 for transparency
        cropped_img = Image.fromarray(cropped_array)
        self.page_images[self.current_page] = cropped_img
        # Crop the mask
        mask_img = self.mask_images[self.current_page]
        cropped_mask = mask_img.crop((left, top, right, bottom))
        self.mask_images[self.current_page] = cropped_mask
        self.show_page()
        # Exit crop mode
        self.toggle_crop_mode()
        # Show the Count Cells button after cropping
        if not self.count_button_packed:
            self.count_button.pack(side=tk.LEFT, padx=10, pady=10)
            self.count_button_packed = True

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.output.bind("<Button-1>", self.drag_start)
            self.output.bind("<B1-Motion>", self.drag_move)
        else:
            self.output.bind("<Button-1>", self.highlight_region)
            self.output.unbind("<B1-Motion>")

    def drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_move(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.img_x += dx
        self.img_y += dy
        self.show_page()
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def rotate_custom(self):
        try:
            degrees = float(self.rotation_entry.get())
            img = self.page_images[self.current_page]
            rotated = img.rotate(degrees, expand=True)
            self.page_images[self.current_page] = rotated
            mask_img = self.mask_images[self.current_page]
            rotated_mask = mask_img.rotate(degrees, expand=True, resample=Image.NEAREST)
            self.mask_images[self.current_page] = rotated_mask
            self.show_page()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for rotation degrees.")

    def zoom_in(self):
        img = self.page_images[self.current_page]
        new_size = (int(img.width * 1.1), int(img.height * 1.1))
        resized = img.resize(new_size, Image.BILINEAR)  # Changed to BILINEAR for speed
        self.page_images[self.current_page] = resized
        mask_img = self.mask_images[self.current_page]
        resized_mask = mask_img.resize(new_size, Image.NEAREST)
        self.mask_images[self.current_page] = resized_mask
        self.show_page()

    def zoom_out(self):
        img = self.page_images[self.current_page]
        new_size = (int(img.width * 0.9), int(img.height * 0.9))
        resized = img.resize(new_size, Image.BILINEAR)  # Changed to BILINEAR for speed
        self.page_images[self.current_page] = resized
        mask_img = self.mask_images[self.current_page]
        resized_mask = mask_img.resize(new_size, Image.NEAREST)
        self.mask_images[self.current_page] = resized_mask
        self.show_page()

    def resize_custom(self):
        try:
            scale = float(self.scale_entry.get())
            if scale <= 0:
                raise ValueError("Scale must be positive")
            img = self.page_images[self.current_page]
            new_size = (int(img.width * scale), int(img.height * scale))
            resized = img.resize(new_size, Image.BILINEAR)  # Changed to BILINEAR for speed
            self.page_images[self.current_page] = resized
            mask_img = self.mask_images[self.current_page]
            resized_mask = mask_img.resize(new_size, Image.NEAREST)
            self.mask_images[self.current_page] = resized_mask
            self.show_page()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for scale factor.")

    def import_tiff(self):
        tiff_path = fd.askopenfilename(filetypes=[("TIFF files", "*.tiff *.tif")])
        if tiff_path:
            self.background_image = Image.open(tiff_path)
            array = np.array(self.background_image)
            if array.ndim == 2 or (array.ndim == 3 and array.shape[2] == 1):  # Grayscale
                array = np.squeeze(array)
                array_norm = (array - array.min()) / (array.max() - array.min() + 1e-8) * 255
                self.background_image = Image.fromarray(array_norm.astype(np.uint8)).convert('RGBA')
            elif array.max() <= 1.0:  # Float image
                array = (array * 255).astype(np.uint8)
                self.background_image = Image.fromarray(array).convert('RGBA')
            else:
                self.background_image = self.background_image.convert('RGBA')
            self.show_page()

    def open_file(self):
        self.path = fd.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("SVG files", "*.svg")])
        if self.path:
            self.doc = fitz.open(self.path)
            self.num_pages = len(self.doc)
            self.current_page = 0
            self.page_images = {}
            self.mask_images = {}
            self.zone_counters = {}
            self.show_page()

    def load_page_image(self):
        if self.doc:
            if self.current_page not in self.page_images:
                page = self.doc[self.current_page]
                mat = fitz.Matrix(self.zoom, self.zoom)
                pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=True)
                img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
                self.page_images[self.current_page] = img
                self.mask_images[self.current_page] = Image.new('L', (img.width, img.height), 0)
                self.zone_counters[self.current_page] = 0
            return self.page_images[self.current_page]

    def show_page(self):
        img = self.load_page_image()
        self.photo = ImageTk.PhotoImage(img)
        self.output.delete("all")
        if self.background_image:
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.output.create_image(0, 0, image=self.background_photo, anchor='nw')
        self.output.create_image(self.img_x, self.img_y, image=self.photo, anchor='nw')
        self.output.config(scrollregion=self.output.bbox(tk.ALL))

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def next_page(self):
        if self.current_page < self.num_pages - 1:
            self.current_page += 1
            self.show_page()

    def highlight_region(self, event):
        if not self.doc or self.crop_mode or self.edit_mode:
            return
        canvas_x = self.output.canvasx(event.x)
        canvas_y = self.output.canvasy(event.y)
        x = int(canvas_x)
        y = int(canvas_y)
        img = self.load_page_image()
        if x < 0 or y < 0 or x >= img.width or y >= img.height:
            return

        # Convert to numpy array
        img_array = np.array(img)

        # Grayscale for edge detection
        gray = np.dot(img_array[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.float32)

        # Compute gradients using Sobel
        dx = sobel(gray, axis=0)
        dy = sobel(gray, axis=1)
        mag = np.hypot(dx, dy)

        # Threshold for edges without normalization
        edge_thresh = 1  # Lowered further to capture very subtle gradients from the light blue lines
        binary = (mag > edge_thresh).astype(bool)

        # Dilate to close gaps in dotted lines
        structure = np.ones((3, 3), dtype=bool)  # Smaller structure to avoid over-dilation
        closed_binary = binary_dilation(binary, structure=structure, iterations=1)

        # Create barrier image: 255 for fillable areas, 0 for barriers
        barrier = np.ones((img.height, img.width), dtype=np.uint8) * 255
        barrier[closed_binary] = 0
        width, height = img.width, img.height
        barrier_img = Image.new('L', (width, height))
        barrier_img.putdata(barrier.flatten())

        # Get seed value
        seed_value = barrier_img.getpixel((x, y))

        if seed_value != 255:
            return  # Clicked on a barrier, do nothing

        # Increment zone id
        self.zone_counters[self.current_page] += 1
        zone_id = self.zone_counters[self.current_page]

        # Floodfill on barrier_img: fill with zone_id
        ImageDraw.floodfill(barrier_img, (x, y), zone_id, thresh=0)  # Exact match for strict boundaries

        # Get mask
        filled = np.array(barrier_img)
        mask = (filled == zone_id)

        # Update mask image
        mask_img = self.mask_images[self.current_page]
        mask_array = np.array(mask_img)
        mask_array[mask] = zone_id
        self.mask_images[self.current_page] = Image.fromarray(mask_array)

        # Apply translucent yellow overlay
        img_array[..., :3][mask] = [255, 255, 0]  # Set RGB to yellow
        img_array[..., 3][mask] = 18  # Set alpha to 18 (~7% opacity)

        # Update image
        updated_img = Image.fromarray(img_array)
        self.page_images[self.current_page] = updated_img
        self.photo = ImageTk.PhotoImage(updated_img)
        self.output.delete("all")
        if self.background_image:
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.output.create_image(0, 0, image=self.background_photo, anchor='nw')
        self.output.create_image(self.img_x, self.img_y, image=self.photo, anchor='nw')
        self.output.config(scrollregion=self.output.bbox(tk.ALL))

    def count_cells(self):
        if self.background_image is None:
            messagebox.showerror("Error", "Please import a TIFF file first.")
            return

        if self.current_page not in self.mask_images:
            messagebox.showerror("Error", "Please load and select regions in the atlas first.")
            return

        # Load image (preserve original bit depth and channels)
        img = np.array(self.background_image)
        
        # Handle possible 3D with single channel or color; force to grayscale
        if len(img.shape) == 3:
            if img.shape[2] == 1:
                img = np.squeeze(img)
            elif img.shape[2] == 3:
                img = color.rgb2gray(img)
            elif img.shape[2] == 4:
                img = color.rgba2rgb(img)
                img = color.rgb2gray(img)
            else:
                raise ValueError("Unsupported number of channels")
        
        # Now img is 2D
        
        # For intensity: convert to float (bright regions positive)
        intensity = util.img_as_float(img)
        
        # Apply Gaussian filter to reduce noise (adjust sigma for fluorescence noise)
        intensity = filters.gaussian(intensity, sigma=2.0)
        
        # Otsu thresholding for bright objects on dark background
        thresh = filters.threshold_otsu(intensity)
        binary = intensity > thresh
        
        # Remove small objects (adjust min_size based on image resolution/cell size, e.g., for small fluorescent spots)
        binary = morphology.remove_small_objects(binary, min_size=20)
        
        # Distance transform for watershed
        distance = ndi.distance_transform_edt(binary)
        
        # Find local maxima as markers (adjust min_distance for cell spacing in fluorescent images)
        coords = feature.peak_local_max(distance, min_distance=5, exclude_border=True)
        markers = np.zeros(distance.shape, dtype=bool)
        markers[tuple(coords.T)] = True
        markers = measure.label(markers)
        
        # Watershed segmentation to separate touching cells
        labels = segmentation.watershed(-distance, markers, mask=binary)
        
        # Get all region properties
        props = measure.regionprops(labels)
        
        # Initialize counts
        max_zone = self.zone_counters.get(self.current_page, 0)
        counts = {i: 0 for i in range(1, max_zone + 1)}
        filtered_props = []
        
        # Filter props based on mask and count per zone
        mask_img = self.mask_images[self.current_page]
        atlas_img = self.page_images[self.current_page]
        for prop in props:
            y, x = prop.centroid  # row, col on background
            ax = int(x - self.img_x)
            ay = int(y - self.img_y)
            if 0 <= ax < atlas_img.width and 0 <= ay < atlas_img.height:
                zone_id = mask_img.getpixel((ax, ay))
                if zone_id > 0:
                    counts[zone_id] += 1
                    filtered_props.append(prop)
        
        # Normalize original image to full range for visibility (stretch contrast)
        img_min = img.min()
        img_max = img.max()
        if img_max > img_min:
            img_norm = (img - img_min) / (img_max - img_min)
        else:
            img_norm = np.zeros_like(img, dtype=float)
        img_uint8 = util.img_as_ubyte(img_norm)
        
        # Convert to RGB for color annotation
        img_rgb = color.gray2rgb(img_uint8)
        
        original = Image.fromarray(img_rgb)
        
        draw = ImageDraw.Draw(original)
        try:
            font = ImageFont.truetype("arial.ttf", 15)
        except IOError:
            font = ImageFont.load_default()  # Fallback if font not found
        
        # Annotate only filtered props
        centroids = [(int(prop.centroid[1]), int(prop.centroid[0])) for prop in filtered_props]  # (x, y) where x=col, y=row
        
        for i, prop in enumerate(filtered_props, start=1):
            y, x = prop.centroid  # (row, col)
            draw.text((int(x), int(y)), str(i), fill=(255, 0, 0), font=font)
        
        self.background_image = original.convert('RGBA')
        self.show_page()

        # Create Excel file
        df = pd.DataFrame({'Zone': list(counts.keys()), 'Cell_Count': list(counts.values())})
        df = df.sort_values('Zone')  # Sort by zone id
        save_path = fd.asksaveasfilename(title="Save Excel File", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            df.to_excel(save_path, index=False)
            messagebox.showinfo("Cell Counts Saved", f"Cell counts per zone saved to: {save_path}")
        else:
            messagebox.showinfo("Cell Counts", f"Cell counts per zone: {counts}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewer(root)
    root.mainloop()
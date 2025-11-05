# Mask Settings Documentation

## Cell Detection Settings

### Threshold Method
- Options: otsu, adaptive, local, manual
- Controls how the image is converted to binary (black and white) for cell detection
- OTSU: Automatically determines optimal threshold using Otsu's method
- Adaptive: Uses local areas to determine threshold, good for varying brightness
- Local: Similar to adaptive but with different implementation
- Manual: Uses a fixed threshold value you specify

### Manual Threshold
- Range: 0.0 to 1.0
- Only used when threshold_method is "manual"
- Higher values make cell detection more selective (fewer cells detected)
- Lower values make detection more sensitive (more cells detected)

### Adaptive Block Size
- Must be an odd integer (e.g., 51, 101, 151)
- Size of the local region used for adaptive thresholding
- Larger values consider more surrounding area
- Smaller values are more sensitive to local changes
- Recommended range: 51-151 pixels

### Local Radius
- Integer value (typically 5-30)
- Size of the neighborhood for local thresholding
- Similar to adaptive block size but for local threshold method
- Larger values smooth out noise but might miss smaller cells

### Min Cell Size
- Integer value (pixels)
- Minimum area for a region to be considered a cell
- Helps filter out noise and artifacts
- Typically 20-50 pixels depending on image resolution

### Max Cell Size
- Integer value (pixels)
- Maximum area for a region to be considered a cell
- Helps filter out clumps or non-cell objects
- Typically 100-200 pixels depending on image resolution

### Circularity Threshold
- Range: 0.0 to 1.0
- How circular a region must be to be considered a cell
- 1.0 is perfectly circular
- Lower values allow more irregular shapes
- Typical value: 0.7

### Min Peak Distance
- Integer value (pixels)
- Minimum distance between detected cell centers
- Helps separate touching cells
- Typically 5-10 pixels

### Peak Min Intensity
- Range: 0.0 to 1.0
- Minimum brightness for cell detection
- Higher values only detect brighter cells
- Lower values detect dimmer cells
- Typical value: 0.1

### Watershed Compactness
- Range: 0.0 to 1.0
- Controls cell separation in watershed algorithm
- Higher values prefer more compact (rounder) regions
- Lower values follow intensity gradients more closely
- Typical value: 0.0

### Base Multiplier
- Range: typically 0.5 to 2.0
- Base sensitivity for cell detection
- Higher values make detection more selective
- Lower values make detection more sensitive
- Default: 1.1

### Sensitivity Range
- Range: typically 0.1 to 1.0
- How much the sensitivity slider can adjust detection
- Larger values give the slider more effect
- Smaller values give finer control
- Default: 0.2

## Preprocessing Settings

### Background Method
- Options: "tophat", "none"
- Controls how background is removed
- Tophat: Uses morphological operations to remove large-scale variations
- None: No background correction

### Ball Radius
- Integer value (pixels)
- Size of the structural element for background correction
- Larger values remove larger-scale background variations
- Smaller values preserve more detail
- Default: 15

### Denoise Method
- Options: "gaussian", "median", "bilateral"
- Type of noise reduction applied
- Gaussian: Smooth Gaussian blur
- Median: Better at preserving edges
- Bilateral: Preserves edges while smoothing

### Gaussian Sigma
- Range: typically 0.1 to 5.0
- Amount of Gaussian blur applied
- Higher values give more smoothing
- Only used when denoise_method is "gaussian"

### Median Kernel
- Integer value (pixels)
- Size of the median filter kernel
- Larger values give more smoothing
- Only used when denoise_method is "median"

### Bilateral Sigma Color
- Range: typically 0.1 to 1.0
- Color sensitivity for bilateral filter
- Higher values blend colors more
- Only used when denoise_method is "bilateral"

### Bilateral Sigma Space
- Range: typically 1.0 to 10.0
- Spatial sensitivity for bilateral filter
- Higher values blend larger areas
- Only used when denoise_method is "bilateral"

### Contrast Method
- Options: "stretch", "clahe", "gamma"
- Type of contrast enhancement
- Stretch: Simple contrast stretching
- CLAHE: Contrast Limited Adaptive Histogram Equalization
- Gamma: Gamma correction

### CLAHE Kernel
- Integer value (typically 8-16)
- Size of local area for CLAHE
- Only used when contrast_method is "clahe"

### CLAHE Clip Limit
- Range: typically 1.0 to 4.0
- Limits contrast enhancement to reduce noise
- Only used when contrast_method is "clahe"

### Gamma
- Range: typically 0.1 to 5.0
- Gamma correction value
- Values < 1 brighten image
- Values > 1 darken image
- Only used when contrast_method is "gamma"

### Enhance Method
- Options: "unsharp_mask"
- Type of image enhancement
- Unsharp mask: Sharpens image details

### Unsharp Radius
- Range: typically 0.1 to 5.0
- Radius of the unsharp mask
- Larger values affect larger features

### Unsharp Amount
- Range: typically 0.1 to 5.0
- Strength of the unsharp mask
- Larger values give stronger sharpening
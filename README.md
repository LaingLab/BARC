# Regional IF Analyzer

A GUI tool for analyzing immunofluorescence images with atlas region mapping and automated cell counting.

## Description

The Regional IF Analyzer is designed to help researchers analyze immunofluorescence images by:
- Overlaying atlas sections onto TIFF images
- Highlighting and naming specific regions of interest
- Detecting and counting cells within defined regions
- Exporting results to Excel files
- Saving annotated images

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- tkinter (usually comes with Python, but may need separate installation on Linux)

On Ubuntu/Debian Linux, you might need to install tkinter separately:
```bash
sudo apt-get install python3-tk
```

### Setting Up

1. Clone the repository:
```bash
git clone https://github.com/LaingLab/BARC.git
cd BARC
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Program

1. Navigate to the program directory:
```bash
cd Application
```

2. Run the program:
```bash
python Application/barcc.py
```

## Basic Usage

1. **Import TIFF Image**:
   - Click "File > Import TIFF"
   - Select your TIFF image file

2. **Determine Regions**

   a. *Draw Region of Interest*:
      - Click "Paint > Start Paint"
      - Draw a circle around the ROI
      - Once done, click "Paint > Stop Paint"
   
   b. *Import Atlas Section*:
      - Click "File > Import Atlas Section"
      - Select your PDF atlas file

3. **Align Atlas**:
   - Use "Move Atlas" button to position the atlas over your image
   - Use rotation and scaling controls if needed

4. **Define Regions**:
   - Click on regions to highlight them
   - Name each region when prompted

5. **Verify Mask**:
   - Click "Mask > Show Mask"
   - Adjust detection with "Mask > Show Mask Settings"
   - Manually add and remove cells under "Mask > Add/Remove Cells"

7. **Count Cells**:
   - Click "Count Cells" to analyze
   - Save results to Excel when prompted

## Common Issues

- If tkinter is missing: Install python3-tk package via your system's package manager
- If images don't load: Ensure your TIFF files are in a compatible format
- For PDF loading issues: Ensure PyMuPDF is properly installed

## Support

For issues and feature requests, please open an issue in the GitHub repository.

## License


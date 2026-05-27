# BARCC v8.01.000

This is a significant release with major improvements to cell detection, parameter tuning, and workflow automation.

## Highlights

- **New Blob Detection Engine** (default): Replaced the primary detection method with skimage.feature.blob_log for much more accurate results on immunofluorescence images.
- **Smart Suggest (Offline)**: New fully local AI-like assistant in Mask Settings that analyzes your image and suggests optimized parameters. Completely private — no data leaves your computer.
- **Left File Browser Pane**: Browse all TIFFs in a folder directly in the app, with visual indicators showing which images have already been counted.
- **Automatic Exports**: "Count Cells" now automatically saves:
  - {image}.xlsx (with Cell Counts + full Detection Parameters metadata sheet)
  - {image}_masked.tif (original + final cell mask overlay)
- **Export / Import Settings**: Save and load complete detection configurations as portable .json files.
- **Improved UX**: Brush size dialog auto-opens for Add/Remove Cell, better Autotune behavior, fixed transparency mode, and many stability fixes.

## Other Changes
- Full rewrite and expansion of the User Manual and README for v8.01.
- Various bug fixes around painted regions, ProgressDialogs, and menu behavior.

## Requirements
For full .xlsx support with metadata, install:
pip install openpyxl xlsxwriter

Full changelog and updated manual available in the repository.


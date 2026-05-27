import fitz
from PIL import Image

class PDFHandler:
    def __init__(self):
        self.doc = None
        self.num_pages = 0

    def open_pdf(self, path):
        self.doc = fitz.open(path)
        self.num_pages = len(self.doc)
        return self.doc, self.num_pages

    def render_page(self, page_index, zoom):
        if self.doc is None:
            raise RuntimeError("No PDF opened")
        page = self.doc[page_index]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=True)
        img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
        return img

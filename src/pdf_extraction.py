from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
import os

def extract_drawing(pdf_path, page_number):
    """Extract the specific page from the PDF as an image."""
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        writer.add_page(reader.pages[page_number - 1])  # Zero-indexed

        temp_pdf_path = "temp_page.pdf"
        with open(temp_pdf_path, "wb") as temp_pdf:
            writer.write(temp_pdf)

        # Convert PDF page to image
        images = convert_from_path(temp_pdf_path, dpi=300)
        os.remove(temp_pdf_path)  # Cleanup temp file
        return images[0]  # Return the first image
    except Exception as e:
        raise ValueError(f"Error extracting drawing from PDF: {e}")

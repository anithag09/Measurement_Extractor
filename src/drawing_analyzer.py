import pytesseract

# Ensure Tesseract is installed and configured
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Update for your system

class DrawingAnalyzer:
    def analyze_drawing(self, drawing, question):
        """Analyze the drawing (image) and return the answer for the given question."""
        try:
            # Perform OCR on the drawing
            ocr_text = pytesseract.image_to_string(drawing)

            # Match specific keywords in the question
            if "diameter" in question.lower():
                return self.extract_diameter(ocr_text)
            elif "length" in question.lower():
                return self.extract_length(ocr_text)
            else:
                return "No relevant data found"
        except Exception as e:
            raise ValueError(f"Error analyzing drawing: {e}")

    def extract_diameter(self, ocr_text):
        """Extract diameter-related information from OCR text."""
        import re
        matches = re.findall(r"\d+(\.\d+)?", ocr_text)
        return ", ".join(matches) if matches else "No diameter found"

    def extract_length(self, ocr_text):
        """Extract length-related information from OCR text."""
        import re
        matches = re.findall(r"\d+(\.\d+)? mm", ocr_text)
        return ", ".join(matches) if matches else "No length found"

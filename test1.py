import pandas as pd
import fitz
import re
import openpyxl
from pathlib import Path
import logging
import cv2
import numpy as np
from PIL import Image
import torch
from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification, LayoutLMv3TokenizerFast
from paddleocr import PaddleOCR
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrawingAnalyzer:
    def __init__(self, pdf_path, excel_path):
        self.pdf_path = pdf_path
        self.excel_path = excel_path
        self.pdf_content = {}
        self.questions = {}
        self.images = {}
        self.required_pages = set()
        
        # Initialize OCR
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        
        # Initialize LayoutLM for document understanding
        self.processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
        self.tokenizer = LayoutLMv3TokenizerFast.from_pretrained("microsoft/layoutlmv3-base")
        self.model = LayoutLMv3ForSequenceClassification.from_pretrained("microsoft/layoutlmv3-base", num_labels=2)
        
        # Define dimension patterns
        self.dimension_patterns = {
            'hole_diameter': r'(?:P|Ø|ϕ)\s*(\d+(?:\.\d+)?)',
            'length': r'(?<!\w)(\d+(?:\.\d+)?)\s*(?:mm)?(?!\w)',
            'angle': r'(\d+)\s*(?:°|deg|X)',
            'counterbore': r'(?:P|Ø|ϕ)\s*(\d+(?:\.\d+)?)\s*(?:THRU|THROUGH)?\s*[Xx]\s*(?:P|Ø|ϕ)\s*(\d+(?:\.\d+)?)\s*[Zz]\s*(\d+(?:\.\d+)?)',
            'center_distance': r'(\d+(?:\.\d+)?)\s*(?:PLCS|PLACES|PLC)',
        }

    def extract_pdf_content(self):
        """Extract content using OCR and LayoutLM"""
        try:
            pdf_document = fitz.open(self.pdf_path)
            
            for page_num in range(pdf_document.page_count):
                current_page = page_num + 1
                
                if current_page in self.required_pages:
                    page = pdf_document[page_num]
                    
                    # Convert PDF page to image
                    zoom = 2
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    opencv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
                    # Save temporary image for OCR
                    temp_img_path = f"temp_page_{current_page}.png"
                    cv2.imwrite(temp_img_path, opencv_img)
                    
                    # Perform OCR
                    ocr_result = self.ocr.ocr(temp_img_path, cls=True)
                    
                    # Process OCR results
                    text_blocks = []
                    boxes = []
                    for result in ocr_result[0]:
                        text = result[1][0]
                        box = result[0]
                        text_blocks.append(text)
                        boxes.append(box)
                    
                    # Use LayoutLM to understand document structure
                    encoded_inputs = self.processor(
                        Image.open(temp_img_path),
                        text=text_blocks,
                        boxes=boxes,
                        return_tensors="pt",
                        truncation=True
                    )
                    
                    # Store processed results
                    self.pdf_content[current_page] = {
                        'text': ' '.join(text_blocks),
                        'boxes': boxes,
                        'layout': encoded_inputs
                    }
                    
                    # Clean up temporary file
                    os.remove(temp_img_path)
                    
                    # Store image for visualization if needed
                    self.images[current_page] = opencv_img
                    
            pdf_document.close()
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            raise

    def find_dimension_by_context(self, page_data, context_keywords, pattern_type):
        """Find dimensions based on context and spatial relationship"""
        text = page_data['text']
        boxes = page_data['boxes']
        pattern = self.dimension_patterns.get(pattern_type)
        
        if not pattern:
            return None
            
        # Find all matching dimensions
        matches = re.finditer(pattern, text)
        best_match = None
        min_distance = float('inf')
        
        for match in matches:
            match_pos = match.start()
            
            # Find nearby text blocks that contain context keywords
            for keyword in context_keywords:
                keyword_pos = text.find(keyword)
                if keyword_pos != -1:
                    distance = abs(match_pos - keyword_pos)
                    if distance < min_distance:
                        min_distance = distance
                        best_match = match
        
        if best_match:
            return float(best_match.group(1))
        return None

    def analyze_dimensions(self, page_num, question):
        """AI-enhanced dimension analysis"""
        try:
            page_data = self.pdf_content.get(page_num)
            if not page_data:
                return None

            question_lower = question.lower()
            
            # Length analysis
            if 'length' in question_lower:
                context = ['length', 'side view', 'total']
                result = self.find_dimension_by_context(page_data, context, 'length')
                return result
            
            # Hole diameter analysis
            elif 'diameter' in question_lower and 'hole' in question_lower:
                context = ['hole', 'diameter', 'φ', 'P']
                result = self.find_dimension_by_context(page_data, context, 'hole_diameter')
                return result
            
            # Width analysis
            elif 'width' in question_lower:
                context = ['width', 'w']
                result = self.find_dimension_by_context(page_data, context, 'length')
                return result
            
            # Center distance analysis
            elif 'distance between center' in question_lower:
                context = ['center', 'plc', 'places']
                result = self.find_dimension_by_context(page_data, context, 'center_distance')
                return result
            
            # Chamfer angle analysis
            elif 'chamfer' in question_lower:
                context = ['chamfer', '°', 'deg']
                result = self.find_dimension_by_context(page_data, context, 'angle')
                return result
            
            # Counterbore analysis
            elif 'counterbore' in question_lower:
                text = page_data['text']
                cb_matches = re.findall(self.dimension_patterns['counterbore'], text)
                if cb_matches:
                    diam, cb_diam, depth = cb_matches[0]
                    return f"P{diam} THRU X P{cb_diam} Z {depth}"
            
            # All diameters analysis
            elif 'all' in question_lower and 'diameter' in question_lower:
                text = page_data['text']
                diameters = re.findall(self.dimension_patterns['hole_diameter'], text)
                if diameters:
                    return ', '.join(f'P{d}' for d in sorted(set(map(float, diameters))))

            return None
            
        except Exception as e:
            logger.error(f"Error in dimension analysis: {str(e)}")
            return None

    def read_questions(self):
        """Read questions from Excel file"""
        try:
            df = pd.read_excel(self.excel_path, header=None)
            current_page = None
            
            for index, row in df.iterrows():
                content = str(row[1])
                
                if pd.isna(content) or content.strip() == '':
                    continue
                    
                if content.startswith('Page-'):
                    current_page = int(content.split('-')[1])
                    self.required_pages.add(current_page)
                    self.questions[current_page] = []
                elif current_page:
                    self.questions[current_page].append({
                        'row': index + 1,
                        'question': content.strip()
                    })
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise

    def update_excel(self):
        """Update Excel file with analysis results"""
        try:
            workbook = openpyxl.load_workbook(self.excel_path)
            sheet = workbook.active
            
            for page_num, questions in self.questions.items():
                for q in questions:
                    result = self.analyze_dimensions(page_num, q['question'])
                    if result is not None:
                        cell = sheet.cell(row=q['row'], column=3)
                        if isinstance(result, str):
                            cell.value = result
                        else:
                            try:
                                cell.value = float(result)
                            except (ValueError, TypeError):
                                cell.value = result
            
            workbook.save(self.excel_path)
            
        except Exception as e:
            logger.error(f"Error updating Excel file: {str(e)}")
            raise

    def process_drawings(self):
        """Main processing function"""
        try:
            logger.info("Starting drawing analysis process")
            
            if not Path(self.pdf_path).exists():
                raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
            if not Path(self.excel_path).exists():
                raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
                
            self.read_questions()
            self.extract_pdf_content()
            self.update_excel()
            
            logger.info("Successfully completed drawing analysis")
            
        except Exception as e:
            logger.error(f"Error in processing: {str(e)}")
            raise

# Usage
if __name__ == "__main__":
    try:
        analyzer = DrawingAnalyzer("Autodesk Part Drawings.pdf", "Drawing Checklist.xlsx")
        analyzer.process_drawings()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
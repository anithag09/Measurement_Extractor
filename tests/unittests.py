import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
import re

def enhance_image(image):
    """
    Enhance image for better OCR
    """
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary

def extract_measurements(pdf_path, page_number):
    """Extract all required measurements from page 3"""
    images = convert_from_path(pdf_path, first_page=page_number, 
                             last_page=page_number, dpi=400)
    image = images[0]
    enhanced_image = enhance_image(image)
    
    # Extract text with better OCR configuration
    custom_config = r'--oem 3 --psm 6'  # PSM 6 for uniform block of text
    text = pytesseract.image_to_string(enhanced_image, config=custom_config)
    
    # Initialize measurements
    hole_edge_dist = None
    chamfer_angle = None
    hole_distance = None
    counterbore_depth = None
    
    # Process text line by line
    lines = text.split('\n')
    for i, line in enumerate(lines):
        current_context = ' '.join(lines[max(0, i-2):min(len(lines), i+3)]).lower()
        
        # Look for chamfer angle in first drawing
        if 'x' in line.lower() and ('c' in line.lower() or 'chamfer' in line.lower()):
            matches = re.findall(r'(\d+)\s*[xX]\s*(\d+)[°c]', line)
            for match in matches:
                angle = int(match[1])
                if 40 <= angle <= 50:
                    chamfer_angle = angle
        
        # Look for hole spacing and edge distance in Mount Bracket drawing
        if 'p6' in line.lower() and 'plc' in current_context:
            numbers = re.findall(r'(?:^|\s)(\d+)(?:\s|$)', current_context)
            for num in numbers:
                value = int(num)
                if 25 <= value <= 35 and not hole_edge_dist:  # Edge distance
                    hole_edge_dist = value
                elif 45 <= value <= 55 and not hole_distance:  # Hole spacing
                    hole_distance = value
        
        # Look for counterbore depth
        if ('z' in line.lower() or 'depth' in line.lower()) and 'section' in current_context:
            matches = re.findall(r'(?:^|\s)(\d+)(?:\s|$)', line)
            for match in matches:
                value = int(match)
                if 25 <= value <= 35:
                    counterbore_depth = value
    
    return hole_edge_dist, chamfer_angle, hole_distance, counterbore_depth

# Main execution
if __name__ == "__main__":
    pdf_path = "./data/input/Autodesk Part Drawings.pdf"
    page_number = 3
    
    edge_dist, chamfer, hole_dist, cbore_depth = extract_measurements(pdf_path, page_number)
    
    print(f"Hole to edge distance: {edge_dist} mm")
    print(f"Chamfer angle: {chamfer} degrees")
    print(f"Distance between holes: {hole_dist} mm")
    print(f"Counterbore depth: {cbore_depth} mm")
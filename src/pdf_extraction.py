import pytesseract
import re
from pdf2image import convert_from_path
from src.image_processing import ImageProcessor
from collections import Counter

class DrawingExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.image_processor = ImageProcessor()

    def preprocess_text(self, text):
        """Clean and standardize text for better extraction"""
        # Replace common OCR mistakes
        text = text.replace('O', '0').replace('o', '0')
        text = text.replace('l', '1').replace('I', '1')
        text = text.replace('S', '5').replace('B', '8')
        # Standardize separators
        text = re.sub(r'[\s,]+', ' ', text)
        return text.strip()

    def extract_page2_dimensions(self):
        """Extract dimensions from page 2"""
        images = convert_from_path(self.pdf_path, first_page=2, last_page=2, dpi=400)
        image = images[0]
        enhanced_image = self.image_processor.enhance_image(image)
        
        # Extract text with OCR
        custom_config = r'--oem 3 --psm 11'
        text = pytesseract.image_to_string(enhanced_image, config=custom_config)
        
        # Find numbers and context
        numbers = []
        lines = text.split('\n')
        for line in lines:
            # Look for numbers with R or P prefix
            radius_matches = re.finditer(r'[RP]\s*(\d+(?:\.\d+)?)', line, re.IGNORECASE)
            for match in radius_matches:
                try:
                    value = float(match.group(1))
                    numbers.append(('hole', value))
                except ValueError:
                    continue
            
            # Look for standalone numbers
            standalone_matches = re.finditer(r'\b(\d+(?:\.\d+)?)\b', line)
            for match in standalone_matches:
                try:
                    value = float(match.group(1))
                    numbers.append(('dim', value))
                except ValueError:
                    continue
        
        # Filter dimensions
        hole_dims = [value for type_, value in numbers if type_ == 'hole' and 2 <= value <= 50]
        side_dims = [value for type_, value in numbers if type_ == 'dim' and 10 <= value <= 1000]
        
        return {
            'total_length': max(side_dims) if side_dims else None,
            'hole_diameter': max(hole_dims) if hole_dims else None,
            'width': self.extract_width()
        }
    
    def extract_width(self):
        """Extract width dimension from page 2"""
        images = convert_from_path(self.pdf_path, first_page=2, last_page=2, dpi=400)
        image = images[0]
        enhanced_image = self.image_processor.enhance_image(image)
        
        custom_config = r'--oem 3 --psm 11'
        text_data = pytesseract.image_to_data(enhanced_image, config=custom_config, 
                                            output_type=pytesseract.Output.DICT)
        
        dimensions = []
        for i, text in enumerate(text_data['text']):
            if text.strip():
                dimensions.append({
                    'text': text,
                    'x': text_data['left'][i],
                    'y': text_data['top'][i]
                })
        
        horizontal_dims = []
        for dim in dimensions:
            match = re.match(r'^(\d+(?:\.\d+)?)$', dim['text'])
            if match:
                value = float(match.group(1))
                context = ' '.join(d['text'].lower() for d in dimensions 
                                 if abs(d['y'] - dim['y']) < 20
                                 and abs(d['x'] - dim['x']) < 100)
                
                if any(word in context for word in ['width', 'w', 'horizontal']) or 5 <= value <= 500:
                    horizontal_dims.append(value)
        
        if horizontal_dims:
            filtered_dims = [d for d in horizontal_dims if d >= 5]
            filtered_dims.sort()
            return filtered_dims[0] if filtered_dims else None
        return None

    def extract_hole_edge_distance(self, page_number):
        """
        Extract the distance between hole center and edge
        """
        # Convert PDF to image
        images = convert_from_path(self.pdf_path, first_page=page_number, 
                                last_page=page_number, dpi=400)
        image = images[0]
        
        # Extract text with OCR
        custom_config = r'--oem 3 --psm 11'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        # Find all numbers in the text with their context
        distances = []
        for line in text.split('\n'):
            # Check for hole and dimension related context
            if any(x in line for x in ['P', 'PLCS', 'THRU']):
                # Extract numbers that appear after hole specifications
                matches = re.finditer(r'P\d+.*?(\d+)', line)
                for match in matches:
                    try:
                        value = int(match.group(1))
                        # Filter for reasonable hole-to-edge distances
                        if 20 <= value <= 50:  # General range for edge distances
                            distances.append(value)
                    except ValueError:
                        continue
                        
                # Also look for standalone dimensions on same line
                numbers = re.findall(r'\b(\d+)\b', line)
                for num in numbers:
                    try:
                        value = int(num)
                        if 20 <= value <= 50:
                            distances.append(value)
                    except ValueError:
                        continue
        
        # Return the most common distance in the expected range
        if distances:
            return Counter(distances).most_common(1)[0][0]
            
        return None


    def extract_page3_measurements(self):
        """Extract measurements from page 3 with improved accuracy"""
        images = convert_from_path(self.pdf_path, first_page=3, last_page=3, dpi=400)
        image = images[0]
        enhanced_image = self.image_processor.enhance_image(image)
        
        # Try multiple PSM modes for better accuracy
        text_results = []
        for psm in [6, 11, 3]:
            custom_config = f'--oem 3 --psm {psm}'
            text = pytesseract.image_to_string(enhanced_image, config=custom_config)
            text_results.append(self.preprocess_text(text))
        
        # Combine results
        combined_text = '\n'.join(text_results)
        
        results = {
            'hole_edge_distance': None,
            'chamfer_angle': None,
            'hole_distance': None,
            'counterbore_depth': None
        }
        
        # Extract hole edge distance
        edge_distances = []
        for line in combined_text.split('\n'):
            if any(x in line.upper() for x in ['P6', 'PLCS', 'EDGE']):
                matches = re.finditer(r'(?:P6|P\s*6).*?(\d{2,3})', line)
                for match in matches:
                    value = int(match.group(1))
                    if 25 <= value <= 35:
                        edge_distances.append(value)
        if edge_distances:
            results['hole_edge_distance'] = Counter(edge_distances).most_common(1)[0][0]
        
        # Extract chamfer angle
        angles = []
        for line in combined_text.split('\n'):
            if any(x in line.lower() for x in ['chamfer', '45°', '45x']):
                matches = re.findall(r'(\d+)\s*(?:°|deg|x)', line)
                for match in matches:
                    angle = int(match)
                    if 40 <= angle <= 50:
                        angles.append(angle)
        if angles:
            results['chamfer_angle'] = Counter(angles).most_common(1)[0][0]
        
        # Extract hole distance
        distances = []
        for line in combined_text.split('\n'):
            if 'P6' in line.upper() and any(x in line.upper() for x in ['PCD', 'PITCH', 'CIRCLE']):
                numbers = re.findall(r'(?<!\d)(\d{2})(?!\d)', line)
                for num in numbers:
                    value = int(num)
                    if 45 <= value <= 55:
                        distances.append(value)
        if distances:
            results['hole_distance'] = Counter(distances).most_common(1)[0][0]
        
        # Extract counterbore depth
        depths = []
        for line in combined_text.split('\n'):
            if any(x in line.lower() for x in ['depth', 'z', 'deep']):
                matches = re.findall(r'(?<!\d)(\d{2})(?!\d)', line)
                for match in matches:
                    value = int(match)
                    if 25 <= value <= 35:
                        depths.append(value)
        if depths:
            results['counterbore_depth'] = Counter(depths).most_common(1)[0][0]
        
        return results

    def extract_page5_measurements(self):
        """Extract measurements from page 5 with improved accuracy"""
        images = convert_from_path(self.pdf_path, first_page=5, last_page=5, dpi=400)
        image = images[0]
        enhanced_image = self.image_processor.enhance_image(image, for_symbols=True)
        
        results = {
            'disc_thickness': None,
            'circle_diameter': None,
            'all_diameters': self.extract_all_diameters(enhanced_image)  # Using improved method
        }
        
        # Extract disc thickness
        thicknesses = []
        text = pytesseract.image_to_string(enhanced_image, config='--oem 3 --psm 11')
        for line in text.split('\n'):
            if any(x in line.lower() for x in ['thick', 'sheet', 't=']):
                matches = re.findall(r'(?<!\d)(\d+(?:\.\d+)?)(?!\d)', line)
                for match in matches:
                    try:
                        value = float(match)
                        if 2 <= value <= 25:
                            thicknesses.append(value)
                    except ValueError:
                        continue
        if thicknesses:
            results['disc_thickness'] = min(thicknesses)
        
        # Extract circle diameter (PCD)
        diameters = []
        for line in text.split('\n'):
            if any(x in line.upper() for x in ['PCD', 'PITCH', 'CIRCLE', 'Ø']):
                matches = re.findall(r'(?<!\d)(\d+)(?!\d)', line)
                for match in matches:
                    try:
                        value = int(match)
                        if 60 <= value <= 120:
                            diameters.append(value)
                    except ValueError:
                        continue
        if diameters:
            results['circle_diameter'] = Counter(diameters).most_common(1)[0][0]
        
        return results

    def extract_disc_thickness(self, enhanced_image):
        """Extract disc thickness from page 5"""
        custom_config = r'--oem 3 --psm 11'
        text = pytesseract.image_to_string(enhanced_image, config=custom_config)
        
        thickness_values = []
        lines = text.split('\n')
        for line in lines:
            if any(x in line.upper() for x in ['SHEET', 'PLCS', 'SCALE']):
                continue
            
            matches = re.finditer(r'\b(\d+(?:\.\d+)?)\b', line)
            for match in matches:
                try:
                    value = float(match.group(1))
                    if 2 <= value <= 25:
                        thickness_values.append(value)
                except ValueError:
                    continue
        
        return min(thickness_values) if thickness_values else None
    
    def extract_circle_diameter(self, enhanced_image):
        """Extract circle diameter from page 5"""
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(enhanced_image, config=custom_config)
        
        patterns = [
            r'(?:pcd|pitch circle)\s*(?:dia|\u2300)?\s*(\d+)',
            r'(?:\u2300|\u00D8|dia\.?|diameter)\s*(\d+)',
            r'(?:bolt circle|hole circle)\s*(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.group(1))
                    if 60 <= value <= 120:
                        return value
                except ValueError:
                    continue
        return None
    
    def extract_all_diameters(self, enhanced_image):
        """
        Extract all valid diameters with improved context validation
        Returns: List of diameter dictionaries with value, symbol, and context
        """
        # Try multiple PSM modes for better accuracy
        combined_text = ''
        for psm in [6, 11, 3]:
            custom_config = f'--oem 3 --psm {psm}'
            text = pytesseract.image_to_string(enhanced_image, config=custom_config)
            combined_text += '\n' + self.preprocess_text(text)

        all_diameters = []
        invalid_contexts = ['MILLIMETER', 'SCALE', 'SHEET', 'TITLE', 'DATE', 'DWG', '.ipt']
        
        # Pattern for finding diameters with context
        diameter_patterns = [
            (r'[⌀Øø]\s*(\d+(?:\.\d+)?)', '⌀'),  # Standard diameter symbol
            (r'(?:DIA|\bD\b)[. ]*(\d+(?:\.\d+)?)', '⌀'),  # DIA or D prefix
            (r'(?:PCD|PITCH CIRCLE)[. ]*(\d+(?:\.\d+)?)', 'PCD'),  # PCD specific
            (r'\bM(\d+(?:\.\d+)?)\b', 'M'),  # Metric thread
            (r'(?<![\w.])\d+(?:\.\d+)?(?:\s*)[xX](\d+(?:\.\d+)?)', '⌀')  # Dimensions with x
        ]
        
        # Process each line individually for better context control
        for line in combined_text.split('\n'):
            line = line.strip()
            
            # Skip lines with invalid contexts
            if any(invalid in line.upper() for invalid in invalid_contexts):
                continue
                
            # Skip lines that appear to be notes or file names
            if '.ipt' in line.lower() or len(re.findall(r'\d+', line)) > 5:
                continue
            
            # Check each pattern
            for pattern, symbol in diameter_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        # Filter for reasonable diameter ranges and contexts
                        if 2 <= value <= 500:  # Reasonable diameter range
                            # Get surrounding context (up to 10 chars before and after)
                            match_start = max(0, match.start() - 10)
                            match_end = min(len(line), match.end() + 10)
                            context = line[match_start:match_end].strip()
                            
                            # Additional validation
                            if len(context.split()) <= 6:  # Avoid long text segments
                                all_diameters.append({
                                    'value': value,
                                    'symbol': symbol,
                                    'context': context
                                })
                    except (ValueError, IndexError):
                        continue
        
        # Remove duplicates while preserving context
        seen_values = set()
        unique_diameters = []
        for d in all_diameters:
            if d['value'] not in seen_values:
                seen_values.add(d['value'])
                unique_diameters.append(d)
        
        # Sort by value
        return sorted(unique_diameters, key=lambda x: x['value'])
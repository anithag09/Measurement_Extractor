from src.pdf_extraction import DrawingExtractor
from src.excel_handler import ExcelHandler
import json
from pathlib import Path

def load_config(config_path="config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {config_path}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in config file")

def validate_paths(config):
    """Validate that the required paths exist"""
    required_paths = ['pdf_path', 'excel_path']
    
    for path_key in required_paths:
        if path_key not in config:
            raise KeyError(f"Missing required path: {path_key}")
        
        file_path = Path(config[path_key])
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
    return config['pdf_path'], config['excel_path']

def process_drawings(pdf_path, excel_path):
    """Main function to process drawings and update Excel"""
    # Initialize handlers
    extractor = DrawingExtractor(pdf_path)
    excel_handler = ExcelHandler(excel_path)
    
    try:
        # Read questions from Excel
        questions = excel_handler.read_questions()
        
        # Initialize results dictionary
        results = {2: [], 3: [], 5: []}
        
        # Process Page 2
        if 2 in questions:
            page2_data = extractor.extract_page2_dimensions()
            results[2] = [
                {'value': page2_data['total_length']},
                {'value': page2_data['hole_diameter']},
                {'value': page2_data['width']}
            ]
        
        # Process Page 3
        if 3 in questions:
            page3_data = extractor.extract_page3_measurements()
            results[3] = [
                {'value': page3_data['hole_edge_distance']},
                {'value': page3_data['chamfer_angle']},
                {'value': page3_data['hole_distance']},
                {'value': page3_data['counterbore_depth']}
            ]
        
        # Process Page 5
        if 5 in questions:
            page5_data = extractor.extract_page5_measurements()
            results[5] = [
                {'value': page5_data['disc_thickness']},
                {'value': page5_data['circle_diameter']},
                {'value': page5_data['all_diameters']}
            ]
        
        # Update Excel with results
        for page_num, page_results in results.items():
            if page_results:  # Only update if we have results for this page
                excel_handler.update_answers(page_num, page_results)
    
    finally:
        # Ensure workbook is properly closed
        excel_handler.close()

def main():
    try:
        # Load configuration
        config = load_config()
        
        # Validate and get paths
        pdf_path, excel_path = validate_paths(config)
        
        # Process drawings
        process_drawings(pdf_path, excel_path)
        print("Processing completed successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
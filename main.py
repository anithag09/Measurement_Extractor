import os
import json
from src.drawing_analyzer import DrawingAnalyzer
from src.excel_handler import read_questions, write_answer
from src.pdf_extraction import extract_drawing

def load_config():
    """Load paths and settings from the config file."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def main():
    # Load configuration
    config = load_config()
    pdf_path = config['pdf_path']
    excel_path = config['excel_path']

    # Initialize analyzer
    analyzer = DrawingAnalyzer()

    # Read questions from Excel
    questions = read_questions(excel_path)

    # Process each question
    for q in questions:
        try:
            # Extract page number from question (assuming format "Page-X: question")
            page_parts = q['question'].split(':')[0].split('-')
            if len(page_parts) > 1:
                page_number = int(page_parts[1])

                # Extract drawing
                drawing = extract_drawing(pdf_path, page_number)
                if drawing is not None:
                    # Analyze drawing and get answer
                    answer = analyzer.analyze_drawing(drawing, q['question'])

                    # Write answer to Excel
                    write_answer(excel_path, q['row'], answer)
                    print(f"Processed question for page {page_number}")

        except Exception as e:
            print(f"Error processing question {q['question']}: {e}")
            continue

if __name__ == "__main__":
    main()

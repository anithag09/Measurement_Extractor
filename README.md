# Project: PDF Drawing Analyzer

This project automates the process of extracting and analyzing technical drawing data from PDFs, answering specific questions defined in an Excel file, and writing the results back to the same Excel file. It is designed to work dynamically with varying PDF and Excel formats without hardcoding.

## Requirements

### Software Requirements
- Python 3.8 or higher
- Operating System: Windows/Linux/MacOS
- Tesseract OCR installed (for image text extraction)

### Python Libraries
Install the following libraries before running the project:
```bash
pip install pytesseract pandas PyPDF2 pdf2image pillow
```

### External Tools
- **Tesseract OCR**: Required for extracting text from images.
  - Download and install Tesseract from [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract).
  - Add Tesseract to your system PATH.

### Files Needed
1. **PDF File**: The file containing technical drawings (e.g., `Autodesk Part Drawings.pdf`).
2. **Excel File**: An Excel file with questions in column B and placeholders for answers in column C (e.g., `Drawing Checklist.xlsx`).

### Directory Structure
```
project/
|
├── config.json
├── main.py
├── data/
│   ├── input/
│   │   ├── Autodesk Part Drawings.pdf
│   └── Drawing Checklist.xlsx
├── src/
    ├── drawing_analyzer.py
    ├── excel_handler.py
    └── pdf_extraction.py
```

## How It Works

1. **Config File**:
   - `config.json` stores the paths for the input PDF and Excel file.
   - Example:
     ```json
     {
         "pdf_path": "./data/input/Autodesk Part Drawings.pdf",
         "excel_path": "./data/Drawing Checklist.xlsx"
     }
     ```

2. **Main Script**:
   - The `main.py` script reads the config file, processes the PDF and Excel file, and writes answers to the Excel file.

3. **Excel Handler**:
   - Reads questions from column B of the Excel file.
   - Writes answers to column C of the Excel file.

4. **PDF Extraction**:
   - Extracts specific pages from the PDF based on the question requirements.
   - Converts the PDF page to an image for analysis.

5. **Drawing Analyzer**:
   - Uses OCR to extract text from the image.
   - Identifies and extracts relevant data (e.g., diameters, lengths) based on the question.

## Installation Guide

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd project/
   ```

2. Install dependencies:
   ```bash
   pip install pytesseract pandas PyPDF2 pdf2image pillow
   ```

3. Install and configure Tesseract OCR:
   - Download Tesseract from [here](https://github.com/tesseract-ocr/tesseract).
   - Add the Tesseract executable path in the `src/drawing_analyzer.py` file:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
     ```

4. Place your input files in the `data/input` directory:
   - `Autodesk Part Drawings.pdf`
   - `Drawing Checklist.xlsx`

5. Update the file paths in `config.json` if necessary.

## Usage

1. Run the main script:
   ```bash
   python main.py
   ```

2. The script will:
   - Read questions from the Excel file.
   - Extract relevant pages from the PDF.
   - Perform OCR on the pages to analyze the drawings.
   - Write the answers back to column C of the Excel file.

3. Output:
   - Updated Excel file with answers in column C.

## Code Overview

### 1. `main.py`
- Entry point of the application.
- Coordinates the entire workflow: reading questions, extracting pages, analyzing drawings, and writing answers.

### 2. `config.json`
- Stores the paths to the input PDF and Excel files.

### 3. `src/excel_handler.py`
- Handles reading and writing data to the Excel file.

### 4. `src/pdf_extraction.py`
- Extracts specific pages from the PDF and converts them into images for analysis.

### 5. `src/drawing_analyzer.py`
- Uses OCR to extract text from images.
- Contains logic to analyze the extracted text and retrieve relevant information.

## Example

### Input
- **PDF File**: Contains technical drawings.
- **Excel File**:
  | B (Questions)                              | C (Answers)       |
  |-------------------------------------------|-------------------|
  | Page-2: Capture the diameter of the hole. |                   |

### Output
- **Updated Excel File**:
  | B (Questions)                              | C (Answers)       |
  |-------------------------------------------|-------------------|
  | Page-2: Capture the diameter of the hole. | 15                |

## Error Handling

- Invalid paths: Check if files exist before processing.
- OCR errors: Log errors if OCR fails to extract text.
- Excel write errors: Validate data before writing.

## Future Improvements

1. Add support for multiple languages in OCR.
2. Improve question parsing with NLP models.
3. Enhance drawing analysis using advanced computer vision techniques (e.g., OpenCV).
4. Automate unit testing for PDF and Excel handlers.



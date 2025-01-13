# Engineering Drawing Measurement Extraction

A Python-based automated system for extracting measurements and specifications from engineering drawings in PDF format. The system uses OCR technology to identify and extract various measurements and automatically updates them in an Excel checklist. It is designed to work dynamically with varying PDF and Excel formats without hardcoding.

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Configuration](#configuration)
- [Features](#features)
- [Technical Details](#technical-details)
- [Error Handling](#error-handling)
- [Scalability](#scalability)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)

## Overview
This project automates the extraction of measurements from engineering drawings by:
- Converting PDF pages to high-resolution images
- Using OCR to extract text and measurements
- Processing and validating the extracted data
- Updating an Excel checklist with the results
- Providing visual feedback through color-coding

## Requirements

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- Tesseract OCR engine installed
- Poppler installed (for PDF processing)

### Python Dependencies
```plaintext
pytesseract>=0.3.8
pdf2image>=1.16.0
opencv-python>=4.5.3
numpy>=1.21.0
pandas>=1.3.0
openpyxl>=3.0.7
```

## Installation

1. Install system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install tesseract-ocr poppler-utils
   
   # macOS
   brew install tesseract poppler
   
   # Windows
   # Download and install Tesseract from GitHub
   # Download and install poppler from conda-forge
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/engineering-drawing-extraction.git
   cd engineering-drawing-extraction
   ```

3. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure
```
engineering-drawing-extraction/
├── src/
│   ├── __init__.py
│   ├── excel_handler.py
│   ├── image_processing.py
│   └── pdf_extraction.py
├── tests/
│   ├── __init__.py
│   ├── unittests.py
├── config.json
├── main.py
├── requirements.txt
└── README.md
```

## Usage

1. Configure the input/output paths in `config.json`:
   ```json
   {
       "pdf_path": "path/to/your/drawing.pdf",
       "excel_path": "path/to/your/checklist.xlsx"
   }
   ```

2. Prepare your Excel checklist with the required format:
   - Column B: Questions/specifications grouped by page
   - Column C: Will be populated with extracted values

3. Run the extraction:
   ```bash
   python main.py
   ```

4. Check the results in your Excel file:
   - Green cells: Successfully extracted values
   - Pink cells: Failed extractions

## Features

### Current Features
- PDF to image conversion with optimized DPI
- Advanced image preprocessing for better OCR
- Multiple OCR passes with different configurations
- Intelligent context-based measurement extraction
- Support for various measurement types:
  - Linear dimensions
  - Diameters
  - Angles
  - Depths
  - Edge distances
- Excel integration with visual feedback
- Robust error handling and logging

### Supported Measurements
- Total length from side view
- Hole diameters
- Part width
- Hole-to-edge distances
- Chamfer angles
- Hole-to-hole distances
- Counterbore depths
- Disc thickness
- Circle diameters (PCD)

## Technical Details

### Image Processing
- Adaptive contrast enhancement
- Noise reduction
- Binary thresholding
- Morphological operations

### OCR Strategy
- Multiple PSM modes for different text layouts
- Context-aware pattern matching
- Validation through multiple passes
- Symbol and dimension recognition

### Data Validation
- Range-based filtering
- Context verification
- Duplicate detection
- Statistical validation (most common values)

## Error Handling
- Comprehensive exception handling
- Detailed error logging
- Graceful fallbacks
- Visual feedback in Excel

## Scalability

### Current Capabilities
- Processes single PDF files
- Handles multiple pages within a PDF
- Supports standard engineering drawing formats

### Scalability Options
1. Batch Processing
   - Process multiple PDFs in sequence
   - Parallel processing of different drawings
   - Distributed processing across machines

2. Storage Optimization
   - Temporary file cleanup
   - Image compression
   - Memory management for large files

3. Performance Enhancement
   - Caching of intermediate results
   - Multi-threading for image processing
   - GPU acceleration for OCR

## Limitations
- Requires consistent drawing formatting
- OCR accuracy depends on image quality
- Limited support for handwritten text
- May struggle with complex overlapping dimensions
- Processing time increases with image resolution

## Future Enhancements

### Short-term Improvements
1. Support for additional measurement types
2. Enhanced symbol recognition
3. Improved error reporting
4. Configuration UI
5. Progress tracking

### Medium-term Goals
1. Machine learning for pattern recognition
2. Support for multiple drawing standards
3. PDF annotation capability
4. Batch processing interface
5. Result verification tools

### Long-term Vision
1. AI-powered drawing understanding
2. 3D model generation from 2D drawings
3. CAD software integration
4. Cloud-based processing
5. Mobile app for scanning and processing

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

### Contribution Guidelines
- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Maintain backwards compatibility



![alt text](<Screenshot 2025-01-13 at 10.01.23 PM.png>)

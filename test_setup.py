"""
Simple test script for the Chrono AI Assignment Grader
This creates a sample homework assignment for testing purposes.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_homework():
    """Create a sample homework assignment image for testing."""
    
    # Create a white image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Add homework content
    y_position = 50
    
    # Title
    draw.text((50, y_position), "Math Homework Assignment", fill='black', font=font)
    y_position += 80
    
    # Question 1
    draw.text((50, y_position), "Q1: What is 15 + 23?", fill='black', font=font)
    y_position += 40
    draw.text((70, y_position), "Answer: 38", fill='blue', font=small_font)
    y_position += 60
    
    # Question 2
    draw.text((50, y_position), "Q2: Solve for x: 2x + 5 = 13", fill='black', font=font)
    y_position += 40
    draw.text((70, y_position), "Answer: x = 4", fill='blue', font=small_font)
    y_position += 60
    
    # Question 3
    draw.text((50, y_position), "Q3: What is the area of a circle with radius 5?", fill='black', font=font)
    y_position += 40
    draw.text((70, y_position), "Answer: A = π × 5² = 25π ≈ 78.54", fill='blue', font=small_font)
    y_position += 60
    
    # Question 4 (with wrong answer for testing)
    draw.text((50, y_position), "Q4: What is 7 × 8?", fill='black', font=font)
    y_position += 40
    draw.text((70, y_position), "Answer: 54", fill='blue', font=small_font)  # Wrong answer (should be 56)
    
    # Save the image
    img.save('sample_homework.png')
    print("✅ Sample homework image created: sample_homework.png")

def create_setup_guide():
    """Create a setup guide file."""
    guide = """
# Chrono AI Assignment Grader - Setup Guide

## Prerequisites
1. Python 3.7 or higher installed
2. Tesseract OCR installed on your system
3. OpenAI API key

## Installation Steps

### 1. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH, or update config.env with the installation path

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup OpenAI API Key
1. Get your API key from https://platform.openai.com/api-keys
2. Copy `config.env` to `.env`
3. Replace `your-openai-api-key-here` with your actual API key

### 4. Test the Installation
```bash
python chrono_grader.py --test
```

## Usage Examples

### Grade a homework image:
```bash
python chrono_grader.py homework_image.jpg
```

### Grade with custom output file:
```bash
python chrono_grader.py homework_image.jpg -o my_results.txt
```

### Test with sample image:
```bash
python test_setup.py  # Creates sample_homework.png
python chrono_grader.py sample_homework.png
```

## Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- PDF (single page)

## Troubleshooting

### "tesseract not found" error:
- Make sure Tesseract is installed and in PATH
- On Windows, update the TESSERACT_CMD in config.env

### "OpenAI API error":
- Check your API key in .env file
- Ensure you have sufficient credits in your OpenAI account
- Check your internet connection

### Poor OCR results:
- Ensure image is clear and high resolution
- Try preprocessing the image (contrast, brightness)
- Check that text is properly oriented (not rotated)

## Features
- ✅ OCR text extraction from images
- ✅ AI-powered question parsing
- ✅ Automatic grading with GPT
- ✅ Detailed feedback generation
- ✅ Formatted result reports
- ✅ Support for math, science, and language assignments

For support, visit: https://github.com/your-repo/chrono-grader
"""
    
    with open('SETUP_GUIDE.md', 'w') as f:
        f.write(guide)
    
    print("✅ Setup guide created: SETUP_GUIDE.md")

if __name__ == "__main__":
    print("🔧 Setting up Chrono AI Assignment Grader test environment...")
    create_sample_homework()
    create_setup_guide()
    print("🎉 Test environment setup complete!")
    print("\nNext steps:")
    print("1. Add your OpenAI API key to config.env")
    print("2. Run: python chrono_grader.py sample_homework.png")

# Chrono AI Assignment Grader

🚀 **AI-Powered Assignment Grading Platform** - A standalone Python MVP that automatically grades student homework assignments from images using OCR and OpenAI's GPT models.

## 🌟 Features

- **📸 Image Processing**: Extract text from homework images using advanced OCR
- **🤖 AI-Powered Parsing**: Intelligently separate questions from answers
- **🎯 Automatic Grading**: Grade assignments using GPT-4/GPT-3.5 with detailed feedback
- **📊 Comprehensive Reports**: Generate formatted grading reports with explanations
- **🔧 Easy Setup**: Simple configuration and command-line interface

## 📦 Project Structure

```
chronofrontend/
├── chrono_grader.py      # Main grading application
├── test_setup.py         # Test environment setup
├── requirements.txt      # Python dependencies
├── config.env           # Configuration template
├── landingpage.html     # Web interface (dark theme)
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR
- **Windows**: Download from [Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### 3. Setup OpenAI API Key
1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Copy `config.env` to `.env`
3. Add your API key: `OPENAI_API_KEY=your-actual-key-here`

### 4. Test the Setup
```bash
python test_setup.py          # Creates sample homework image
python chrono_grader.py sample_homework.png
```

## 💻 Usage

### Grade a homework assignment:
```bash
python chrono_grader.py homework_image.jpg
```

### Custom output file:
```bash
python chrono_grader.py homework_image.jpg -o results.txt
```

### Test mode:
```bash
python chrono_grader.py --test
```

## 📋 Example Output

```
============================================================
CHRONO AI ASSIGNMENT GRADING RESULTS
============================================================
Generated: 2025-07-22 14:30:15
Total Questions: 4
Overall Score: 3.0/4 (75.0%)
============================================================

Q1: What is 15 + 23?
Student Answer: 38
Status: Correct
Points: 1.0/1.0
----------------------------------------

Q2: Solve for x: 2x + 5 = 13
Student Answer: x = 4
Status: Correct
Points: 1.0/1.0
----------------------------------------

Q3: What is the area of a circle with radius 5?
Student Answer: A = π × 5² = 25π ≈ 78.54
Status: Correct
Points: 1.0/1.0
----------------------------------------

Q4: What is 7 × 8?
Student Answer: 54
Status: Incorrect
Correct Answer: 56
Explanation: 7 × 8 = 56, not 54. This is a basic multiplication error.
Feedback: Review your multiplication tables for single-digit numbers.
Points: 0.0/1.0
----------------------------------------
```

## 🛠️ Architecture

The system consists of four main components:

1. **`extract_text(image_path)`** - OCR text extraction using Tesseract
2. **`parse_questions(text)`** - AI-powered question/answer parsing
3. **`grade_questions(questions)`** - GPT-based grading with feedback
4. **`write_results(results)`** - Formatted report generation

## 🎨 Web Interface

The project includes a modern dark-themed landing page (`landingpage.html`) showcasing the Chrono platform with:

- ✨ Gradient hero section with animated statistics
- 🌙 Professional dark theme design  
- 📱 Mobile-responsive layout
- 🎯 Interactive elements and hover effects
- 📊 Feature highlights and testimonials

## 🔧 Configuration

Edit `config.env` to customize:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Tesseract Configuration (Windows)
# TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# OCR Settings
OCR_LANGUAGE=eng
OCR_PSM=6
OCR_OEM=3
```

## 📸 Supported Formats

- **Images**: JPEG, PNG
- **Documents**: PDF (single page)
- **Content**: Math, Science, Language assignments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and support:
1. Check the troubleshooting guide in `SETUP_GUIDE.md`
2. Open an issue on GitHub
3. Contact the development team

## 🎯 Roadmap

- [ ] Multi-page PDF support
- [ ] Batch processing capabilities
- [ ] Custom rubric templates
- [ ] Integration with LMS platforms
- [ ] Advanced image preprocessing
- [ ] Multi-language support

---

**Built with ❤️ by the Chrono Team** | **Powered by OpenAI GPT & Tesseract OCR**
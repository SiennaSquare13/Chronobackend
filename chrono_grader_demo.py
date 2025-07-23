"""
Chrono AI Assignment Grader - DEMO VERSION (No API Required)
This version demonstrates the full pipeline without requiring OpenAI API calls.
"""

import pytesseract
from PIL import Image
import json
import re
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Configure Tesseract path
tesseract_path = os.getenv('TESSERACT_CMD')
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def extract_text(image_path: str) -> str:
    """Extract text from image using OCR (same as original)"""
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        print(f"📸 Processing image: {image_path}")
        
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            custom_oem_psm_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,?!:;()[]{}+=*/-_ '
            
            extracted_text = pytesseract.image_to_string(
                img, 
                config=custom_oem_psm_config,
                lang='eng'
            )
            
            cleaned_text = clean_extracted_text(extracted_text)
            
            print(f"✅ Text extraction completed. Characters extracted: {len(cleaned_text)}")
            print(f"📄 Full text: {cleaned_text}")
            
            return cleaned_text
            
    except Exception as e:
        print(f"❌ OCR processing failed: {str(e)}")
        raise Exception(f"Failed to extract text from image: {str(e)}")

def clean_extracted_text(raw_text: str) -> str:
    """Clean OCR text (same as original)"""
    cleaned = re.sub(r'\n\s*\n', '\n\n', raw_text)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = cleaned.strip()
    return cleaned

def parse_questions(text: str) -> List[Dict[str, str]]:
    """Parse questions from text (same as original)"""
    print("📝 Parsing questions and answers from text...")
    
    question_patterns = [
        r'(?:Q|Question|Prob|Problem)\s*(\d+)[\.:)]?\s*(.+?)(?=(?:Q|Question|Prob|Problem)\s*\d+|$)',
        r'(\d+)[\.:)]\s*(.+?)(?=\d+[\.:)]|$)',
        r'(\d+)\.\s*(.+?)(?=\d+\.|$)'
    ]
    
    questions = []
    
    for pattern in question_patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f"✅ Found {len(matches)} questions using pattern")
            
            for match in matches:
                question_num = match[0].strip()
                content = match[1].strip()
                
                parsed_qa = separate_question_answer(content)
                
                questions.append({
                    'question_number': question_num,
                    'question_text': parsed_qa['question'],
                    'student_answer': parsed_qa['answer'],
                    'raw_content': content
                })
            break
    
    print(f"📊 Total questions parsed: {len(questions)}")
    return questions

def separate_question_answer(content: str) -> Dict[str, str]:
    """Separate questions and answers (same as original)"""
    answer_indicators = [
        r'Answer:?\s*(.+?)(?=\n|$)',
        r'Ans:?\s*(.+?)(?=\n|$)',
        r'Solution:?\s*(.+?)(?=\n|$)',
        r'=\s*(.+?)(?=\n|$)',
        r'\?\s*(.+?)(?=\n|$)'
    ]
    
    question_text = content
    student_answer = ""
    
    for indicator in answer_indicators:
        match = re.search(indicator, content, re.IGNORECASE)
        if match:
            student_answer = match.group(1).strip()
            question_text = content[:match.start()].strip()
            break
    
    if not student_answer:
        lines = content.split('\n')
        if len(lines) > 1:
            question_text = lines[0].strip()
            student_answer = ' '.join(lines[1:]).strip()
    
    return {
        'question': question_text,
        'answer': student_answer if student_answer else content
    }

def demo_grade_questions(questions: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    DEMO VERSION: Grade questions using simple logic instead of AI
    This demonstrates the complete pipeline without API costs
    """
    print("🔍 Starting to grade questions using DEMO logic...")
    print("ℹ️  Note: This is a demo version. Real AI grading requires OpenAI API.")
    
    graded_results = []
    
    # Demo grading logic for common math problems
    demo_answers = {
        "15+23": "38",
        "15 + 23": "38",
        "what is 15 + 23": "38",
        "2x+5=13": "x=4",
        "2x + 5 = 13": "x = 4",
        "solve for x: 2x + 5 = 13": "x = 4",
        "7x8": "56",
        "7 x 8": "56", 
        "7*8": "56",
        "7 * 8": "56",
        "what is 7 x 8": "56",
        "what is 7 × 8": "56"
    }
    
    for i, question in enumerate(questions, 1):
        print(f"📚 Grading Question {question['question_number']} ({i}/{len(questions)})")
        
        # Simple demo grading logic
        q_text = question['question_text'].lower().strip()
        student_ans = question['student_answer'].lower().strip()
        
        # Check if it's a math question we can demo-grade
        correct_answer = None
        for pattern, answer in demo_answers.items():
            if pattern.lower() in q_text:
                correct_answer = answer
                break
        
        if correct_answer:
            # Check if student answer matches
            if correct_answer.lower() in student_ans or student_ans == correct_answer.lower():
                # Correct answer
                result = {
                    **question,
                    'status': 'Correct',
                    'correct_answer': correct_answer,
                    'explanation': 'Correct calculation and answer.',
                    'score': 1.0,
                    'feedback': 'Well done! Your answer is correct.',
                    'graded_at': f"Question {question['question_number']}"
                }
                print(f"   ✅ Status: Correct (Score: 1.0)")
            else:
                # Incorrect answer
                result = {
                    **question,
                    'status': 'Incorrect',
                    'correct_answer': correct_answer,
                    'explanation': f'The correct answer is {correct_answer}. Your answer was {question["student_answer"]}.',
                    'score': 0.0,
                    'feedback': 'Review your calculation. Check each step carefully.',
                    'graded_at': f"Question {question['question_number']}"
                }
                print(f"   ❌ Status: Incorrect (Score: 0.0)")
        else:
            # Unknown question type - assign partial credit
            result = {
                **question,
                'status': 'Demo Mode - Manual Review Needed',
                'correct_answer': 'Unable to determine in demo mode',
                'explanation': 'This question type requires AI grading for accurate assessment.',
                'score': 0.5,
                'feedback': 'Demo version: Please use full AI grading for complex questions.',
                'graded_at': f"Question {question['question_number']}"
            }
            print(f"   ⚠️  Status: Demo Mode (Score: 0.5)")
        
        graded_results.append(result)
    
    # Calculate totals
    total_score = sum(q['score'] for q in graded_results)
    max_score = len(graded_results)
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    print(f"📊 Demo grading completed!")
    print(f"   Total Score: {total_score:.1f}/{max_score} ({percentage:.1f}%)")
    
    return graded_results

def write_results(results: List[Dict[str, str]], output_path: Optional[str] = None) -> str:
    """Write results to file (same as original)"""
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"chrono_demo_results_{timestamp}.txt"
    
    print(f"📝 Writing results to: {output_path}")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("CHRONO AI ASSIGNMENT GRADER - DEMO RESULTS\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Questions: {len(results)}\n")
            
            total_score = sum(float(q.get('score', 0)) for q in results)
            max_score = len(results)
            percentage = (total_score / max_score * 100) if max_score > 0 else 0
            
            f.write(f"Overall Score: {total_score:.1f}/{max_score} ({percentage:.1f}%)\n")
            f.write("=" * 60 + "\n")
            f.write("NOTE: This is a DEMO version with limited grading capabilities.\n")
            f.write("For full AI-powered grading, use the main chrono_grader.py with OpenAI API.\n")
            f.write("=" * 60 + "\n\n")
            
            # Write each question
            for i, result in enumerate(results, 1):
                question_num = result.get('question_number', str(i))
                
                f.write(f"Q{question_num}: {result.get('question_text', 'No question text')}\n")
                f.write(f"Student Answer: {result.get('student_answer', 'No answer provided')}\n")
                f.write(f"Status: {result.get('status', 'Unknown')}\n")
                
                if result.get('status') != 'Correct':
                    f.write(f"Correct Answer: {result.get('correct_answer', 'Not available')}\n")
                
                if result.get('explanation'):
                    f.write(f"Explanation: {result.get('explanation')}\n")
                
                if result.get('feedback'):
                    f.write(f"Feedback: {result.get('feedback')}\n")
                
                score = result.get('score', 0)
                f.write(f"Points: {score}/1.0\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"✅ Demo results written to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error writing results: {e}")
        raise

def main_demo(image_path: str, output_path: Optional[str] = None):
    """Main demo function"""
    print("🚀 Starting Chrono AI Assignment Grader - DEMO VERSION")
    print("ℹ️  This version works without OpenAI API for testing purposes")
    print(f"📸 Input image: {image_path}")
    
    try:
        # Extract text
        extracted_text = extract_text(image_path)
        
        # Parse questions
        questions = parse_questions(extracted_text)
        
        if not questions:
            print("❌ No questions could be parsed from the image.")
            return None
        
        # Demo grading
        graded_results = demo_grade_questions(questions)
        
        # Write results
        output_file = write_results(graded_results, output_path)
        
        print("🎉 Demo grading completed!")
        print(f"📄 Results saved to: {output_file}")
        print("\n🔔 To get full AI-powered grading:")
        print("   1. Add credits to your OpenAI account")
        print("   2. Use: python chrono_grader.py sample_homework.png")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Demo grading failed: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chrono AI Assignment Grader - Demo Version')
    parser.add_argument('image_path', help='Path to the homework image file')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    try:
        output_file = main_demo(args.image_path, args.output)
        print(f"\n🎯 DEMO SUCCESS! Results saved to: {output_file}")
    except Exception as e:
        print(f"\n💥 DEMO FAILED! Error: {e}")
        exit(1)

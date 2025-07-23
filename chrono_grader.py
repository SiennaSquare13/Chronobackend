"""
Chrono AI Assignment Grader - MVP
A standalone Python program that grades student homework assignments from images.

Author: Chrono Team
Date: July 2025
"""

import pytesseract
from PIL import Image
import openai
import json
import re
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Configure Tesseract path (adjust if needed)
tesseract_path = os.getenv('TESSERACT_CMD')
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
openai.api_key = OPENAI_API_KEY

def extract_text(image_path: str) -> str:
    """
    Extract all text from an image using pytesseract OCR.
    
    Args:
        image_path (str): Path to the image file (JPEG/PNG/PDF)
    
    Returns:
        str: Raw extracted text from the image
    
    Raises:
        FileNotFoundError: If the image file doesn't exist
        Exception: If OCR processing fails
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Open and process the image
        print(f"📸 Processing image: {image_path}")
        
        # Open the image using PIL
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Configure OCR settings for better accuracy
            custom_oem_psm_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,?!:;()[]{}+=*/-_ '
            
            # Extract text using pytesseract
            extracted_text = pytesseract.image_to_string(
                img, 
                config=custom_oem_psm_config,
                lang='eng'  # Use English language model
            )
            
            # Clean up the extracted text
            cleaned_text = clean_extracted_text(extracted_text)
            
            print(f"✅ Text extraction completed. Characters extracted: {len(cleaned_text)}")
            print(f"📄 Preview: {cleaned_text[:200]}..." if len(cleaned_text) > 200 else f"📄 Full text: {cleaned_text}")
            
            return cleaned_text
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        raise
    except Exception as e:
        print(f"❌ OCR processing failed: {str(e)}")
        raise Exception(f"Failed to extract text from image: {str(e)}")

def clean_extracted_text(raw_text: str) -> str:
    """
    Clean and preprocess the raw OCR text output.
    
    Args:
        raw_text (str): Raw text from OCR
    
    Returns:
        str: Cleaned and formatted text
    """
    # Remove excessive whitespace and normalize line breaks
    cleaned = re.sub(r'\n\s*\n', '\n\n', raw_text)  # Multiple newlines to double newline
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Multiple spaces/tabs to single space
    cleaned = cleaned.strip()
    
    # Fix common OCR mistakes
    ocr_corrections = {
        '|': 'I',  # Common mistake: | instead of I
        '0': 'O',  # In some contexts
        'S': '5',  # In mathematical contexts
        '§': 'S',  # Special character corrections
    }
    
    # Apply corrections carefully (context-aware would be better)
    # For now, we'll keep it simple and let GPT handle most corrections
    
    return cleaned

def parse_questions(text: str) -> List[Dict[str, str]]:
    """
    Parse questions and student answers from the extracted text.
    
    Args:
        text (str): Cleaned text from OCR
    
    Returns:
        List[Dict[str, str]]: List of dictionaries containing question and answer pairs
    """
    print("📝 Parsing questions and answers from text...")
    
    # Pattern to match question numbers (Q1, Q2, Question 1, 1., etc.)
    question_patterns = [
        r'(?:Q|Question|Prob|Problem)\s*(\d+)[\.:)]?\s*(.+?)(?=(?:Q|Question|Prob|Problem)\s*\d+|$)',
        r'(\d+)[\.:)]\s*(.+?)(?=\d+[\.:)]|$)',
        r'(\d+)\.\s*(.+?)(?=\d+\.|$)'
    ]
    
    questions = []
    
    # Try each pattern to find questions
    for pattern in question_patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f"✅ Found {len(matches)} questions using pattern: {pattern}")
            
            for match in matches:
                question_num = match[0].strip()
                content = match[1].strip()
                
                # Try to separate question from answer
                parsed_qa = separate_question_answer(content)
                
                questions.append({
                    'question_number': question_num,
                    'question_text': parsed_qa['question'],
                    'student_answer': parsed_qa['answer'],
                    'raw_content': content
                })
            break
    
    # If no structured questions found, try to use GPT to parse
    if not questions:
        print("⚠️ No structured questions found. Using GPT to parse...")
        questions = parse_with_gpt(text)
    
    print(f"📊 Total questions parsed: {len(questions)}")
    return questions

def separate_question_answer(content: str) -> Dict[str, str]:
    """
    Attempt to separate question text from student answer within the content.
    
    Args:
        content (str): Combined question and answer content
    
    Returns:
        Dict[str, str]: Dictionary with 'question' and 'answer' keys
    """
    # Look for common answer indicators
    answer_indicators = [
        r'Answer:?\s*(.+?)(?=\n|$)',
        r'Ans:?\s*(.+?)(?=\n|$)',
        r'Solution:?\s*(.+?)(?=\n|$)',
        r'=\s*(.+?)(?=\n|$)',
        r'\?\s*(.+?)(?=\n|$)'  # Answer after question mark
    ]
    
    question_text = content
    student_answer = ""
    
    for indicator in answer_indicators:
        match = re.search(indicator, content, re.IGNORECASE)
        if match:
            student_answer = match.group(1).strip()
            question_text = content[:match.start()].strip()
            break
    
    # If no clear separation, try to split at common break points
    if not student_answer:
        lines = content.split('\n')
        if len(lines) > 1:
            # Assume first line(s) are question, last line(s) are answer
            question_text = lines[0].strip()
            student_answer = ' '.join(lines[1:]).strip()
    
    return {
        'question': question_text,
        'answer': student_answer if student_answer else content
    }

def parse_with_gpt(text: str) -> List[Dict[str, str]]:
    """
    Use GPT to parse questions and answers when regular patterns fail.
    
    Args:
        text (str): Raw text to parse
    
    Returns:
        List[Dict[str, str]]: Parsed questions and answers
    """
    try:
        prompt = f"""
        Please parse the following homework assignment text and extract questions and student answers.
        Return the result as a JSON array where each object has:
        - question_number: The question number or identifier
        - question_text: The actual question being asked
        - student_answer: The student's answer to that question
        - raw_content: The original text content for this question
        
        Text to parse:
        {text}
        
        Return only valid JSON, no other text.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that parses homework assignments. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.1
        )
        
        result = response["choices"][0]["message"]["content"].strip()
        questions = json.loads(result)
        
        print(f"🤖 GPT successfully parsed {len(questions)} questions")
        return questions
        
    except Exception as e:
        print(f"❌ GPT parsing failed: {e}")
        # Return a single question with all content if parsing fails
        return [{
            'question_number': '1',
            'question_text': text,
            'student_answer': 'Could not parse answer',
            'raw_content': text
        }]

def verify_grading(question, student_answer, ai_grade, ai_feedback):
    """
    Double-check the AI's grading for mathematical accuracy
    """
    # Extract numbers and operators from the question and answer
    import re
    
    # Simple verification for basic arithmetic
    if any(op in question for op in ['+', '-', '×', '*', '÷', '/']):
        # Extract calculation from question
        calc_match = re.search(r'(\d+)\s*([+\-×*÷/])\s*(\d+)', question)
        if calc_match:
            num1, op, num2 = calc_match.groups()
            num1, num2 = int(num1), int(num2)
            
            # Calculate expected answer
            expected = None
            if op in ['+']:
                expected = num1 + num2
            elif op in ['-']:
                expected = num1 - num2
            elif op in ['×', '*']:
                expected = num1 * num2
            elif op in ['÷', '/'] and num2 != 0:
                expected = num1 / num2
            
            # Extract student's numeric answer
            student_num = re.search(r'(\d+(?:\.\d+)?)', str(student_answer))
            if student_num and expected is not None:
                student_val = float(student_num.group(1))
                
                # Check if AI grading matches mathematical reality
                is_correct = abs(student_val - expected) < 0.01
                ai_says_correct = 'correct' in ai_grade.lower() or '✓' in ai_grade
                
                if is_correct != ai_says_correct:
                    # Override AI's decision
                    return {
                        'grade': 'Correct ✓' if is_correct else 'Incorrect ✗',
                        'feedback': f"Mathematical verification: {num1} {op} {num2} = {expected}. Student answered: {student_val}. {'This is correct!' if is_correct else 'This is incorrect.'}"
                    }
    
    # If no verification needed or possible, return AI's original grading
    return {'grade': ai_grade, 'feedback': ai_feedback}

def grade_questions(questions: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Grade each question using OpenAI's GPT model.
    
    Args:
        questions (List[Dict[str, str]]): List of parsed questions and answers
    
    Returns:
        List[Dict[str, str]]: List of graded questions with results
    """
    print("🔍 Starting to grade questions using AI...")
    
    graded_results = []
    
    for i, question in enumerate(questions, 1):
        print(f"📚 Grading Question {question['question_number']} ({i}/{len(questions)})")
        
        try:
            # Create a detailed prompt for grading
            grading_prompt = f"""
            You are an expert teacher grading a student's homework assignment. Please grade this question carefully and fairly.
            
            QUESTION: {question['question_text']}
            STUDENT ANSWER: {question['student_answer']}
            
            IMPORTANT GRADING GUIDELINES:
            1. Focus on the FINAL ANSWER and mathematical correctness, not just the process
            2. If the student's final numerical answer is correct, give full credit even if there are minor formatting issues
            3. Be forgiving of OCR errors in the text (garbled symbols, spacing issues)
            4. For math problems, check if the numerical result is mathematically correct
            5. Consider partial credit for correct method but wrong calculation
            6. Double-check your own calculations before marking something wrong
            
            EXAMPLES OF CORRECT GRADING:
            - If question asks "What is 15 + 23?" and student answers "38", this should be CORRECT
            - If student shows "A = π × 5² ≈ 78.54" for circle area with radius 5, this should be CORRECT
            - Focus on mathematical accuracy, not perfect formatting
            
            Please provide your response in this exact JSON format:
            {{
                "status": "Correct" or "Incorrect" or "Partially Correct",
                "correct_answer": "The complete correct answer",
                "explanation": "Brief explanation of why it's right/wrong - be specific about calculations",
                "score": 1.0 for correct, 0.0 for incorrect, 0.5 for partial credit,
                "feedback": "Constructive feedback for the student"
            }}
            
            Return only valid JSON, no other text.
            """
            
            # Call OpenAI API with improved settings
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Using available model
                messages=[
                    {"role": "system", "content": "You are an expert mathematics teacher with 20+ years of experience. You grade assignments carefully, focusing on mathematical correctness and student understanding. Always double-check calculations before marking answers wrong. Give partial credit for correct methods even if final answer is wrong."},
                    {"role": "user", "content": grading_prompt}
                ],
                max_tokens=800,  # Increased for more detailed feedback
                temperature=0.05  # Very low temperature for maximum consistency
            )
            
            # Parse the response
            grading_result = json.loads(response["choices"][0]["message"]["content"].strip())
            
            # Apply verification to double-check AI's work
            verified_result = verify_grading(
                question['question_text'], 
                question['student_answer'], 
                grading_result['status'], 
                grading_result['feedback']
            )
            
            # Update grading result with verification
            if verified_result['grade'] != grading_result['status']:
                print(f"   🔍 Verification override: {grading_result['status']} → {verified_result['grade']}")
                grading_result['status'] = verified_result['grade']
                grading_result['feedback'] = verified_result['feedback']
                grading_result['score'] = '10/10' if 'Correct' in verified_result['grade'] else '0/10'
            
            # Combine original question data with grading results
            graded_question = {
                **question,  # Original question data
                **grading_result,  # Grading results
                'graded_at': f"Question {question['question_number']}"
            }
            
            graded_results.append(graded_question)
            
            print(f"   ✅ Status: {grading_result['status']} (Score: {grading_result['score']})")
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing error for Q{question['question_number']}: {e}")
            # Fallback result
            graded_results.append({
                **question,
                'status': 'Error - Could not grade',
                'correct_answer': 'Unable to determine',
                'explanation': 'AI grading failed - manual review needed',
                'score': 0.0,
                'feedback': 'Please review this question manually.',
                'graded_at': f"Question {question['question_number']}"
            })
            
        except Exception as e:
            print(f"   ❌ Grading error for Q{question['question_number']}: {e}")
            # Fallback result
            graded_results.append({
                **question,
                'status': 'Error - Could not grade',
                'correct_answer': 'Unable to determine',
                'explanation': 'AI grading failed - manual review needed',
                'score': 0.0,
                'feedback': 'Please review this question manually.',
                'graded_at': f"Question {question['question_number']}"
            })
    
    # Calculate overall statistics
    total_score = sum(q['score'] for q in graded_results if isinstance(q.get('score'), (int, float)))
    max_score = len(graded_results)
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    print(f"📊 Grading completed!")
    print(f"   Total Score: {total_score:.1f}/{max_score} ({percentage:.1f}%)")
    
    return graded_results

def write_results(results: List[Dict[str, str]], output_path: Optional[str] = None) -> str:
    """
    Write grading results to a formatted text file.
    
    Args:
        results (List[Dict[str, str]]): List of graded questions
        output_path (str, optional): Output file path. If None, auto-generate.
    
    Returns:
        str: Path to the output file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"chrono_grading_results_{timestamp}.txt"
    
    print(f"📝 Writing results to: {output_path}")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 60 + "\n")
            f.write("CHRONO AI ASSIGNMENT GRADING RESULTS\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Questions: {len(results)}\n")
            
            # Calculate and write summary
            total_score = 0.0
            for q in results:
                score = q.get('score', 0)
                if isinstance(score, (int, float)):
                    total_score += float(score)
            
            max_score = len(results)
            percentage = (total_score / max_score * 100) if max_score > 0 else 0
            
            f.write(f"Overall Score: {total_score:.1f}/{max_score} ({percentage:.1f}%)\n")
            f.write("=" * 60 + "\n\n")
            
            # Write each question result
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
            
            # Footer
            f.write("=" * 60 + "\n")
            f.write("Report generated by Chrono AI Assignment Grader\n")
            f.write("=" * 60 + "\n")
        
        print(f"✅ Results successfully written to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error writing results: {e}")
        raise Exception(f"Failed to write results to file: {e}")

def main(image_path: str, output_path: Optional[str] = None):
    """
    Main function to process an assignment image and generate grading results.
    
    Args:
        image_path (str): Path to the homework image
        output_path (str, optional): Output file path
    """
    print("🚀 Starting Chrono AI Assignment Grader...")
    print(f"📸 Input image: {image_path}")
    
    try:
        # Step 1: Extract text from image
        extracted_text = extract_text(image_path)
        
        # Step 2: Parse questions and answers
        questions = parse_questions(extracted_text)
        
        if not questions:
            print("❌ No questions could be parsed from the image.")
            return None
        
        # Step 3: Grade questions
        graded_results = grade_questions(questions)
        
        # Step 4: Write results to file
        output_file = write_results(graded_results, output_path)
        
        print("🎉 Assignment grading completed successfully!")
        print(f"📄 Results saved to: {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Assignment grading failed: {e}")
        raise

def test_extract_text():
    """Test function for the text extraction functionality."""
    print("🧪 Testing text extraction functionality...")
    
    # Test with a sample image path (you would replace this with an actual image)
    test_image = "sample_homework.png"
    
    if os.path.exists(test_image):
        try:
            result = extract_text(test_image)
            print(f"✅ Test passed! Extracted text length: {len(result)}")
            return result
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return None
    else:
        print(f"⚠️ Test image '{test_image}' not found. Create a sample image to test.")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chrono AI Assignment Grader')
    parser.add_argument('image_path', help='Path to the homework image file')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode
        test_result = test_extract_text()
        if test_result:
            print("\n" + "="*50)
            print("EXTRACTED TEXT SAMPLE:")
            print("="*50)
            print(test_result)
    else:
        # Normal operation
        try:
            output_file = main(args.image_path, args.output)
            print(f"\n🎯 SUCCESS! Grading results saved to: {output_file}")
        except Exception as e:
            print(f"\n💥 FAILED! Error: {e}")
            exit(1)

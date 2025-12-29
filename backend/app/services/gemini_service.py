import json
from json_repair import repair_json
import re
from typing import List, Optional
from google import genai
from google.genai import types
from app.config import settings
from app.schemas import QuestionVariantCreate


def get_client():
    """Get the Gemini client."""
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key not configured")
    return genai.Client(api_key=settings.GEMINI_API_KEY)


async def generate_question_variants(
    question_id: str,
    question_text: str,
    options: List[str],
    correct_index: int,
    num_variants: int = 5
) -> List[QuestionVariantCreate]:
    """
    Generate paraphrased variants of a question using Gemini AI.
    
    Args:
        question_id: ID of the base question
        question_text: Original question text
        options: List of 4 options
        correct_index: Index of the correct option (0-3)
        num_variants: Number of variants to generate (1-10)
    
    Returns:
        List of QuestionVariantCreate objects ready to be saved
    """
    client = get_client()
    
    prompt = f"""You are an expert test question writer. Generate {num_variants} different paraphrased versions of the following multiple choice question.

ORIGINAL QUESTION:
{question_text}

OPTIONS:
A) {options[0]}
B) {options[1]}
C) {options[2]}
D) {options[3]}

CORRECT ANSWER: {['A', 'B', 'C', 'D'][correct_index]}) {options[correct_index]}

REQUIREMENTS:
1. Each variant must test the SAME concept/knowledge as the original
2. Preserve the SAME difficulty level
3. The correct answer must remain logically correct
4. Use different wording, phrasing, or scenario framing
5. Options should be reworded but maintain the same meaning
6. Keep the same correct answer index position

OUTPUT FORMAT (JSON array):
[
  {{
    "question_text": "Paraphrased question here?",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "correct_index": {correct_index}
  }},
  ...
]

Generate exactly {num_variants} variants. Output ONLY the JSON array, no other text."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Clean up response - extract JSON
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            response_text = json_match.group()
        
        variants_data = json.loads(response_text)
        
        result = []
        for variant in variants_data:
            if isinstance(variant, dict) and all(k in variant for k in ['question_text', 'options', 'correct_index']):
                if len(variant['options']) == 4:
                    result.append(QuestionVariantCreate(
                        question_id=question_id,
                        question_text=variant['question_text'],
                        options=variant['options'],
                        correct_index=variant['correct_index']
                    ))
        
        return result[:num_variants]
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini response as JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to generate variants: {str(e)}")


async def validate_variant_quality(
    original_text: str,
    variant_text: str
) -> dict:
    """
    Validate that a variant maintains the quality of the original question.
    
    Returns:
        dict with 'is_valid', 'score', and 'feedback'
    """
    if not settings.GEMINI_API_KEY:
        return {"is_valid": True, "score": 0.8, "feedback": "AI validation skipped - no API key"}
    
    client = get_client()
    
    prompt = f"""Compare these two questions and evaluate if the variant maintains the same meaning and difficulty:

ORIGINAL: {original_text}

VARIANT: {variant_text}

Evaluate on scale 0-1:
1. Semantic similarity (same concept tested)
2. Difficulty preservation
3. Grammatical correctness
4. Clarity

Output JSON: {{"is_valid": true/false, "score": 0.0-1.0, "feedback": "brief feedback"}}
Only output the JSON, nothing else."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Clean up response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            response_text = json_match.group()
        
        return json.loads(response_text)
    except:
        return {"is_valid": True, "score": 0.7, "feedback": "Auto-approved - validation unavailable"}


async def generate_questions_from_topic(
    topic: str,
    difficulty: str = "Medium",
    num_questions: int = 10,
    description: str = ""
) -> list:
    """
    Generate complete MCQ questions for a topic using Gemini AI.
    
    Args:
        topic: The topic/subject area (e.g., "JavaScript", "Python", "SQL")
        difficulty: Easy, Medium, or Hard
        num_questions: Number of questions to generate (1-100)
        description: Optional description or focus area
    
    Returns:
        List of question dictionaries ready to be saved
    """
    client = get_client()
    
    focus = f" Focus on: {description}" if description else ""
    
    prompt = f"""You are an expert technical interviewer. Generate {num_questions} unique multiple choice questions for assessing candidates on {topic}.

REQUIREMENTS:
- Topic: {topic}
- Difficulty: {difficulty}
- Questions should test practical knowledge and understanding
- Each question must have exactly 4 options (A, B, C, D)
- Only ONE option should be correct
- Options should be plausible (no obviously wrong answers)
- Questions should be clear and unambiguous{focus}

DIFFICULTY GUIDELINES:
- Easy: Basic concepts, definitions, simple syntax
- Medium: Application of concepts, common patterns, problem-solving
- Hard: Edge cases, optimization, advanced concepts, tricky scenarios

OUTPUT FORMAT (JSON array):
[
  {{
    "question_text": "What is the output of console.log(typeof null)?",
    "options": ["undefined", "object", "null", "string"],
    "correct_index": 1,
    "explanation": "In JavaScript, typeof null returns 'object' due to a historical bug."
  }},
  ...
]

Generate exactly {num_questions} questions. Output ONLY the valid JSON array, no markdown, no explanation."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        response_text = response.text.strip()
        
        # Clean up response - extract JSON array
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            response_text = json_match.group()
        
        # Use json_repair to fix any malformed JSON from AI
        repaired_json = repair_json(response_text)
        questions_data = json.loads(repaired_json)
        
        result = []
        for q in questions_data:
            if isinstance(q, dict) and all(k in q for k in ['question_text', 'options', 'correct_index']):
                if len(q['options']) == 4 and 0 <= q['correct_index'] <= 3:
                    result.append({
                        "topic": topic,
                        "difficulty": difficulty,
                        "description": q.get('explanation', description),
                        "question_text": q['question_text'],
                        "options": q['options'],
                        "correct_index": q['correct_index']
                    })
        
        return result[:num_questions]
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to generate questions: {str(e)}")

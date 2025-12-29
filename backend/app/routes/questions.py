from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.schemas import (
    BaseQuestionCreate,
    BaseQuestionResponse,
    QuestionVariantCreate,
    QuestionVariantResponse,
    GenerateVariantsRequest,
    GenerateVariantsResponse,
    ApproveVariantRequest
)
from app.services import (
    create_base_question,
    get_base_questions,
    get_base_question_by_id,
    delete_base_question,
    create_variant,
    get_variants_by_question_id,
    approve_variant,
    get_pending_variants,
    get_topics,
    get_question_stats,
    generate_question_variants
)
from app.utils import get_current_admin

router = APIRouter(prefix="/questions", tags=["Questions"])


# ============ Base Questions ============

@router.post("/base", response_model=BaseQuestionResponse)
async def create_new_base_question(
    question: BaseQuestionCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new base question."""
    return await create_base_question(question, current_admin["admin_id"])


@router.get("/base", response_model=List[BaseQuestionResponse])
async def list_base_questions(
    topic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin)
):
    """Get list of base questions with optional filters."""
    return await get_base_questions(topic, difficulty, skip, limit)


@router.get("/base/{question_id}", response_model=BaseQuestionResponse)
async def get_base_question(
    question_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get a specific base question."""
    return await get_base_question_by_id(question_id)


@router.delete("/base/{question_id}")
async def delete_question(
    question_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a base question and all its variants."""
    await delete_base_question(question_id)
    return {"message": "Question deleted successfully"}


# ============ Question Variants ============

@router.post("/variants", response_model=QuestionVariantResponse)
async def create_question_variant(
    variant: QuestionVariantCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new question variant (manually)."""
    return await create_variant(variant, is_ai_generated=False)


@router.get("/variants/{question_id}", response_model=List[QuestionVariantResponse])
async def list_variants(
    question_id: str,
    approved_only: bool = Query(False),
    current_admin: dict = Depends(get_current_admin)
):
    """Get all variants for a base question."""
    return await get_variants_by_question_id(question_id, approved_only)


@router.put("/variants/{variant_id}/approve", response_model=QuestionVariantResponse)
async def approve_reject_variant(
    variant_id: str,
    request: ApproveVariantRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """Approve or reject a question variant."""
    return await approve_variant(variant_id, request.approved, current_admin["admin_id"])


@router.get("/pending", response_model=List[QuestionVariantResponse])
async def list_pending_variants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin)
):
    """Get all pending (unapproved) variants."""
    return await get_pending_variants(skip, limit)


# ============ AI Generation ============

@router.post("/generate-variants", response_model=GenerateVariantsResponse)
async def generate_ai_variants(
    request: GenerateVariantsRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """Generate AI variants for a base question using Gemini."""
    variants_data = await generate_question_variants(
        question_id=request.question_id,
        question_text=request.base_question_text,
        options=request.options,
        correct_index=request.correct_index,
        num_variants=request.num_variants
    )
    
    # Save generated variants
    saved_variants = []
    for variant_data in variants_data:
        saved = await create_variant(variant_data, is_ai_generated=True)
        saved_variants.append(saved)
    
    return GenerateVariantsResponse(
        question_id=request.question_id,
        variants_generated=len(saved_variants),
        variants=saved_variants
    )


@router.post("/generate-questions")
async def generate_ai_questions(
    request: dict,
    current_admin: dict = Depends(get_current_admin)
):
    """Generate complete questions for a topic using AI."""
    from app.services import generate_questions_from_topic, create_base_question, create_variant
    from app.schemas import BaseQuestionCreate
    
    topic = request.get("topic", "")
    difficulty = request.get("difficulty", "Medium")
    num_questions = request.get("num_questions", 10)
    description = request.get("description", "")
    
    if not topic:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Topic is required")
    
    # Generate questions using AI
    questions_data = await generate_questions_from_topic(
        topic=topic,
        difficulty=difficulty,
        num_questions=num_questions,
        description=description
    )
    
    # Save each question to database
    saved_questions = []
    for q in questions_data:
        # Create base question
        base_q = await create_base_question(
            BaseQuestionCreate(
                topic=q["topic"],
                difficulty=q["difficulty"],
                description=q["description"]
            ),
            str(current_admin["_id"])
        )
        
        # Create the variant
        from app.schemas import QuestionVariantCreate
        await create_variant(
            QuestionVariantCreate(
                question_id=base_q.id,
                question_text=q["question_text"],
                options=q["options"],
                correct_index=q["correct_index"]
            ),
            is_ai_generated=True,
            auto_approve=True  # Auto-approve for immediate use
        )
        
        saved_questions.append(base_q)
    
    return {
        "topic": topic,
        "difficulty": difficulty,
        "questions_generated": len(saved_questions),
        "questions": saved_questions
    }


# ============ Statistics ============

@router.get("/topics", response_model=List[str])
async def list_topics(current_admin: dict = Depends(get_current_admin)):
    """Get all unique topics."""
    return await get_topics()


@router.get("/stats")
async def question_statistics(current_admin: dict = Depends(get_current_admin)):
    """Get question statistics."""
    return await get_question_stats()

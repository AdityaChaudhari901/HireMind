from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from app.database import get_database
from app.models import BaseQuestionModel, QuestionVariantModel
from app.schemas import (
    BaseQuestionCreate,
    BaseQuestionResponse,
    QuestionVariantCreate,
    QuestionVariantResponse
)
from app.utils import generate_unique_id


async def create_base_question(
    question_data: BaseQuestionCreate,
    created_by: str
) -> BaseQuestionResponse:
    """Create a new base question."""
    db = get_database()
    
    question_doc = {
        "topic": question_data.topic,
        "difficulty": question_data.difficulty.value,
        "description": question_data.description,
        "created_at": datetime.utcnow(),
        "created_by": created_by
    }
    
    result = await db.base_questions.insert_one(question_doc)
    
    return BaseQuestionResponse(
        id=str(result.inserted_id),
        topic=question_data.topic,
        difficulty=question_data.difficulty.value,
        description=question_data.description,
        created_at=question_doc["created_at"],
        variant_count=0
    )


async def get_base_questions(
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[BaseQuestionResponse]:
    """Get list of base questions with optional filters."""
    db = get_database()
    
    query = {}
    if topic:
        query["topic"] = topic
    if difficulty:
        query["difficulty"] = difficulty
    
    cursor = db.base_questions.find(query).skip(skip).limit(limit)
    questions = await cursor.to_list(length=limit)
    
    result = []
    for q in questions:
        # Count variants for each question
        variant_count = await db.question_variants.count_documents({
            "question_id": str(q["_id"])
        })
        
        result.append(BaseQuestionResponse(
            id=str(q["_id"]),
            topic=q["topic"],
            difficulty=q["difficulty"],
            description=q.get("description"),
            created_at=q["created_at"],
            variant_count=variant_count
        ))
    
    return result


async def get_base_question_by_id(question_id: str) -> BaseQuestionResponse:
    """Get a base question by ID."""
    db = get_database()
    
    question = await db.base_questions.find_one({"_id": ObjectId(question_id)})
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base question not found"
        )
    
    variant_count = await db.question_variants.count_documents({
        "question_id": question_id
    })
    
    return BaseQuestionResponse(
        id=str(question["_id"]),
        topic=question["topic"],
        difficulty=question["difficulty"],
        description=question.get("description"),
        created_at=question["created_at"],
        variant_count=variant_count
    )


async def delete_base_question(question_id: str) -> bool:
    """Delete a base question and its variants."""
    db = get_database()
    
    # Delete variants first
    await db.question_variants.delete_many({"question_id": question_id})
    
    # Delete base question
    result = await db.base_questions.delete_one({"_id": ObjectId(question_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base question not found"
        )
    
    return True


async def create_variant(
    variant_data: QuestionVariantCreate,
    is_ai_generated: bool = False
) -> QuestionVariantResponse:
    """Create a question variant."""
    db = get_database()
    
    # Verify base question exists
    base_question = await db.base_questions.find_one({
        "_id": ObjectId(variant_data.question_id)
    })
    if not base_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base question not found"
        )
    
    variant_doc = {
        "question_id": variant_data.question_id,
        "question_text": variant_data.question_text,
        "options": variant_data.options,
        "correct_answer": variant_data.options[variant_data.correct_index],
        "correct_index": variant_data.correct_index,
        "approved": not is_ai_generated,  # Manual variants are auto-approved
        "is_ai_generated": is_ai_generated,
        "created_at": datetime.utcnow()
    }
    
    result = await db.question_variants.insert_one(variant_doc)
    
    return QuestionVariantResponse(
        id=str(result.inserted_id),
        question_id=variant_data.question_id,
        question_text=variant_data.question_text,
        options=variant_data.options,
        correct_index=variant_data.correct_index,
        approved=variant_doc["approved"],
        is_ai_generated=is_ai_generated,
        created_at=variant_doc["created_at"]
    )


async def get_variants_by_question_id(
    question_id: str,
    approved_only: bool = False
) -> List[QuestionVariantResponse]:
    """Get all variants for a base question."""
    db = get_database()
    
    query = {"question_id": question_id}
    if approved_only:
        query["approved"] = True
    
    cursor = db.question_variants.find(query)
    variants = await cursor.to_list(length=100)
    
    return [
        QuestionVariantResponse(
            id=str(v["_id"]),
            question_id=v["question_id"],
            question_text=v["question_text"],
            options=v["options"],
            correct_index=v["correct_index"],
            approved=v["approved"],
            is_ai_generated=v.get("is_ai_generated", False),
            created_at=v["created_at"]
        )
        for v in variants
    ]


async def approve_variant(
    variant_id: str,
    approved: bool,
    approved_by: str
) -> QuestionVariantResponse:
    """Approve or reject a variant."""
    db = get_database()
    
    update_data = {
        "approved": approved,
        "approved_at": datetime.utcnow() if approved else None,
        "approved_by": approved_by if approved else None
    }
    
    result = await db.question_variants.find_one_and_update(
        {"_id": ObjectId(variant_id)},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )
    
    return QuestionVariantResponse(
        id=str(result["_id"]),
        question_id=result["question_id"],
        question_text=result["question_text"],
        options=result["options"],
        correct_index=result["correct_index"],
        approved=result["approved"],
        is_ai_generated=result.get("is_ai_generated", False),
        created_at=result["created_at"]
    )


async def get_pending_variants(
    skip: int = 0,
    limit: int = 50
) -> List[QuestionVariantResponse]:
    """Get all pending (unapproved) variants."""
    db = get_database()
    
    cursor = db.question_variants.find({"approved": False}).skip(skip).limit(limit)
    variants = await cursor.to_list(length=limit)
    
    return [
        QuestionVariantResponse(
            id=str(v["_id"]),
            question_id=v["question_id"],
            question_text=v["question_text"],
            options=v["options"],
            correct_index=v["correct_index"],
            approved=v["approved"],
            is_ai_generated=v.get("is_ai_generated", False),
            created_at=v["created_at"]
        )
        for v in variants
    ]


async def get_topics() -> List[str]:
    """Get all unique topics."""
    db = get_database()
    topics = await db.base_questions.distinct("topic")
    return topics


async def get_question_stats() -> dict:
    """Get question statistics."""
    db = get_database()
    
    total_base = await db.base_questions.count_documents({})
    total_variants = await db.question_variants.count_documents({})
    approved_variants = await db.question_variants.count_documents({"approved": True})
    pending_variants = await db.question_variants.count_documents({"approved": False})
    
    return {
        "total_base_questions": total_base,
        "total_variants": total_variants,
        "approved_variants": approved_variants,
        "pending_variants": pending_variants
    }

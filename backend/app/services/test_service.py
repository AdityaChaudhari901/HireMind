import random
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException, status
from app.database import get_database
from app.models import TestSessionModel, TestLinkModel, AssignedQuestion
from app.schemas import (
    CreateTestLinkRequest,
    TestLinkResponse,
    StartTestRequest,
    StartTestResponse,
    QuestionResponse
)
from app.utils import generate_unique_id, shuffle_list
from app.services.timer_service import timer_service
from app.config import settings


async def create_test_link(
    request: CreateTestLinkRequest,
    created_by: str,
    base_url: str = "http://localhost:5173"
) -> TestLinkResponse:
    """Create a unique test link for candidates."""
    db = get_database()
    
    link_id = generate_unique_id(prefix="test-")
    expires_at = datetime.utcnow() + timedelta(hours=request.expires_hours)
    
    link_doc = {
        "link_id": link_id,
        "test_name": request.test_name,
        "total_questions": request.total_questions,
        "time_per_question": request.time_per_question,
        "topics": request.topics,
        "is_used": False,
        "max_uses": request.max_uses,  # 0 = unlimited
        "current_uses": 0,
        "expires_at": expires_at,
        "created_at": datetime.utcnow(),
        "created_by": created_by
    }
    
    await db.test_links.insert_one(link_doc)
    
    return TestLinkResponse(
        link_id=link_id,
        test_name=request.test_name,
        total_questions=request.total_questions,
        time_per_question=request.time_per_question,
        topics=request.topics,
        full_url=f"{base_url}/test/{link_id}",
        expires_at=expires_at,
        is_used=False,
        max_uses=request.max_uses,
        current_uses=0,
        created_at=link_doc["created_at"]
    )


async def validate_test_link(link_id: str) -> dict:
    """Validate a test link and return its details."""
    db = get_database()
    
    link = await db.test_links.find_one({"link_id": link_id})
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test link not found"
        )
    
    # Check if max uses exceeded (0 = unlimited)
    max_uses = link.get("max_uses", 0)
    current_uses = link.get("current_uses", 0)
    if max_uses > 0 and current_uses >= max_uses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This test link has reached its maximum number of uses"
        )
    
    if link.get("expires_at") and link["expires_at"] < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This test link has expired"
        )
    
    return {
        "valid": True,
        "test_name": link["test_name"],
        "total_questions": link["total_questions"],
        "time_per_question": link["time_per_question"],
        "topics": link.get("topics", [])
    }


async def start_test(
    link_id: str,
    candidate: StartTestRequest,
    ip_address: str,
    user_agent: str
) -> StartTestResponse:
    """Start a test session for a candidate."""
    db = get_database()
    
    # Validate link first
    await validate_test_link(link_id)
    
    # Get link details
    link = await db.test_links.find_one({"link_id": link_id})
    
    # Create or get user
    user = await db.users.find_one({"email": candidate.email})
    if not user:
        user_doc = {
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "created_at": datetime.utcnow()
        }
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
    else:
        user_id = str(user["_id"])
    
    # Check if user already has a session for this link
    existing_session = await db.test_sessions.find_one({
        "test_link_id": link_id,
        "user_id": user_id
    })
    
    if existing_session:
        # Return existing session if not completed
        if not existing_session.get("completed"):
            return StartTestResponse(
                session_id=str(existing_session["_id"]),
                total_questions=link["total_questions"],
                time_per_question=link["time_per_question"],
                message="Resuming existing test session"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already completed this test"
            )
    
    # Generate random questions
    assigned_questions = await _generate_question_set(
        total=link["total_questions"],
        topics=link.get("topics", [])
    )
    
    # Create session
    session_doc = {
        "user_id": user_id,
        "test_link_id": link_id,
        "assigned_questions": [q.dict() for q in assigned_questions],
        "current_index": 0,
        "question_start_time": datetime.utcnow(),
        "started_at": datetime.utcnow(),
        "completed": False,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "tab_switches": [],
        "created_at": datetime.utcnow()
    }
    
    result = await db.test_sessions.insert_one(session_doc)
    
    # Increment usage counter
    max_uses = link.get("max_uses", 0)
    current_uses = link.get("current_uses", 0) + 1
    update_doc = {"$inc": {"current_uses": 1}}
    
    # Mark as fully used if max reached
    if max_uses > 0 and current_uses >= max_uses:
        update_doc["$set"] = {"is_used": True}
    
    await db.test_links.update_one(
        {"link_id": link_id},
        update_doc
    )
    
    return StartTestResponse(
        session_id=str(result.inserted_id),
        total_questions=link["total_questions"],
        time_per_question=link["time_per_question"],
        message="Test started successfully"
    )


async def _generate_question_set(
    total: int = 60,
    topics: List[str] = None
) -> List[AssignedQuestion]:
    """Generate a random set of questions with shuffled options."""
    db = get_database()
    
    # Build query for base questions
    query = {}
    if topics:
        query["topic"] = {"$in": topics}
    
    # Get all base questions matching criteria
    base_questions = await db.base_questions.find(query).to_list(length=1000)
    
    if len(base_questions) < total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough questions available. Need {total}, found {len(base_questions)}"
        )
    
    # Randomly select base questions
    selected_base = random.sample(base_questions, min(total, len(base_questions)))
    
    assigned_questions = []
    
    for base_q in selected_base:
        # Get approved variants for this base question
        variants = await db.question_variants.find({
            "question_id": str(base_q["_id"]),
            "approved": True
        }).to_list(length=100)
        
        if not variants:
            # Skip if no approved variants
            continue
        
        # Randomly select one variant
        selected_variant = random.choice(variants)
        
        # Shuffle options
        original_options = selected_variant["options"]
        shuffled_options, shuffle_mapping = shuffle_list(original_options)
        
        assigned_questions.append(AssignedQuestion(
            variant_id=str(selected_variant["_id"]),
            original_options=original_options,
            shuffled_options=shuffled_options,
            shuffle_mapping=shuffle_mapping
        ))
        
        if len(assigned_questions) >= total:
            break
    
    if len(assigned_questions) < total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough approved variants. Need {total}, found {len(assigned_questions)}"
        )
    
    # Shuffle the question order as well
    random.shuffle(assigned_questions)
    
    return assigned_questions


async def get_current_question(session_id: str) -> QuestionResponse:
    """Get the current question for a session."""
    db = get_database()
    
    session = await db.test_sessions.find_one({"_id": ObjectId(session_id)})
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.get("completed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test already completed"
        )
    
    current_index = session.get("current_index", 0)
    assigned_questions = session.get("assigned_questions", [])
    
    if current_index >= len(assigned_questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No more questions"
        )
    
    current_q = assigned_questions[current_index]
    
    # Get the variant details
    variant = await db.question_variants.find_one({
        "_id": ObjectId(current_q["variant_id"])
    })
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Question variant not found"
        )
    
    # Calculate remaining time
    start_time = session.get("question_start_time")
    if start_time:
        remaining = timer_service.get_remaining_time(start_time)
    else:
        remaining = settings.QUESTION_TIMER_SECONDS
    
    return QuestionResponse(
        variant_id=current_q["variant_id"],
        question_text=variant["question_text"],
        options=current_q["shuffled_options"],  # Send shuffled options
        question_number=current_index + 1,
        total_questions=len(assigned_questions),
        time_remaining=remaining
    )


async def submit_answer(
    session_id: str,
    selected_index: Optional[int]
) -> dict:
    """Submit an answer and move to next question."""
    db = get_database()
    
    session = await db.test_sessions.find_one({"_id": ObjectId(session_id)})
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.get("completed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test already completed"
        )
    
    current_index = session.get("current_index", 0)
    assigned_questions = session.get("assigned_questions", [])
    
    if current_index >= len(assigned_questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No more questions"
        )
    
    current_q = assigned_questions[current_index]
    start_time = session.get("question_start_time")
    
    # Validate submission time
    timer_result = timer_service.validate_submission_time(start_time)
    auto_submitted = timer_result["should_auto_submit"]
    time_taken = timer_result["elapsed"]
    
    # Get variant to check correct answer
    variant = await db.question_variants.find_one({
        "_id": ObjectId(current_q["variant_id"])
    })
    
    # Determine if answer is correct
    is_correct = False
    selected_answer = None
    
    if selected_index is not None and 0 <= selected_index <= 3:
        # Map shuffled index back to original index
        original_index = current_q["shuffle_mapping"][selected_index]
        selected_answer = current_q["original_options"][original_index]
        is_correct = (original_index == variant["correct_index"])
    
    # Save attempt
    attempt_doc = {
        "session_id": session_id,
        "user_id": session["user_id"],
        "question_variant_id": current_q["variant_id"],
        "question_index": current_index,
        "selected_answer": selected_answer,
        "selected_index": selected_index,
        "is_correct": is_correct,
        "time_taken": min(time_taken, settings.QUESTION_TIMER_SECONDS),
        "auto_submitted": auto_submitted,
        "submitted_at": datetime.utcnow()
    }
    
    await db.attempts.insert_one(attempt_doc)
    
    # Move to next question or complete test
    next_index = current_index + 1
    is_last_question = next_index >= len(assigned_questions)
    
    if is_last_question:
        # Complete the test
        await db.test_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$set": {
                    "current_index": next_index,
                    "completed": True,
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "test_completed": True,
            "message": "Test completed successfully"
        }
    else:
        # Update session for next question
        await db.test_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$set": {
                    "current_index": next_index,
                    "question_start_time": datetime.utcnow()
                }
            }
        )
        
        # Get next question
        next_question = await get_current_question(session_id)
        
        return {
            "success": True,
            "test_completed": False,
            "next_question": next_question
        }


async def record_tab_switch(session_id: str) -> bool:
    """Record a tab switch event."""
    db = get_database()
    
    result = await db.test_sessions.update_one(
        {"_id": ObjectId(session_id), "completed": False},
        {"$push": {"tab_switches": datetime.utcnow()}}
    )
    
    return result.modified_count > 0


async def get_session(session_id: str) -> dict:
    """Get session details."""
    db = get_database()
    
    session = await db.test_sessions.find_one({"_id": ObjectId(session_id)})
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {
        "session_id": str(session["_id"]),
        "user_id": session["user_id"],
        "current_index": session.get("current_index", 0),
        "total_questions": len(session.get("assigned_questions", [])),
        "completed": session.get("completed", False),
        "started_at": session.get("started_at"),
        "completed_at": session.get("completed_at"),
        "tab_switch_count": len(session.get("tab_switches", []))
    }


async def get_test_links(
    created_by: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[TestLinkResponse]:
    """Get list of test links."""
    db = get_database()
    
    query = {}
    if created_by:
        query["created_by"] = created_by
    
    cursor = db.test_links.find(query).sort("created_at", -1).skip(skip).limit(limit)
    links = await cursor.to_list(length=limit)
    
    return [
        TestLinkResponse(
            link_id=link["link_id"],
            test_name=link["test_name"],
            total_questions=link["total_questions"],
            time_per_question=link["time_per_question"],
            topics=link.get("topics", []),
            full_url=f"http://localhost:5173/test/{link['link_id']}",
            expires_at=link.get("expires_at"),
            is_used=link.get("is_used", False),
            max_uses=link.get("max_uses", 0),
            current_uses=link.get("current_uses", 0),
            created_at=link["created_at"]
        )
        for link in links
    ]

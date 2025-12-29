from typing import List, Optional
from datetime import datetime
from io import StringIO
import csv
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from bson import ObjectId
from app.database import get_database
from app.schemas import (
    TestResultResponse,
    TestResultSummary,
    ResultsListResponse,
    AttemptResponse
)
from app.utils import get_current_admin, calculate_score

router = APIRouter(prefix="/results", tags=["Results"])


@router.get("", response_model=ResultsListResponse)
async def list_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin)
):
    """Get list of all test results (Admin only)."""
    db = get_database()
    
    # Get completed sessions
    total = await db.test_sessions.count_documents({"completed": True})
    
    cursor = db.test_sessions.aggregate([
        {"$match": {"completed": True}},
        {"$sort": {"completed_at": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user_data"
            }
        }
    ])
    
    sessions = await cursor.to_list(length=limit)
    
    results = []
    for session in sessions:
        # Get user info
        user_id = session["user_id"]
        user = await db.users.find_one({"_id": ObjectId(user_id)}) if ObjectId.is_valid(user_id) else None
        
        if not user:
            user = {"name": "Unknown", "email": "unknown@example.com"}
        
        # Count correct answers
        correct_count = await db.attempts.count_documents({
            "session_id": str(session["_id"]),
            "is_correct": True
        })
        
        total_questions = len(session.get("assigned_questions", []))
        score = calculate_score(correct_count, total_questions)
        
        results.append(TestResultSummary(
            session_id=str(session["_id"]),
            user_name=user.get("name", "Unknown"),
            user_email=user.get("email", "unknown@example.com"),
            score_percentage=score,
            total_questions=total_questions,
            correct_answers=correct_count,
            completed_at=session.get("completed_at"),
            tab_switch_count=len(session.get("tab_switches", []))
        ))
    
    return ResultsListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        results=results
    )


@router.delete("/{session_id}")
async def delete_result(
    session_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a test result and all associated attempts (Admin only)."""
    from fastapi import HTTPException, status
    db = get_database()
    
    # Check if session exists
    session = await db.test_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )
    
    # Delete all attempts for this session
    await db.attempts.delete_many({"session_id": session_id})
    
    # Delete the session
    await db.test_sessions.delete_one({"_id": ObjectId(session_id)})
    
    return {"message": "Result deleted successfully"}


@router.get("/{session_id}", response_model=TestResultResponse)
async def get_result_detail(
    session_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get detailed result for a specific session (Admin only)."""
    db = get_database()
    
    session = await db.test_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get user info
    user_id = session["user_id"]
    user = await db.users.find_one({"_id": ObjectId(user_id)}) if ObjectId.is_valid(user_id) else None
    
    if not user:
        user = {"name": "Unknown", "email": "unknown@example.com", "phone": "N/A"}
    
    # Get all attempts for this session
    attempts = await db.attempts.find({"session_id": session_id}).to_list(length=100)
    
    # Calculate statistics
    total_questions = len(session.get("assigned_questions", []))
    correct = sum(1 for a in attempts if a.get("is_correct"))
    incorrect = sum(1 for a in attempts if not a.get("is_correct") and a.get("selected_answer"))
    unanswered = total_questions - len(attempts)
    auto_submitted = sum(1 for a in attempts if a.get("auto_submitted"))
    total_time = sum(a.get("time_taken", 0) for a in attempts)
    avg_time = total_time / len(attempts) if attempts else 0
    
    score = calculate_score(correct, total_questions)
    
    return TestResultResponse(
        session_id=session_id,
        user_name=user.get("name", "Unknown"),
        user_email=user.get("email", "unknown@example.com"),
        user_phone=user.get("phone", "N/A"),
        total_questions=total_questions,
        correct_answers=correct,
        incorrect_answers=incorrect,
        unanswered=unanswered,
        score_percentage=score,
        total_time_seconds=round(total_time, 2),
        average_time_per_question=round(avg_time, 2),
        auto_submitted_count=auto_submitted,
        tab_switch_count=len(session.get("tab_switches", [])),
        started_at=session.get("started_at"),
        completed_at=session.get("completed_at"),
        ip_address=session.get("ip_address"),
        user_agent=session.get("user_agent")
    )


@router.get("/{session_id}/attempts", response_model=List[AttemptResponse])
async def get_session_attempts(
    session_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get all attempts for a session with detailed question info (Admin only)."""
    db = get_database()
    
    attempts = await db.attempts.find({"session_id": session_id}).sort("question_index", 1).to_list(length=100)
    
    result = []
    for attempt in attempts:
        # Get variant info
        variant = await db.question_variants.find_one({"_id": ObjectId(attempt["question_variant_id"])})
        
        if variant:
            result.append(AttemptResponse(
                question_variant_id=attempt["question_variant_id"],
                question_text=variant["question_text"],
                options=variant["options"],
                selected_answer=attempt.get("selected_answer"),
                correct_answer=variant["options"][variant["correct_index"]],
                is_correct=attempt.get("is_correct", False),
                time_taken=attempt.get("time_taken", 0),
                auto_submitted=attempt.get("auto_submitted", False)
            ))
    
    return result


@router.get("/export/csv")
async def export_results_csv(
    current_admin: dict = Depends(get_current_admin)
):
    """Export all results as CSV (Admin only)."""
    db = get_database()
    
    sessions = await db.test_sessions.find({"completed": True}).to_list(length=10000)
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Session ID",
        "Candidate Name",
        "Candidate Email",
        "Candidate Phone",
        "Total Questions",
        "Correct Answers",
        "Score %",
        "Total Time (s)",
        "Avg Time/Question (s)",
        "Auto-Submitted",
        "Tab Switches",
        "Started At",
        "Completed At",
        "IP Address"
    ])
    
    for session in sessions:
        user_id = session["user_id"]
        user = await db.users.find_one({"_id": ObjectId(user_id)}) if ObjectId.is_valid(user_id) else None
        
        if not user:
            user = {"name": "Unknown", "email": "unknown@example.com", "phone": "N/A"}
        
        attempts = await db.attempts.find({"session_id": str(session["_id"])}).to_list(length=100)
        
        total_questions = len(session.get("assigned_questions", []))
        correct = sum(1 for a in attempts if a.get("is_correct"))
        auto_submitted = sum(1 for a in attempts if a.get("auto_submitted"))
        total_time = sum(a.get("time_taken", 0) for a in attempts)
        avg_time = total_time / len(attempts) if attempts else 0
        score = calculate_score(correct, total_questions)
        
        writer.writerow([
            str(session["_id"]),
            user.get("name", "Unknown"),
            user.get("email", "unknown@example.com"),
            user.get("phone", "N/A"),
            total_questions,
            correct,
            score,
            round(total_time, 2),
            round(avg_time, 2),
            auto_submitted,
            len(session.get("tab_switches", [])),
            session.get("started_at", "").isoformat() if session.get("started_at") else "",
            session.get("completed_at", "").isoformat() if session.get("completed_at") else "",
            session.get("ip_address", "")
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=test_results.csv"}
    )

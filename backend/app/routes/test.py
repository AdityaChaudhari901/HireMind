from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from app.schemas import (
    CreateTestLinkRequest,
    TestLinkResponse,
    StartTestRequest,
    StartTestResponse,
    QuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    TestCompleteResponse
)
from app.services import (
    create_test_link,
    validate_test_link,
    start_test,
    get_current_question,
    submit_answer,
    record_tab_switch,
    get_session,
    get_test_links
)
from app.utils import get_current_admin

router = APIRouter(prefix="/test", tags=["Test"])


# ============ Admin Routes ============

@router.post("/generate-link", response_model=TestLinkResponse)
async def generate_test_link(
    request: CreateTestLinkRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """Generate a unique test link for a candidate (Admin only)."""
    return await create_test_link(request, str(current_admin["_id"]))


@router.get("/links", response_model=List[TestLinkResponse])
async def list_test_links(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin)
):
    """Get list of all test links (Admin only)."""
    return await get_test_links(created_by=None, skip=skip, limit=limit)


@router.delete("/links/{link_id}")
async def delete_test_link(
    link_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a test link (Admin only)."""
    from app.database import get_database
    db = get_database()
    
    result = await db.test_links.delete_one({"link_id": link_id})
    
    if result.deleted_count == 0:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test link not found"
        )
    
    return {"message": "Test link deleted successfully"}


# ============ Candidate Routes ============

@router.get("/{link_id}/validate")
async def validate_link(link_id: str):
    """
    Validate a test link (Public endpoint).
    
    Returns test details if the link is valid, active, and unused.
    """
    return await validate_test_link(link_id)


@router.post("/{link_id}/start", response_model=StartTestResponse)
async def start_candidate_test(
    link_id: str,
    candidate: StartTestRequest,
    request: Request
):
    """
    Start a test for a candidate (Public endpoint).
    
    - Creates candidate user if not exists
    - Generates random question set
    - Locks questions for this session
    - Returns session ID for subsequent requests
    """
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    return await start_test(link_id, candidate, ip_address, user_agent)


@router.get("/session/{session_id}/question", response_model=QuestionResponse)
async def get_question(session_id: str):
    """
    Get current question for a session (Public endpoint).
    
    Returns the current question with shuffled options.
    Correct answer is NOT exposed.
    """
    return await get_current_question(session_id)


@router.post("/session/{session_id}/answer", response_model=SubmitAnswerResponse)
async def submit_question_answer(
    session_id: str,
    answer: SubmitAnswerRequest
):
    """
    Submit answer for current question (Public endpoint).
    
    - Validates submission time server-side
    - Records answer (correct/incorrect determined by backend)
    - Moves to next question or completes test
    """
    result = await submit_answer(session_id, answer.selected_index)
    
    return SubmitAnswerResponse(
        success=result["success"],
        next_question=result.get("next_question"),
        test_completed=result.get("test_completed", False),
        message=result.get("message", "")
    )


@router.post("/session/{session_id}/tab-switch")
async def log_tab_switch(session_id: str):
    """
    Log a tab switch event (Public endpoint).
    
    Called by frontend when candidate switches tabs.
    """
    success = await record_tab_switch(session_id)
    return {"logged": success}


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """
    Get session status (Public endpoint).
    
    Returns current progress and completion status.
    """
    return await get_session(session_id)


@router.post("/session/{session_id}/complete", response_model=TestCompleteResponse)
async def complete_test(session_id: str):
    """
    Manually complete a test (Public endpoint).
    
    Called after the last question is submitted.
    """
    session = await get_session(session_id)
    
    return TestCompleteResponse(
        session_id=session_id,
        total_questions=session["total_questions"],
        answered_questions=session["current_index"],
        message="Test completed successfully. Thank you for your participation."
    )

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AttemptResponse(BaseModel):
    """Schema for individual attempt response."""
    question_variant_id: str
    question_text: str
    options: List[str]
    selected_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    time_taken: float
    auto_submitted: bool


class TestResultResponse(BaseModel):
    """Schema for test result response."""
    session_id: str
    user_name: str
    user_email: str
    user_phone: str
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    unanswered: int
    score_percentage: float
    total_time_seconds: float
    average_time_per_question: float
    auto_submitted_count: int
    tab_switch_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    ip_address: Optional[str]
    user_agent: Optional[str]


class TestResultSummary(BaseModel):
    """Schema for test result summary in list view."""
    session_id: str
    user_name: str
    user_email: str
    score_percentage: float
    total_questions: int
    correct_answers: int
    completed_at: Optional[datetime]
    tab_switch_count: int


class ResultsListResponse(BaseModel):
    """Schema for list of results."""
    total: int
    page: int
    page_size: int
    results: List[TestResultSummary]

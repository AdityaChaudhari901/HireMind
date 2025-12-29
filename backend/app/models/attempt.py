from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AttemptModel(BaseModel):
    """Attempt model - tracks individual question attempts."""
    id: Optional[str] = Field(default=None, alias="_id")
    session_id: str
    user_id: str
    question_variant_id: str
    question_index: int = Field(..., ge=0, le=59)
    selected_answer: Optional[str] = None
    selected_index: Optional[int] = None
    is_correct: bool = Field(default=False)
    time_taken: float = Field(..., ge=0, description="Time taken in seconds")
    auto_submitted: bool = Field(default=False, description="Whether answer was auto-submitted due to timeout")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class AttemptInDB(AttemptModel):
    """Attempt as stored in database."""
    pass


class TestResult(BaseModel):
    """Test result summary."""
    session_id: str
    user_id: str
    user_name: str
    user_email: str
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    unanswered: int
    score_percentage: float
    total_time_seconds: float
    average_time_per_question: float
    auto_submitted_count: int
    tab_switch_count: int
    completed_at: Optional[datetime]
    started_at: Optional[datetime]

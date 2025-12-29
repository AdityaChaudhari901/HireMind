from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CreateTestLinkRequest(BaseModel):
    """Schema for creating a test link."""
    test_name: str = Field(default="Assessment Test")
    total_questions: int = Field(default=60, ge=1, le=100)
    time_per_question: int = Field(default=10, ge=5, le=60)
    topics: List[str] = Field(default_factory=list)
    expires_hours: int = Field(default=72, ge=1, le=720)
    max_uses: int = Field(default=0, ge=0, description="Maximum number of candidates. 0 = unlimited")


class TestLinkResponse(BaseModel):
    """Schema for test link response."""
    link_id: str
    test_name: str
    total_questions: int
    time_per_question: int
    topics: List[str]
    full_url: str
    expires_at: Optional[datetime]
    is_used: bool
    max_uses: int = 0
    current_uses: int = 0
    created_at: datetime


class StartTestRequest(BaseModel):
    """Schema for starting a test."""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(...)
    phone: str = Field(..., min_length=10, max_length=15)


class StartTestResponse(BaseModel):
    """Schema for start test response."""
    session_id: str
    total_questions: int
    time_per_question: int
    message: str = "Test started successfully"


class QuestionResponse(BaseModel):
    """Schema for question response to candidate - NO correct answer."""
    variant_id: str
    question_text: str
    options: List[str]
    question_number: int
    total_questions: int
    time_remaining: int


class SubmitAnswerRequest(BaseModel):
    """Schema for submitting an answer."""
    selected_index: Optional[int] = Field(default=None, ge=0, le=3)


class SubmitAnswerResponse(BaseModel):
    """Schema for submit answer response."""
    success: bool
    next_question: Optional[QuestionResponse] = None
    test_completed: bool = False
    message: str = ""


class TestCompleteResponse(BaseModel):
    """Schema for test completion response."""
    session_id: str
    total_questions: int
    answered_questions: int
    message: str = "Test completed successfully. Thank you for your participation."

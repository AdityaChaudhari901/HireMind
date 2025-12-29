from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.question import DifficultyLevel


class BaseQuestionCreate(BaseModel):
    """Schema for creating a base question."""
    topic: str = Field(..., min_length=1, max_length=100)
    difficulty: DifficultyLevel
    description: Optional[str] = Field(default=None, max_length=500)


class BaseQuestionResponse(BaseModel):
    """Schema for base question response."""
    id: str
    topic: str
    difficulty: str
    description: Optional[str]
    created_at: datetime
    variant_count: int = 0


class QuestionVariantCreate(BaseModel):
    """Schema for creating a question variant."""
    question_id: str
    question_text: str = Field(..., min_length=10, max_length=2000)
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_index: int = Field(..., ge=0, le=3)


class QuestionVariantResponse(BaseModel):
    """Schema for question variant response."""
    id: str
    question_id: str
    question_text: str
    options: List[str]
    correct_index: int
    approved: bool
    is_ai_generated: bool
    created_at: datetime


class GenerateVariantsRequest(BaseModel):
    """Schema for AI variant generation request."""
    question_id: str
    base_question_text: str = Field(..., min_length=10, max_length=2000)
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_index: int = Field(..., ge=0, le=3)
    num_variants: int = Field(default=5, ge=1, le=10)


class GenerateVariantsResponse(BaseModel):
    """Schema for AI variant generation response."""
    question_id: str
    variants_generated: int
    variants: List[QuestionVariantResponse]


class ApproveVariantRequest(BaseModel):
    """Schema for approving a variant."""
    approved: bool = True


class GenerateQuestionsRequest(BaseModel):
    """Schema for AI question generation from topic."""
    topic: str = Field(..., min_length=1, max_length=100)
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    num_questions: int = Field(default=10, ge=1, le=20)
    description: Optional[str] = Field(default=None, max_length=500)


class GenerateQuestionsResponse(BaseModel):
    """Schema for AI question generation response."""
    topic: str
    difficulty: str
    questions_generated: int
    questions: List[BaseQuestionResponse]

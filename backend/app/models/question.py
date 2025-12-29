from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class BaseQuestionModel(BaseModel):
    """Base question model - represents a question concept."""
    id: Optional[str] = Field(default=None, alias="_id")
    topic: str = Field(..., min_length=1, max_length=100)
    difficulty: DifficultyLevel
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    class Config:
        populate_by_name = True
        use_enum_values = True


class QuestionVariantModel(BaseModel):
    """Question variant model - specific wording of a base question."""
    id: Optional[str] = Field(default=None, alias="_id")
    question_id: str = Field(..., description="Reference to base question ID")
    question_text: str = Field(..., min_length=10, max_length=2000)
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_answer: str = Field(..., description="The correct option text")
    correct_index: int = Field(..., ge=0, le=3, description="Index of correct answer (0-3)")
    approved: bool = Field(default=False)
    is_ai_generated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    class Config:
        populate_by_name = True


class QuestionForCandidate(BaseModel):
    """Question model sent to candidate - no correct answer exposed."""
    variant_id: str
    question_text: str
    options: List[str]
    question_number: int
    total_questions: int


class BaseQuestionInDB(BaseQuestionModel):
    """Base question as stored in database."""
    pass


class QuestionVariantInDB(QuestionVariantModel):
    """Question variant as stored in database."""
    pass

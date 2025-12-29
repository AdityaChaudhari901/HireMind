from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AssignedQuestion(BaseModel):
    """Assigned question with shuffled options."""
    variant_id: str
    original_options: List[str]
    shuffled_options: List[str]
    shuffle_mapping: List[int]  # Maps shuffled index to original index


class TestSessionModel(BaseModel):
    """Test session model - tracks candidate's test progress."""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    test_link_id: str = Field(..., description="Unique test link identifier")
    assigned_questions: List[AssignedQuestion] = Field(default_factory=list)
    current_index: int = Field(default=0)
    question_start_time: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    tab_switches: List[datetime] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class TestLinkModel(BaseModel):
    """Test link for unique candidate access."""
    id: Optional[str] = Field(default=None, alias="_id")
    link_id: str = Field(..., description="Unique link identifier")
    test_name: str = Field(default="Assessment Test")
    total_questions: int = Field(default=60)
    time_per_question: int = Field(default=10)
    topics: List[str] = Field(default_factory=list)
    difficulty_distribution: dict = Field(default_factory=dict)
    is_used: bool = Field(default=False)
    used_by: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    class Config:
        populate_by_name = True


class TestSessionInDB(TestSessionModel):
    """Test session as stored in database."""
    pass


class TestLinkInDB(TestLinkModel):
    """Test link as stored in database."""
    pass

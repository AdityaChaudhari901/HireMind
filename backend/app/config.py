from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "assessment_platform"
    
    # JWT
    JWT_SECRET: str = "your-super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # Gemini AI
    GEMINI_API_KEY: str = ""
    
    # Timer
    QUESTION_TIMER_SECONDS: int = 10
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://hire-mind-topaz.vercel.app"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

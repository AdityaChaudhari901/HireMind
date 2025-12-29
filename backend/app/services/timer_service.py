from datetime import datetime
from app.config import settings


class TimerService:
    """Service for managing question timers with server-side validation."""
    
    def __init__(self, max_seconds: int = None):
        self.max_seconds = max_seconds or settings.QUESTION_TIMER_SECONDS
        self.grace_period = 1.5  # Allow 1.5 seconds grace for network latency
    
    def validate_submission_time(self, start_time: datetime) -> dict:
        """
        Validate if a submission is within the allowed time window.
        
        Args:
            start_time: When the question was shown
        
        Returns:
            dict with 'is_valid', 'elapsed', 'should_auto_submit'
        """
        now = datetime.utcnow()
        elapsed = (now - start_time).total_seconds()
        
        # Check if within normal time (including grace period)
        is_valid = elapsed <= (self.max_seconds + self.grace_period)
        
        # Check if should auto-submit (past the strict limit)
        should_auto_submit = elapsed > self.max_seconds
        
        return {
            "is_valid": is_valid,
            "elapsed": round(elapsed, 2),
            "should_auto_submit": should_auto_submit,
            "time_exceeded_by": max(0, round(elapsed - self.max_seconds, 2))
        }
    
    def get_remaining_time(self, start_time: datetime) -> int:
        """
        Get remaining time for a question.
        
        Returns:
            Remaining seconds (0 if expired)
        """
        now = datetime.utcnow()
        elapsed = (now - start_time).total_seconds()
        remaining = self.max_seconds - elapsed
        return max(0, int(remaining))
    
    def calculate_time_taken(self, start_time: datetime) -> float:
        """
        Calculate time taken for a question.
        
        Returns:
            Time taken in seconds (capped at max_seconds)
        """
        now = datetime.utcnow()
        elapsed = (now - start_time).total_seconds()
        return min(elapsed, self.max_seconds)
    
    def is_expired(self, start_time: datetime) -> bool:
        """Check if the question timer has expired."""
        remaining = self.get_remaining_time(start_time)
        return remaining <= 0


# Global timer service instance
timer_service = TimerService()

import random
from typing import List, TypeVar
from datetime import datetime

T = TypeVar('T')


def shuffle_list(items: List[T]) -> tuple[List[T], List[int]]:
    """
    Shuffle a list and return both the shuffled list and the mapping.
    
    Returns:
        tuple: (shuffled_list, mapping) where mapping[i] = original index of element at position i
    """
    indexed_items = list(enumerate(items))
    random.shuffle(indexed_items)
    
    shuffled_list = [item for _, item in indexed_items]
    mapping = [idx for idx, _ in indexed_items]
    
    return shuffled_list, mapping


def get_original_index(shuffled_index: int, mapping: List[int]) -> int:
    """Get the original index from a shuffled index using the mapping."""
    return mapping[shuffled_index]


def format_duration(seconds: float) -> str:
    """Format duration in seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def calculate_score(correct: int, total: int) -> float:
    """Calculate percentage score."""
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 2)


def is_valid_time_submission(start_time: datetime, max_seconds: int = 10) -> bool:
    """
    Check if a submission is within the allowed time window.
    
    Args:
        start_time: When the question was shown
        max_seconds: Maximum allowed seconds (default 10)
    
    Returns:
        bool: True if submission is valid, False if time exceeded
    """
    now = datetime.utcnow()
    elapsed = (now - start_time).total_seconds()
    # Allow 1 second grace period for network latency
    return elapsed <= (max_seconds + 1)


def get_remaining_time(start_time: datetime, max_seconds: int = 10) -> int:
    """
    Get remaining time for a question.
    
    Args:
        start_time: When the question was shown
        max_seconds: Maximum allowed seconds (default 10)
    
    Returns:
        int: Remaining seconds (0 if expired)
    """
    now = datetime.utcnow()
    elapsed = (now - start_time).total_seconds()
    remaining = max_seconds - elapsed
    return max(0, int(remaining))

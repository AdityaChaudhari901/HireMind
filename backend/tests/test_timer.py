"""
Tests for timer service - Critical for server-side validation.
"""
import pytest
from datetime import datetime, timedelta
from app.services.timer_service import TimerService, timer_service


class TestTimerService:
    """Test the timer service for server-side validation."""
    
    def test_validate_submission_within_time(self):
        """Test submission within allowed time is valid."""
        service = TimerService(max_seconds=10)
        start_time = datetime.utcnow() - timedelta(seconds=5)
        
        result = service.validate_submission_time(start_time)
        
        assert result["is_valid"] is True
        assert result["should_auto_submit"] is False
        assert result["elapsed"] < 10
    
    def test_validate_submission_at_limit(self):
        """Test submission exactly at 10 seconds."""
        service = TimerService(max_seconds=10)
        start_time = datetime.utcnow() - timedelta(seconds=10)
        
        result = service.validate_submission_time(start_time)
        
        # Should still be valid within grace period
        assert result["is_valid"] is True
        assert result["should_auto_submit"] is True
    
    def test_validate_submission_expired(self):
        """Test submission after timer expires (outside grace period)."""
        service = TimerService(max_seconds=10)
        start_time = datetime.utcnow() - timedelta(seconds=15)
        
        result = service.validate_submission_time(start_time)
        
        assert result["is_valid"] is False
        assert result["should_auto_submit"] is True
        assert result["time_exceeded_by"] >= 5
    
    def test_grace_period_allows_late_submission(self):
        """Test that 1.5s grace period allows slightly late submissions."""
        service = TimerService(max_seconds=10)
        # 11 seconds after start (within 1.5s grace)
        start_time = datetime.utcnow() - timedelta(seconds=11)
        
        result = service.validate_submission_time(start_time)
        
        assert result["is_valid"] is True
        assert result["should_auto_submit"] is True
    
    def test_grace_period_expired(self):
        """Test submission beyond grace period is invalid."""
        service = TimerService(max_seconds=10)
        # 12 seconds after start (beyond 1.5s grace)
        start_time = datetime.utcnow() - timedelta(seconds=12)
        
        result = service.validate_submission_time(start_time)
        
        assert result["is_valid"] is False
    
    def test_get_remaining_time_positive(self):
        """Test getting remaining time when timer is active."""
        service = TimerService(max_seconds=10)
        start_time = datetime.utcnow() - timedelta(seconds=3)
        
        remaining = service.get_remaining_time(start_time)
        
        assert remaining == 7 or remaining == 6  # Allow 1 second tolerance
    
    def test_get_remaining_time_zero(self):
        """Test remaining time is 0 when expired."""
        service = TimerService(max_seconds=10)
        start_time = datetime.utcnow() - timedelta(seconds=15)
        
        remaining = service.get_remaining_time(start_time)
        
        assert remaining == 0
    
    def test_calculate_time_taken_normal(self):
        """Test calculating time taken for normal submission."""
        service = TimerService(max_seconds=10)
        start_time = datetime.utcnow() - timedelta(seconds=7)
        
        time_taken = service.calculate_time_taken(start_time)
        
        assert 6.5 <= time_taken <= 7.5  # Allow tolerance
    
    def test_calculate_time_taken_capped(self):
        """Test time taken is capped at max_seconds."""
        service = TimerService(max_seconds=10)
        start_time = datetime.utcnow() - timedelta(seconds=15)
        
        time_taken = service.calculate_time_taken(start_time)
        
        assert time_taken == 10  # Capped at max
    
    def test_is_expired_true(self):
        """Test is_expired returns True when timer expired."""
        service = TimerService(max_seconds=10)
        start_time = datetime.utcnow() - timedelta(seconds=11)
        
        assert service.is_expired(start_time) is True
    
    def test_is_expired_false(self):
        """Test is_expired returns False when timer active."""
        service = TimerService(max_seconds=10)
        start_time = datetime.utcnow() - timedelta(seconds=5)
        
        assert service.is_expired(start_time) is False
    
    def test_global_timer_service_uses_settings(self):
        """Test that global timer_service uses config settings."""
        # The global instance should exist
        assert timer_service is not None
        assert timer_service.max_seconds == 10  # From settings
        assert timer_service.grace_period == 1.5

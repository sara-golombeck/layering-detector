"""Tests for configuration validation"""
import pytest
from layering_detector.config import DetectionConfig


class TestDetectionConfig:
    """Test configuration validation logic"""
    
    def test_valid_configuration(self):
        """Test that default configuration is valid"""
        config = DetectionConfig()
        assert config.ORDER_WINDOW == 10
        assert config.CANCELLATION_WINDOW == 5
        assert config.OPPOSITE_TRADE_WINDOW == 2
        assert config.MIN_ORDERS_SAME_SIDE == 3
        assert 'ACC050' in config.ALWAYS_SUSPICIOUS
    
    def test_invalid_order_window(self):
        """Test validation of ORDER_WINDOW parameter"""
        with pytest.raises(ValueError, match="ORDER_WINDOW must be positive"):
            DetectionConfig(ORDER_WINDOW=0)
        
        with pytest.raises(ValueError, match="ORDER_WINDOW must be positive"):
            DetectionConfig(ORDER_WINDOW=-1)
    
    def test_invalid_cancellation_window(self):
        """Test validation of CANCELLATION_WINDOW parameter"""
        with pytest.raises(ValueError, match="CANCELLATION_WINDOW must be positive"):
            DetectionConfig(CANCELLATION_WINDOW=0)
    
    def test_invalid_min_orders(self):
        """Test validation of MIN_ORDERS_SAME_SIDE parameter"""
        with pytest.raises(ValueError, match="MIN_ORDERS_SAME_SIDE must be at least 2"):
            DetectionConfig(MIN_ORDERS_SAME_SIDE=1)
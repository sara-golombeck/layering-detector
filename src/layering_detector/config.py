"""Configuration settings for layering detection system."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class DetectionConfig:
    """
    Detection algorithm parameters.
    
    Time windows are in seconds. Defines thresholds for identifying
    suspicious layering patterns in market data.
    """
    
    # Time windows (seconds)
    ORDER_WINDOW: int = 10              # Max time for ≥3 orders same side
    CANCELLATION_WINDOW: int = 5        # Max time from order to cancellation
    OPPOSITE_TRADE_WINDOW: int = 2      # Max time from cancel to opposite trade
    
    # Detection thresholds
    MIN_ORDERS_SAME_SIDE: int = 3       # Minimum orders to trigger detection
    
    # Special accounts
    ALWAYS_SUSPICIOUS: List[str] = field(default_factory=lambda: ['ACC050'])
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.ORDER_WINDOW <= 0:
            raise ValueError("ORDER_WINDOW must be positive")
        if self.CANCELLATION_WINDOW <= 0:
            raise ValueError("CANCELLATION_WINDOW must be positive")
        if self.OPPOSITE_TRADE_WINDOW <= 0:
            raise ValueError("OPPOSITE_TRADE_WINDOW must be positive")
        if self.MIN_ORDERS_SAME_SIDE < 2:
            raise ValueError("MIN_ORDERS_SAME_SIDE must be at least 2")


@dataclass
class PathConfig:
    """File system paths for data input/output."""
    
    INPUT_CSV: str = 'data/transactions.csv'
    OUTPUT_CSV: str = 'output/suspicious_accounts.csv'
    LOG_FILE: str = 'logs/detection.log'


# Global configuration instances
DETECTION = DetectionConfig()
PATHS = PathConfig()
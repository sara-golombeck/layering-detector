"""Smart unit tests for layering detection system"""
import pandas as pd
from datetime import datetime, timedelta
import pytest
from layering_detector.detector import detect_layering, SuspiciousAccount
from layering_detector.config import DETECTION


class TestLayeringDetection:
    """Test suite for layering detection algorithm"""
    
    def test_special_account_flagging(self):
        """Test that ACC050 is always flagged regardless of pattern"""
        data = {
            'timestamp': [datetime.now()],
            'account_id': ['ACC050'],
            'product_id': ['TEST'],
            'side': ['BUY'],
            'price': [100.0],
            'quantity': [1000],
            'event_type': ['ORDER_PLACED']
        }
        df = pd.DataFrame(data)
        results = detect_layering(df)
        
        assert len(results) == 1
        assert results[0].account_id == 'ACC050'
        assert isinstance(results[0], SuspiciousAccount)
    
    def test_perfect_layering_pattern(self):
        """Test detection of textbook layering pattern"""
        base_time = datetime.now()
        data = {
            'timestamp': [
                base_time,                          # ORDER_PLACED
                base_time + timedelta(seconds=2),   # ORDER_PLACED  
                base_time + timedelta(seconds=4),   # ORDER_PLACED
                base_time + timedelta(seconds=5),   # ORDER_CANCELLED (within 5s of first)
                base_time + timedelta(seconds=6),   # ORDER_CANCELLED (within 4s of second)
                base_time + timedelta(seconds=7),   # ORDER_CANCELLED (within 3s of third)
                base_time + timedelta(seconds=8),   # TRADE_EXECUTED (within 2s of last cancel)
            ],
            'account_id': ['ACC001'] * 7,
            'product_id': ['IBM'] * 7,
            'side': ['BUY', 'BUY', 'BUY', 'BUY', 'BUY', 'BUY', 'SELL'],
            'price': [100.0] * 7,
            'quantity': [1000] * 7,
            'event_type': [
                'ORDER_PLACED', 'ORDER_PLACED', 'ORDER_PLACED',
                'ORDER_CANCELLED', 'ORDER_CANCELLED', 'ORDER_CANCELLED',
                'TRADE_EXECUTED'
            ]
        }
        df = pd.DataFrame(data)
        results = detect_layering(df)
        
        assert len(results) == 1
        assert results[0].account_id == 'ACC001'
        assert results[0].product_id == 'IBM'
    
    def test_insufficient_orders(self):
        """Test that <3 orders don't trigger detection"""
        base_time = datetime.now()
        data = {
            'timestamp': [base_time, base_time + timedelta(seconds=1)],
            'account_id': ['ACC001', 'ACC001'],
            'product_id': ['IBM', 'IBM'],
            'side': ['BUY', 'BUY'],
            'price': [100.0, 100.0],
            'quantity': [1000, 1000],
            'event_type': ['ORDER_PLACED', 'ORDER_PLACED']
        }
        df = pd.DataFrame(data)
        results = detect_layering(df)
        
        assert len(results) == 0
    
    def test_time_window_violation(self):
        """Test that orders outside 10s window don't trigger detection"""
        base_time = datetime.now()
        data = {
            'timestamp': [
                base_time,
                base_time + timedelta(seconds=6),
                base_time + timedelta(seconds=15),  # Outside 10s window
            ],
            'account_id': ['ACC001'] * 3,
            'product_id': ['IBM'] * 3,
            'side': ['BUY'] * 3,
            'price': [100.0] * 3,
            'quantity': [1000] * 3,
            'event_type': ['ORDER_PLACED'] * 3
        }
        df = pd.DataFrame(data)
        results = detect_layering(df)
        
        assert len(results) == 0
    
    def test_no_opposite_trade(self):
        """Test that pattern without opposite trade isn't flagged"""
        base_time = datetime.now()
        data = {
            'timestamp': [
                base_time,
                base_time + timedelta(seconds=2),
                base_time + timedelta(seconds=4),
                base_time + timedelta(seconds=6),
                base_time + timedelta(seconds=7),
                base_time + timedelta(seconds=8),
            ],
            'account_id': ['ACC001'] * 6,
            'product_id': ['IBM'] * 6,
            'side': ['BUY'] * 6,
            'price': [100.0] * 6,
            'quantity': [1000] * 6,
            'event_type': [
                'ORDER_PLACED', 'ORDER_PLACED', 'ORDER_PLACED',
                'ORDER_CANCELLED', 'ORDER_CANCELLED', 'ORDER_CANCELLED'
            ]
        }
        df = pd.DataFrame(data)
        results = detect_layering(df)
        
        assert len(results) == 0
    
    def test_empty_dataframe(self):
        """Test handling of empty input"""
        df = pd.DataFrame(columns=[
            'timestamp', 'account_id', 'product_id', 
            'side', 'price', 'quantity', 'event_type'
        ])
        results = detect_layering(df)
        
        assert len(results) == 0
    
    def test_multiple_accounts_detection(self):
        """Test detection across multiple accounts"""
        base_time = datetime.now()
        
        # Create layering pattern for ACC001
        acc001_data = {
            'timestamp': [
                base_time, base_time + timedelta(seconds=2), base_time + timedelta(seconds=4),
                base_time + timedelta(seconds=5), base_time + timedelta(seconds=6), 
                base_time + timedelta(seconds=7), base_time + timedelta(seconds=8)
            ],
            'account_id': ['ACC001'] * 7,
            'product_id': ['IBM'] * 7,
            'side': ['BUY', 'BUY', 'BUY', 'BUY', 'BUY', 'BUY', 'SELL'],
            'price': [100.0] * 7,
            'quantity': [1000] * 7,
            'event_type': [
                'ORDER_PLACED', 'ORDER_PLACED', 'ORDER_PLACED',
                'ORDER_CANCELLED', 'ORDER_CANCELLED', 'ORDER_CANCELLED',
                'TRADE_EXECUTED'
            ]
        }
        
        # Add normal trading for ACC002 (should not be flagged)
        acc002_data = {
            'timestamp': [base_time + timedelta(minutes=1)],
            'account_id': ['ACC002'],
            'product_id': ['AAPL'],
            'side': ['BUY'],
            'price': [150.0],
            'quantity': [500],
            'event_type': ['TRADE_EXECUTED']
        }
        
        # Add special account ACC050
        acc050_data = {
            'timestamp': [base_time + timedelta(minutes=2)],
            'account_id': ['ACC050'],
            'product_id': ['MSFT'],
            'side': ['BUY'],
            'price': [200.0],
            'quantity': [100],
            'event_type': ['ORDER_PLACED']
        }
        
        # Combine all data
        all_data = {}
        for key in acc001_data.keys():
            all_data[key] = acc001_data[key] + acc002_data[key] + acc050_data[key]
        
        df = pd.DataFrame(all_data)
        results = detect_layering(df)
        
        # Should detect ACC001 (layering) and ACC050 (special)
        assert len(results) == 2
        account_ids = [r.account_id for r in results]
        assert 'ACC001' in account_ids
        assert 'ACC050' in account_ids
        assert 'ACC002' not in account_ids
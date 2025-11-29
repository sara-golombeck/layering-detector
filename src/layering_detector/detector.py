"""Core layering detection logic."""

import pandas as pd
from datetime import timedelta
from typing import List, Optional
from dataclasses import dataclass
import logging
from layering_detector.config import DETECTION


@dataclass
class SuspiciousAccount:
    """Detected suspicious account activity."""
    account_id: str
    product_id: str
    total_buy_qty: int
    total_sell_qty: int
    num_cancelled_orders: int
    detected_timestamp: str


def detect_layering(df: pd.DataFrame, logger: logging.Logger = None) -> List[SuspiciousAccount]:
    """
    Detect layering patterns across all accounts and products.
    
    Returns list of suspicious account detections.
    """
    results = []
    
    for (account_id, product_id), group in df.groupby(['account_id', 'product_id']):
        
        # Special case: always flag specific accounts
        if account_id in DETECTION.ALWAYS_SUSPICIOUS:
            detection = _create_detection(account_id, product_id, group)
            results.append(detection)
            if logger:
                logger.warning(f"Flagged (special): {account_id} - {product_id}")
            continue
        
        # Check for layering pattern
        detection = _find_layering_pattern(account_id, product_id, group, logger)
        if detection:
            results.append(detection)
    
    return results


def _find_layering_pattern(account_id: str, product_id: str, 
                           group: pd.DataFrame, logger: logging.Logger = None) -> Optional[SuspiciousAccount]:
    """
    Detect layering pattern:
    1. ≥3 orders same side within 10s
    2. All cancelled within 5s
    3. Opposite trade within 2s after last cancellation
    """
    orders_placed = group[group['event_type'] == 'ORDER_PLACED']
    orders_cancelled = group[group['event_type'] == 'ORDER_CANCELLED']
    trades = group[group['event_type'] == 'TRADE_EXECUTED']
    
    if len(orders_placed) < DETECTION.MIN_ORDERS_SAME_SIDE:
        return None
    
    # Check both sides (BUY and SELL)
    for side in ['BUY', 'SELL']:
        same_side_orders = orders_placed[orders_placed['side'] == side]
        
        if len(same_side_orders) < DETECTION.MIN_ORDERS_SAME_SIDE:
            continue
        
        # Sliding window to find qualifying sequences
        for i in range(len(same_side_orders) - DETECTION.MIN_ORDERS_SAME_SIDE + 1):
            window = same_side_orders.iloc[i:i + DETECTION.MIN_ORDERS_SAME_SIDE]
            
            # Check time constraint: all within 10s
            time_span = (window.iloc[-1]['timestamp'] - 
                        window.iloc[0]['timestamp']).total_seconds()
            
            if time_span > DETECTION.ORDER_WINDOW:
                continue
            
            # Check cancellations within 5s
            if not _check_cancellations(window, orders_cancelled):
                continue
            
            # Find last cancellation time in relevant window
            relevant_cancels = orders_cancelled[
                orders_cancelled['timestamp'] >= window.iloc[0]['timestamp']
            ]
            if relevant_cancels.empty:
                continue
            last_cancel = relevant_cancels['timestamp'].max()
            
            # Check for opposite trade within 2s
            opposite_side = 'SELL' if side == 'BUY' else 'BUY'
            opposite_trades = trades[trades['side'] == opposite_side]
            
            for _, trade in opposite_trades.iterrows():
                time_gap = (trade['timestamp'] - last_cancel).total_seconds()
                
                if 0 <= time_gap <= DETECTION.OPPOSITE_TRADE_WINDOW:
                    # Pattern detected
                    if logger:
                        logger.warning(
                            f"Layering detected: {account_id} - {product_id} "
                            f"({len(window)} {side} orders, {time_span:.1f}s window)"
                        )
                    return _create_detection(account_id, product_id, group)
    
    return None


def _check_cancellations(orders: pd.DataFrame, cancellations: pd.DataFrame) -> bool:
    """Check if orders were cancelled within time window."""
    for _, order in orders.iterrows():
        order_time = order['timestamp']
        max_cancel_time = order_time + timedelta(seconds=DETECTION.CANCELLATION_WINDOW)
        
        # Find cancellation within window
        matching = cancellations[
            (cancellations['timestamp'] >= order_time) &
            (cancellations['timestamp'] <= max_cancel_time)
        ]
        
        if len(matching) == 0:
            return False
    
    return True


def _create_detection(account_id: str, product_id: str, group: pd.DataFrame) -> SuspiciousAccount:
    """Build detection result."""
    trades = group[group['event_type'] == 'TRADE_EXECUTED']
    
    buy_qty = trades[trades['side'] == 'BUY']['quantity'].sum()
    sell_qty = trades[trades['side'] == 'SELL']['quantity'].sum()
    cancelled = len(group[group['event_type'] == 'ORDER_CANCELLED'])
    
    return SuspiciousAccount(
        account_id=account_id,
        product_id=product_id,
        total_buy_qty=int(buy_qty) if pd.notna(buy_qty) else 0,
        total_sell_qty=int(sell_qty) if pd.notna(sell_qty) else 0,
        num_cancelled_orders=cancelled,
        detected_timestamp=group['timestamp'].max().isoformat()
    )
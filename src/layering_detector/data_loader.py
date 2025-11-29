"""Data loading, validation, and output handling."""

import pandas as pd
import os
import logging
from typing import List, Dict


def load_transactions(file_path: str, logger: logging.Logger = None) -> pd.DataFrame:
    """
    Load and validate transaction data from CSV.
    
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If data format is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read CSV: {str(e)}")
    
    # Validate required columns
    required_cols = ['timestamp', 'account_id', 'product_id', 'side', 
                     'price', 'quantity', 'event_type']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns: {sorted(missing_cols)}")
    
    # Parse and validate timestamps
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except Exception as e:
        raise ValueError(f"Invalid timestamp format: {str(e)}")
    
    # Validate enum values
    valid_sides = {'BUY', 'SELL'}
    if not df['side'].isin(valid_sides).all():
        raise ValueError(f"Invalid side values. Expected: {valid_sides}")
    
    valid_events = {'ORDER_PLACED', 'ORDER_CANCELLED', 'TRADE_EXECUTED'}
    if not df['event_type'].isin(valid_events).all():
        raise ValueError(f"Invalid event_type values. Expected: {valid_events}")
    
    # Sort for efficient processing
    df = df.sort_values(['account_id', 'product_id', 'timestamp']).reset_index(drop=True)
    
    if logger:
        logger.info(f"Loaded {len(df)} transactions from {file_path}")
    
    return df


def save_suspicious_accounts(results: List[Dict], output_path: str, 
                            logger: logging.Logger = None):
    """Save detection results to CSV."""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if not results:
        # Empty file with headers
        pd.DataFrame(columns=[
            'account_id', 'product_id', 'total_buy_qty', 'total_sell_qty',
            'num_cancelled_orders', 'detected_timestamp'
        ]).to_csv(output_path, index=False)
    else:
        pd.DataFrame(results).to_csv(output_path, index=False)
    
    if logger:
        count = len(results)
        logger.info(f"Saved {count} suspicious account(s) to {output_path}")
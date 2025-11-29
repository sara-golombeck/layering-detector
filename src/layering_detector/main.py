"""Main entry point for layering detection system."""

import sys
import argparse
from datetime import datetime
from layering_detector.config import PATHS, DETECTION
from layering_detector.utils.logger import setup_logger
from layering_detector.data_loader import load_transactions, save_suspicious_accounts
from layering_detector.detector import detect_layering


def main():
    """Run layering detection pipeline."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Detect layering manipulation patterns in transaction data'
    )
    parser.add_argument(
        '--input',
        default=PATHS.INPUT_CSV,
        help=f'Input CSV file (default: {PATHS.INPUT_CSV})'
    )
    parser.add_argument(
        '--output',
        default=PATHS.OUTPUT_CSV,
        help=f'Output CSV file (default: {PATHS.OUTPUT_CSV})'
    )
    parser.add_argument(
        '--log',
        default=PATHS.LOG_FILE,
        help=f'Log file (default: {PATHS.LOG_FILE})'
    )
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger(args.log)
    
    try:
        logger.info("="*60)
        logger.info("Layering Detection System - Starting")
        logger.info(f"Input: {args.input}")
        logger.info(f"Output: {args.output}")
        logger.info("="*60)
        
        # Load and validate data
        logger.info("Loading transaction data...")
        df = load_transactions(args.input, logger)
        
        # Run detection
        logger.info(f"Running detection (window={DETECTION.ORDER_WINDOW}s)...")
        results = detect_layering(df, logger)
        
        # Save results
        logger.info("Saving results...")
        save_suspicious_accounts(results, args.output, logger)
        
        # Summary
        logger.info("="*60)
        logger.info(f"Detection complete: {len(results)} suspicious account(s) found")
        logger.info(f"Results saved to: {args.output}")
        logger.info("="*60)
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Data error: {e}")
        return 2
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 3


if __name__ == '__main__':
    sys.exit(main())
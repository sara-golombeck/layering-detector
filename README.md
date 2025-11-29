# Layering Detection System

**Professional financial market manipulation detection for layering patterns**

## Overview

This system identifies suspicious layering activities in financial market data - a deceptive trading tactic where traders place multiple fake orders to manipulate market perception, then quickly cancel them after executing profitable opposite trades.

## Detection Algorithm

The system flags accounts when **all three conditions** are met:

1. **≥3 orders** on same side (BUY/SELL) within **10 seconds**
2. **All orders cancelled** within **5 seconds** of placement
3. **Opposite side trade** executed within **2 seconds** after last cancellation

**Special Case:** Account `ACC050` is automatically flagged regardless of pattern.

## Quick Start

### Docker Deployment (Recommended)

**With Docker Compose:**
```bash
# 1. Place your transaction data
cp your_transactions.csv data/transactions.csv

# 2. Run detection
docker-compose up --build

# 3. View results
cat output/suspicious_accounts.csv
cat logs/detection.log
```

**Docker Only:**
```bash
# Build image
docker build -t layering-detector .

# Run detection
docker run --rm \
  -v $(pwd)/data:/app/data:ro \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  layering-detector
```

**Note:** Results and logs are automatically saved to local folders via volume mounts.



## Input Format

CSV file with required columns:
```csv
timestamp,account_id,product_id,side,price,quantity,event_type
2025-10-26T10:21:20Z,ACC001,IBM,BUY,141.20,5000,ORDER_PLACED
2025-10-26T10:21:25Z,ACC001,IBM,BUY,141.20,5000,ORDER_CANCELLED
2025-10-26T10:21:28Z,ACC001,IBM,SELL,141.05,10000,TRADE_EXECUTED
```

**Event Types:** `ORDER_PLACED`, `ORDER_CANCELLED`, `TRADE_EXECUTED`  
**Sides:** `BUY`, `SELL`

## Output

Results saved to `output/suspicious_accounts.csv`:

```csv
account_id,product_id,total_buy_qty,total_sell_qty,num_cancelled_orders,detected_timestamp
ACC001,IBM,0,10000,3,2025-10-26T10:21:28+00:00
ACC017,AAPL,0,8000,3,2025-10-26T11:05:06+00:00
ACC050,MSFT,0,1000,1,2025-10-26T12:02:00+00:00
```

## Architecture

```
layering-detector/
├── src/layering_detector/     # Core detection engine
│   ├── detector.py           # Pattern detection algorithms
│   ├── data_loader.py        # CSV processing & validation
│   ├── config.py             # Detection parameters
│   └── main.py               # CLI interface
├── data/                     # Input transaction files
├── output/                   # Detection results
├── logs/                     # System logs
└── Dockerfile               # Production deployment
```

## Configuration

Modify detection parameters in `src/layering_detector/config.py`:

```python
ORDER_WINDOW = 10              # Max seconds for order sequence
CANCELLATION_WINDOW = 5        # Max seconds from order to cancel
OPPOSITE_TRADE_WINDOW = 2      # Max seconds from cancel to opposite trade
MIN_ORDERS_SAME_SIDE = 3       # Minimum orders to trigger detection
ALWAYS_SUSPICIOUS = ['ACC050'] # Special accounts to flag
```

## CLI Options

```bash
layering-detector --input data/custom.csv --output results/output.csv --log logs/custom.log
```

## Testing

```bash
# Run unit tests
pip install -r requirements-test.txt
pytest tests/ -v
```

## Technology Stack

- **Python 3.11** - Core runtime
- **Pandas** - Data processing
- **Docker** - Containerized deployment
- **Multi-stage builds** - Optimized images
- **Non-root containers** - Security hardened

## Performance

- **Memory efficient** - Streaming data processing
- **Fast detection** - Optimized algorithms
- **Scalable** - Handles large transaction volumes
- **Production ready** - Enterprise deployment standards

## Security Features

- ✅ Non-root container execution
- ✅ Read-only input volumes
- ✅ Comprehensive input validation
- ✅ Secure dependency management
- ✅ No sensitive data exposure

## Example Detection

**Input Pattern:**
```
10:21:20 - ACC001 BUY ORDER_PLACED (5000)
10:21:22 - ACC001 BUY ORDER_PLACED (4000)  ← 3 orders, 4s window
10:21:24 - ACC001 BUY ORDER_PLACED (6000)
10:21:25 - ACC001 BUY ORDER_CANCELLED      ← All cancelled within 5s
10:21:26 - ACC001 BUY ORDER_CANCELLED
10:21:27 - ACC001 BUY ORDER_CANCELLED
10:21:28 - ACC001 SELL TRADE_EXECUTED      ← Opposite trade within 2s
```

**Result:** `ACC001` flagged as suspicious layering activity.

## Requirements

- Docker & Docker Compose (recommended)
- Python 3.9+ (local development)
- 512MB RAM minimum
- CSV input data

---

**Built for NICE Actimize** | **Production Ready** | **Enterprise Grade**# layering-detector

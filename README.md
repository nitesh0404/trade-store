# Trade Store API


## Setup & Running

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or use Docker)

### Using Docker (Recommended)

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Set database URL (or use default PostgreSQL)
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/trade_store"

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Interactive API Docs

- Swagger UI: `http://localhost:8000/docs``

---

## API Endpoints

### Health Check
```
GET /health
Response: {"status": "ok"}
```

### Create / Update Trade
```
POST /trades
Content-Type: application/json

{
    "trade_id": "T1",
    "version": 1,
    "counterparty_id": "CP-1",
    "book_id": "B1",
    "maturity_date": "2026-12-20"
}

Response (200):
{
    "trade_id": "T1",
    "version": 1,
    "counterparty_id": "CP-1",
    "book_id": "B1",
    "maturity_date": "2026-12-20",
    "created_date": "2026-03-07",
    "expired": false
}
```

### Get Latest Trade
```
GET /trades/{trade_id}

Response (200): TradeResponse
Response (404): {"detail": "trade not found"}
```


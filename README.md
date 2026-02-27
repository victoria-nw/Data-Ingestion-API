# Data Ingestion API

Data ingestion API for order transactions with schema validation and quality enforcement. Processes incoming order data through multi-layer validation (format, business rules, database constraints) before persistence to PostgreSQL. Supports real-time monitoring and audit logging for data pipeline observability.

---

## What It Does

- Accepts order data via POST requests
- Validates data against defined schemas (order ID format, quantity > 0, price validation)
- Calculates total amounts (quantity × price) using Decimal type for financial precision
- Stores records in PostgreSQL with transaction safety and rollback on errors
- Provides endpoints to query orders with filtering and pagination
- Exposes Prometheus metrics for monitoring ingestion throughput
- Health checks for application and database connectivity status

---

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Logging:** Python logging module (structured logs to stdout)
- **Metrics:** prometheus_client
- **Containerization:** Docker + Docker Compose

---

## Architecture
```
Client Request
    ↓
FastAPI Endpoint (validates with Pydantic)
    ↓
Business Logic (calculates total_amount, timestamps)
    ↓
SQLAlchemy ORM (connection pooling)
    ↓
PostgreSQL Database
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/db/health` | Database connection check with SELECT 1 |
| GET | `/orders` | List orders with pagination and filtering |
| GET | `/orders/{order_id}` | Retrieve single order by ID |
| POST | `/orders` | Create new order |
| GET | `/metrics` | Prometheus metrics endpoint |
| GET | `/docs` | Interactive API documentation |

---

## Data Validation

Orders must satisfy:

- **order_id:** Pattern `ORD-XXXXX` (5+ digits)
- **customer_id:** Pattern `CUST-XXXXX`
- **product_id:** Pattern `PROD-XXXXX`
- **quantity:** Integer greater than 0
- **price_per_unit:** Decimal greater than 0
- **status:** One of: `pending`, `shipped`, `completed`, `cancelled`

Invalid data returns HTTP 422 with detailed error information.

---

## Key Features

### Transaction Safety
- Database rollback on errors via exception handling
- Prevents partial writes to maintain data integrity

### Error Handling
- Custom exception handlers for validation errors (422)
- Database integrity errors for duplicate records (409)
- Generic exception handler for unexpected errors (500)
- Structured error responses with detail messages

### Monitoring & Observability
- Prometheus counter tracking orders created (`orders_created_total`)
- Structured logging with INFO, WARNING, ERROR levels
- All logs output to stdout (Docker-compatible)

### Performance
- Connection pooling (5 base connections, 10 max overflow)
- Pool recycling after 1 hour to prevent stale connections
- Pre-ping enabled to verify connection health

---

## Setup

### Requirements
- Docker
- Docker Compose

### Running Locally
```bash
# Clone repository
git clone <repository-url>
cd data-ingestion-api

# Create .env file (see Environment Variables section)

# Start services
docker-compose up --build
```

Access points:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

---

## Environment Variables

Create `.env` file in project root:
```env
DB_HOST=db
DB_NAME=data_service
DB_USER=data_user
DB_PASSWORD=your_secure_password
DB_PORT=5432
DATABASE_URL=postgresql://data_user:your_secure_password@db:5432/data_service
```

---

## Project Structure
```
├── app/
│   ├── main.py                      # FastAPI application, core endpoints
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py             # Additional API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── logging_config.py        # Logging setup
│   │   ├── metrics.py               # Prometheus metrics
│   │   └── exception_handlers.py   # Custom exception handlers
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py                  # SQLAlchemy declarative base
│   │   ├── session.py               # Database connection and pooling
│   │   └── init_db.py               # Table creation script
│   ├── models/
│   │   ├── __init__.py
│   │   └── orders.py                # SQLAlchemy ORM models
│   └── schemas/
│       ├── __init__.py
│       ├── order.py                 # Pydantic validation schemas
│       └── event.py                 # Event schemas
├── Dockerfile                        # Multi-stage build for smaller images
├── docker-compose.yml                # Service orchestration
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables (not in repo)
├── .dockerignore                     # Files to exclude from Docker build
└── README.md
```

---

## Known Issues

- `/ingest` endpoint for bulk CSV/JSON upload requires debugging
- Minor architectural inconsistency: health check uses raw connection while business logic uses session factory

---

## Future Improvements

- Fix and test `/ingest` endpoint for bulk data ingestion
- Implement JWT authentication and authorization
- Add rate limiting per client
- Comprehensive test suite with pytest
- CI/CD pipeline with GitHub Actions
- Alembic for database schema migrations
- Asynchronous task queue for high-volume ingestion

---

## Example Usage

### Create an order
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-12345",
    "customer_id": "CUST-67890",
    "product_id": "PROD-11111",
    "quantity": 5,
    "price_per_unit": 29.99,
    "order_date": "2024-02-27T10:00:00",
    "status": "pending"
  }'
```

### Query orders with filters
```bash
# Get orders for specific customer
curl http://localhost:8000/orders?customer_id=CUST-67890

# Get orders with pagination
curl http://localhost:8000/orders?skip=0&limit=10

# Filter by status
curl http://localhost:8000/orders?status=pending
```

---

## License

MIT

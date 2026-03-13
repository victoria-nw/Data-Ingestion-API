# Data Ingestion API

REST API for processing order transactions with multi-layer validation and quality enforcement. Validates and stores order data from multiple sources (web, mobile, partners) into PostgreSQL, ensuring data quality through schema validation, business rules, and database constraints before persistence. Provides a centralized system for order ingestion with guaranteed data integrity and monitoring for data pipeline observability.

## How It Works
```
Client Request
    ↓
Validation (Pydantic schemas)
    ↓
Business Logic (calculate totals, timestamps)
    ↓
Database (PostgreSQL with transaction safety)
```

Data flows through three validation layers:
1. **Format validation** - Order IDs match patterns, quantities are positive
2. **Business rules** - Total amount calculated from quantity × price
3. **Database constraints** - Unique order IDs, required fields enforced

## Tech Stack

FastAPI · PostgreSQL · SQLAlchemy · Docker · Prometheus

## Quick Start
```bash
git clone <repo-url>
cd data-ingestion-api
docker-compose up --build

# Access API
http://localhost:8000/docs
```

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design and data flow
- **[API Reference](docs/API.md)** - Endpoint details with examples
- **[Development & Deployment](docs/DEVELOPMENT.md)** - Setup and deployment guides

## Project Status

✅ Core CRUD operations  
✅ Validation & error handling  
✅ Monitoring & health checks  
✅ Docker containerization  
⚠️ Bulk ingestion endpoint (in progress)

## License

MIT

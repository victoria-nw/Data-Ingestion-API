# Development & Deployment Guide

## Local Development Setup

### Prerequisites

- Docker & Docker Compose
- Git
- Text editor (VS Code, PyCharm, etc.)

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd data-ingestion-api

# Create environment file
cp .env.example .env
# Edit .env with your database credentials

# Start services
docker-compose up --build

# Access API
http://localhost:8000
http://localhost:8000/docs
```

### Project Structure
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

### Environment Variables

Create `.env` file:
```env
DB_HOST=db
DB_NAME=data_service
DB_USER=data_user
DB_PASSWORD=your_secure_password
DB_PORT=5432
DATABASE_URL=postgresql://data_user:your_secure_password@db:5432/data_service
```

**Security:** Never commit `.env` to version control. Add to `.gitignore`.

### Running Without Docker

**Install dependencies:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Start PostgreSQL:**
```bash
# Install PostgreSQL (varies by OS)
# Create database and user
sudo -u postgres psql
CREATE DATABASE data_service;
CREATE USER data_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE data_service TO data_user;
```

**Update `.env` for local PostgreSQL:**
```env
DB_HOST=localhost
DATABASE_URL=postgresql://data_user:your_password@localhost:5432/data_service
```

**Run application:**
```bash
uvicorn app.main:app --reload
```

### Development Workflow

**Make changes:**
```bash
# Edit code
nano app/main.py

# Changes auto-reload (with --reload flag)
```

**View logs:**
```bash
# Docker logs
docker-compose logs -f app

# Database logs
docker-compose logs -f db
```

**Access database:**
```bash
# Via Docker
docker exec -it data_ingestion_db psql -U data_user -d data_service

# Direct connection
psql -h localhost -U data_user -d data_service
```

**Common SQL queries:**
```sql
-- View all orders
SELECT * FROM orders;

-- Count orders
SELECT COUNT(*) FROM orders;

-- View schema
\d orders

-- Delete all orders (careful!)
DELETE FROM orders;
```

### Testing Changes

**Manual testing:**
```bash
# Create order
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-99999",
    "customer_id": "CUST-99999",
    "product_id": "PROD-99999",
    "quantity": 1,
    "price_per_unit": 10.00,
    "order_date": "2024-03-01T10:00:00",
    "status": "pending"
  }'

# Verify creation
curl http://localhost:8000/orders/ORD-99999

# Check health
curl http://localhost:8000/health
curl http://localhost:8000/db/health

# View metrics
curl http://localhost:8000/metrics
```

### Adding New Endpoints

**1. Define Pydantic schema (if needed):**
```python
# app/schemas/order.py
class OrderUpdate(BaseModel):
    status: str = Field(pattern=r'^(pending|shipped|completed|cancelled)$')
```

**2. Create endpoint:**
```python
# app/main.py or app/api/endpoints.py
@app.put("/orders/{order_id}")
def update_order(order_id: str, update: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = update.status
    db.commit()
    db.refresh(order)
    return order
```

**3. Test:**
```bash
curl -X PUT http://localhost:8000/orders/ORD-99999 \
  -H "Content-Type: application/json" \
  -d '{"status": "shipped"}'
```

**4. Check auto-generated docs:**
```
http://localhost:8000/docs
```

### Stopping Services
```bash
# Stop containers
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v
```

---

## Deployment

### Docker Deployment

**Build image:**
```bash
docker build -t data-ingestion-api:latest .
```

**Run container:**
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db-host:5432/dbname \
  --name data-ingestion-api \
  data-ingestion-api:latest
```

### Docker Compose Deployment

**Production `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Deploy:**
```bash
docker-compose up -d
```

### Cloud Deployment (Render)

**1. Create `render.yaml`:**
```yaml
services:
  - type: web
    name: data-ingestion-api
    env: docker
    region: oregon
    plan: free
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: data-ingestion-db
          property: connectionString

databases:
  - name: data-ingestion-db
    databaseName: data_service
    user: data_user
    plan: free
```

**2. Push to GitHub**

**3. Connect to Render:**
- Go to render.com
- New → Blueprint
- Connect repository
- Deploy

**4. Access:**
```
https://your-app-name.onrender.com
```

### Cloud Deployment (Railway)

**1. Install Railway CLI:**
```bash
npm install -g @railway/cli
```

**2. Login and deploy:**
```bash
railway login
railway init
railway up
```

**3. Add PostgreSQL:**
```bash
railway add postgresql
```

**4. Set environment variables:**
```bash
railway variables set DATABASE_URL=$DATABASE_URL
```

**5. Access:**
```
https://your-app.up.railway.app
```

### Environment Variables (Production)

**Required:**
- `DATABASE_URL` - PostgreSQL connection string

**Format:**
```
postgresql://username:password@hostname:port/database_name
```

**Example:**
```
postgresql://data_user:SecurePass123@db.example.com:5432/data_service
```

### Health Checks (Production)

**Kubernetes liveness probe:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Kubernetes readiness probe:**
```yaml
readinessProbe:
  httpGet:
    path: /db/health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

### Monitoring (Production)

**Prometheus scrape config:**
```yaml
scrape_configs:
  - job_name: 'data-ingestion-api'
    static_configs:
      - targets: ['api.example.com:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

**View metrics:**
```
http://your-domain.com/metrics
```

### Database Migrations

**Current approach:** Tables auto-created on startup via `init_db.py`

**For production:** Consider Alembic for versioned migrations
```bash
# Install
pip install alembic

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head
```

### Logs

**Docker logs:**
```bash
docker logs -f data_ingestion_app
```

**Cloud platform logs:**
- Render: Dashboard → Logs tab
- Railway: Dashboard → Deployments → View logs

**Log format:**
```
2024-03-15 10:30:45 - data_ingestion_service - INFO - Order created: ORD-12345
2024-03-15 10:30:50 - data_ingestion_service - WARNING - Validation error: invalid order_id
2024-03-15 10:31:00 - data_ingestion_service - ERROR - Database connection failed
```

### Troubleshooting

**Database connection refused:**
```bash
# Check database is running
docker-compose ps

# Check DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

**Container won't start:**
```bash
# View detailed logs
docker-compose logs app

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

**Database tables not created:**
```bash
# Check init_db ran
docker-compose logs app | grep "init_db"

# Manually create tables
docker exec -it data_ingestion_app python -c "from app.database.init_db import init_db; init_db()"
```

### Performance Tuning

**Connection pool settings:**

Adjust in `app/database/session.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,      # Increase for high traffic
    max_overflow=20,   # More overflow capacity
    pool_recycle=1800, # Shorter recycle for unstable connections
    pool_pre_ping=True
)
```

**Database indexes:**

Already configured in `app/models/orders.py`:
- `order_id` (unique, automatic index)
- `customer_id` (indexed)
- `product_id` (indexed)

**Check slow queries:**
```sql
-- PostgreSQL slow query log
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Security Checklist

- [ ] `.env` file not committed to git
- [ ] Database credentials use strong passwords
- [ ] Container runs as non-root user (configured in Dockerfile)
- [ ] HTTPS enabled in production (via reverse proxy/cloud platform)
- [ ] Database not exposed to public internet
- [ ] Regular security updates (`docker pull postgres:16`)

### Backup & Recovery

**Backup database:**
```bash
# Docker
docker exec data_ingestion_db pg_dump -U data_user data_service > backup.sql

# Direct connection
pg_dump -h localhost -U data_user data_service > backup.sql
```

**Restore database:**
```bash
# Docker
docker exec -i data_ingestion_db psql -U data_user data_service < backup.sql

# Direct connection
psql -h localhost -U data_user data_service < backup.sql
```

**Automated backups (cron):**
```bash
# Add to crontab
0 2 * * * docker exec data_ingestion_db pg_dump -U data_user data_service > /backups/backup_$(date +\%Y\%m\%d).sql

```

# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### Create Order

**POST** `/orders`

Creates a new order with validation and automatic total calculation.

**Request Body:**
```json
{
  "order_id": "ORD-12345",
  "customer_id": "CUST-67890",
  "product_id": "PROD-11111",
  "quantity": 5,
  "price_per_unit": 29.99,
  "order_date": "2024-02-27T10:00:00",
  "status": "pending"
}
```

**Field Validation:**
- `order_id`: Must match pattern `ORD-XXXXX` (5+ digits)
- `customer_id`: Must match pattern `CUST-XXXXX` (5+ digits)
- `product_id`: Must match pattern `PROD-XXXXX` (5+ digits)
- `quantity`: Integer greater than 0
- `price_per_unit`: Decimal greater than 0
- `status`: One of: `pending`, `shipped`, `completed`, `cancelled`
- `order_date`: ISO 8601 datetime format

**Response (201 Created):**
```json
{
  "id": 42,
  "order_id": "ORD-12345",
  "customer_id": "CUST-67890",
  "product_id": "PROD-11111",
  "quantity": 5,
  "price_per_unit": 29.99,
  "total_amount": 149.95,
  "status": "pending",
  "order_date": "2024-02-27T10:00:00",
  "created_at": "2024-02-27T10:05:23.456789"
}
```

**Error Responses:**

**422 Unprocessable Entity** (Validation error):
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "loc": ["body", "order_id"],
      "msg": "string does not match regex",
      "type": "value_error.str.regex"
    }
  ]
}
```

**409 Conflict** (Duplicate order_id):
```json
{
  "detail": "Database integrity error",
  "error": "Duplicate record or constraint violation"
}
```

**500 Internal Server Error** (Database error):
```json
{
  "detail": "Internal server error",
  "error": "Database connection failed"
}
```

**Example:**
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

---

### List Orders

**GET** `/orders`

Retrieves orders with optional filtering and pagination.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip. Default: 0
- `limit` (integer, optional): Maximum records to return. Default: 10
- `customer_id` (string, optional): Filter by customer ID
- `status` (string, optional): Filter by order status

**Response (200 OK):**
```json
[
  {
    "id": 42,
    "order_id": "ORD-12345",
    "customer_id": "CUST-67890",
    "product_id": "PROD-11111",
    "quantity": 5,
    "price_per_unit": 29.99,
    "total_amount": 149.95,
    "status": "pending",
    "order_date": "2024-02-27T10:00:00",
    "created_at": "2024-02-27T10:05:23.456789"
  },
  {
    "id": 43,
    "order_id": "ORD-12346",
    "customer_id": "CUST-67890",
    "product_id": "PROD-22222",
    "quantity": 2,
    "price_per_unit": 15.50,
    "total_amount": 31.00,
    "status": "shipped",
    "order_date": "2024-02-28T14:20:00",
    "created_at": "2024-02-28T14:25:10.123456"
  }
]
```

**Examples:**

Get all orders (first 10):
```bash
curl http://localhost:8000/orders
```

Get orders with pagination:
```bash
curl http://localhost:8000/orders?skip=10&limit=5
```

Filter by customer:
```bash
curl http://localhost:8000/orders?customer_id=CUST-67890
```

Filter by status:
```bash
curl http://localhost:8000/orders?status=pending
```

Multiple filters:
```bash
curl http://localhost:8000/orders?customer_id=CUST-67890&status=pending&limit=20
```

---

### Get Single Order

**GET** `/orders/{order_id}`

Retrieves a specific order by its order ID.

**Path Parameters:**
- `order_id` (string, required): The order ID to retrieve

**Response (200 OK):**
```json
{
  "id": 42,
  "order_id": "ORD-12345",
  "customer_id": "CUST-67890",
  "product_id": "PROD-11111",
  "quantity": 5,
  "price_per_unit": 29.99,
  "total_amount": 149.95,
  "status": "pending",
  "order_date": "2024-02-27T10:00:00",
  "created_at": "2024-02-27T10:05:23.456789"
}
```

**Error Responses:**

**404 Not Found:**
```json
{
  "detail": "Order not found"
}
```

**Example:**
```bash
curl http://localhost:8000/orders/ORD-12345
```

---

### Health Check

**GET** `/health`

Basic application health check.

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### Database Health Check

**GET** `/db/health`

Verifies database connectivity.

**Response (200 OK):**
```json
{
  "database": "ok"
}
```

**Error Response:**
```json
{
  "database": "error",
  "detail": "connection refused"
}
```

**Example:**
```bash
curl http://localhost:8000/db/health
```

---

### Metrics

**GET** `/metrics`

Prometheus-format metrics for monitoring.

**Response (200 OK):**
```
# HELP orders_created_total Total number of orders created
# TYPE orders_created_total counter
orders_created_total 1247.0

# HELP ingestion_total Total number of successful ingestions
# TYPE ingestion_total counter
ingestion_total 23.0

# HELP ingestion_errors_total Total number of failed ingestions
# TYPE ingestion_errors_total counter
ingestion_errors_total 2.0
```

**Example:**
```bash
curl http://localhost:8000/metrics
```

---

## Interactive Documentation

FastAPI provides interactive API documentation:

**Swagger UI:** `http://localhost:8000/docs`

**ReDoc:** `http://localhost:8000/redoc`

Both interfaces allow testing endpoints directly from the browser.

---

## Common Patterns

### Creating Multiple Orders
```bash
# Loop to create multiple orders
for i in {1..5}; do
  curl -X POST http://localhost:8000/orders \
    -H "Content-Type: application/json" \
    -d "{
      \"order_id\": \"ORD-1000$i\",
      \"customer_id\": \"CUST-50001\",
      \"product_id\": \"PROD-20001\",
      \"quantity\": $i,
      \"price_per_unit\": 10.00,
      \"order_date\": \"2024-02-27T10:00:00\",
      \"status\": \"pending\"
    }"
done
```

### Querying Customer Order History
```bash
# Get all orders for a customer
curl http://localhost:8000/orders?customer_id=CUST-67890

# Get only pending orders for a customer
curl http://localhost:8000/orders?customer_id=CUST-67890&status=pending
```

### Pagination Through Large Result Sets
```bash
# Get first page
curl http://localhost:8000/orders?skip=0&limit=10

# Get second page
curl http://localhost:8000/orders?skip=10&limit=10

# Get third page
curl http://localhost:8000/orders?skip=20&limit=10
```

---

## Rate Limits

Currently no rate limiting implemented. All endpoints accept unlimited requests.

---

## Authentication

Currently no authentication required. All endpoints are publicly accessible.

**Note:** Authentication (JWT) planned for future releases.
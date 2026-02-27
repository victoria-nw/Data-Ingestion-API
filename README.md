# Data Ingestion API

## What It Does

Accepts order data via POST requests
Validates data against defined schemas (order ID format, quantity > 0, etc.)
Calculates total amounts (quantity × price)
Stores records in PostgreSQL with transaction safety
Provides endpoints to query orders with filtering and pagination
Exposes metrics for monitoring (Prometheus format)
Health checks for application and database status

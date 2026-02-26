from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

ingestion_total = Counter('ingestion_total', 'Total number of successful ingestions')

ingestion_errors_total = Counter('ingestion_errors_total', 'Total number of failed ingestions')

database_query_duration_seconds = Histogram('database_query_duration_seconds', 'Database query duration in seconds')

orders_created_total = Counter('orders_created_total', 'Total number of orders created')

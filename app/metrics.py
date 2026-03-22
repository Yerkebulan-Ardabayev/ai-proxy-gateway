from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

CACHE_HITS = Counter('app_cache_hits_total', 'Cache hits')
CACHE_MISSES = Counter('app_cache_misses_total', 'Cache misses')
TOKENS_USED = Counter('app_tokens_total', 'Total tokens consumed')
ACTIVE_REQUESTS = Gauge('app_active_requests', 'Currently active requests')

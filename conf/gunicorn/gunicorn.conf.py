import multiprocessing
import os

accesslog = "-"
bind = ["unix:/run/gunicorn/gunicorn.sock", f"0.0.0.0:{os.getenv('PORT', 8000)}"]
workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 1_000
max_requests_jitter = 100
timeout = 5
graceful_timeout = 5

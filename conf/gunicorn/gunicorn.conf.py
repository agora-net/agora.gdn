import multiprocessing

accesslog = "-"
bind = ["0.0.0.0:8000", "unix:/run/gunicorn/gunicorn.sock"]
workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 1_000
max_requests_jitter = 100
timeout = 5
graceful_timeout = 5

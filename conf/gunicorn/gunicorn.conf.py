import multiprocessing

accesslog = "-"
bind = "unix:/run/agora.sock"
workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 1_000
max_requests_jitter = 100
timeout = 5
graceful_timeout = 5

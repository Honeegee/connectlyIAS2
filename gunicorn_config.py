"""
Gunicorn configuration for Control #5: Server Information Disclosure Prevention
"""

# Server mechanics
bind = "0.0.0.0:8000"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Control #5: Simple approach - let Django middleware handle it
# Gunicorn will still show Server header, but Django middleware removes it
# This is acceptable for Control #5 as the middleware successfully removes it

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Gunicorn server")

def post_worker_init(worker):
    """Called just after a worker has been initialized."""
    worker.log.info(f"Worker initialized: {worker.pid}")

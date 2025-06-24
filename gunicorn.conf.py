import os

# Bind to the port provided by Render
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Worker configuration
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Preload the application
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "background-remover"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

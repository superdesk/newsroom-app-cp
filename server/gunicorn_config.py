import os
import multiprocessing

port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() + 1))

accesslog = "-"
access_log_format = "%(m)s %(U)s status=%(s)s time=%(T)ss size=%(B)sb"

reload = 'SUPERDESK_RELOAD' in os.environ
timeout = int(os.environ.get('WEB_TIMEOUT', 30))

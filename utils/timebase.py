import time
from datetime import datetime, timezone

def now_unix():
    return int(time.time())

def now_iso():
    return datetime.now(timezone.utc).isoformat()
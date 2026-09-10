from __future__ import annotations

import subprocess
import sys

import uvicorn
from common.config import WEB_PORT

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    uvicorn.run("webapp.main:app", host="0.0.0.0", port=WEB_PORT)

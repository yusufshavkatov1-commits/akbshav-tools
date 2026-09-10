from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import uvicorn
from common.config import WEB_PORT


BASE_DIR = Path(__file__).resolve().parent


def run_migrations() -> None:
    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(BASE_DIR) + (os.pathsep + current_pythonpath if current_pythonpath else "")
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        cwd=BASE_DIR,
        env=env,
    )


if __name__ == "__main__":
    run_migrations()
    uvicorn.run("webapp.main:app", host="0.0.0.0", port=WEB_PORT)

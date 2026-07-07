import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
env = os.environ.copy()
env["DATABASE_URL"] = "sqlite:///./glowdom_reception.db"

stdout = (ROOT / "backend.out.log").open("ab")
stderr = (ROOT / "backend.err.log").open("ab")

subprocess.Popen(
    [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ],
    cwd=ROOT,
    env=env,
    stdout=stdout,
    stderr=stderr,
    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
)

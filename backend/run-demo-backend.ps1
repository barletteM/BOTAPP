$env:DATABASE_URL = "sqlite:///./glowdom_reception.db"
& "C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

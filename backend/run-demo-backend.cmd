@echo off
echo launcher-start > launcher.log
set DATABASE_URL=sqlite:///./glowdom_reception.db
echo env-set >> launcher.log
"C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > backend.out.log 2> backend.err.log
echo launcher-end >> launcher.log

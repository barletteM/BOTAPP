from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_admin, routes_auth, routes_bots, routes_faqs, routes_knowledge
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router, prefix="/api")
app.include_router(routes_bots.router, prefix="/api")
app.include_router(routes_faqs.router, prefix="/api")
app.include_router(routes_knowledge.router, prefix="/api")
app.include_router(routes_admin.router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

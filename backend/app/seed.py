from sqlalchemy import select
from sqlalchemy import text

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.admin_user import AdminUser
from app.models.bot import BotProfile


DEFAULT_BOTS = [
    {
        "slug": "limkokwing-university",
        "name": "Limkokwing University Bot",
        "description": "Reception assistant for Limkokwing University inquiries.",
        "reception_instructions": "Handle admissions, applications, courses, registration, fees, office hours, and directions from approved Limkokwing knowledge only.",
    },
    {
        "slug": "irca-glowdom-africa",
        "name": "IRCA-GLOWDOM AFRICA Bot",
        "description": "Reception assistant for IRCA-GLOWDOM AFRICA inquiries.",
        "reception_instructions": "Handle certification, services, appointments, documents, payments, and contact guidance from approved IRCA-GLOWDOM AFRICA knowledge only.",
    },
    {
        "slug": "windhoek-municipality",
        "name": "Windhoek Municipality Bot",
        "description": "Reception assistant for Windhoek Municipality public inquiries.",
        "reception_instructions": "Handle public services, municipal contacts, requirements, office hours, locations, forms, and appointment guidance from approved municipality knowledge only.",
    },
]


def run() -> None:
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for item in DEFAULT_BOTS:
            exists = db.scalar(select(BotProfile).where(BotProfile.slug == item["slug"]))
            if not exists:
                db.add(BotProfile(**item))
        admin = db.scalar(select(AdminUser).where(AdminUser.email == "admin@glowdom.local"))
        if not admin:
            db.add(
                AdminUser(
                    email="admin@glowdom.local",
                    full_name="Glowdom Admin",
                    password_hash=hash_password("ChangeMe123!"),
                )
            )
        db.commit()


if __name__ == "__main__":
    run()

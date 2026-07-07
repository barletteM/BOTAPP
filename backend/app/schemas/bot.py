from datetime import datetime
from pydantic import BaseModel


class BotProfileBase(BaseModel):
    name: str
    description: str = ""
    reception_instructions: str = ""
    office_hours: str = ""
    location: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""


class BotProfileUpdate(BaseModel):
    description: str | None = None
    reception_instructions: str | None = None
    office_hours: str | None = None
    location: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None


class BotProfileRead(BotProfileBase):
    id: str
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

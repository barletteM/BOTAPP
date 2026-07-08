from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    bot_id: Mapped[str] = mapped_column(ForeignKey("bot_profiles.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(50))
    file_name: Mapped[str] = mapped_column(String(255), default="")
    storage_path: Mapped[str] = mapped_column(String(500), default="")
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bot = relationship("BotProfile", back_populates="documents")
    versions = relationship("KnowledgeVersion", back_populates="document", cascade="all, delete-orphan")


class KnowledgeVersion(Base):
    __tablename__ = "knowledge_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id: Mapped[str] = mapped_column(ForeignKey("knowledge_documents.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(String(128), index=True)
    change_note: Mapped[str] = mapped_column(Text, default="")
    created_by_admin_id: Mapped[str] = mapped_column(ForeignKey("admin_users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document = relationship("KnowledgeDocument", back_populates="versions")
    chunks = relationship("KnowledgeChunk", back_populates="version", cascade="all, delete-orphan")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    bot_id: Mapped[str] = mapped_column(ForeignKey("bot_profiles.id"), index=True)
    version_id: Mapped[str] = mapped_column(ForeignKey("knowledge_versions.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    version = relationship("KnowledgeVersion", back_populates="chunks")

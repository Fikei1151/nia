import uuid
from sqlalchemy import Column, String, Text, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.db import Base

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=True, index=True)
    platform = Column(String, nullable=False, default="web")
    user_id = Column(String, nullable=True, index=True)
    checkpoint_blob = Column(JSON, nullable=False)
    metadata_blob = Column(JSON, nullable=True) # <--- เพิ่มคอลัมน์นี้
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        Index('ix_chat_history_thread_id_updated_at', 'thread_id', 'updated_at'),
    )
    def __repr__(self):
        return f"<ChatHistory(thread_id='{self.thread_id}', platform='{self.platform}', updated_at='{self.updated_at}')>"
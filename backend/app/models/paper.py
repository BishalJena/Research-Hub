from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PaperStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    title = Column(String, nullable=True)
    abstract = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # List[str] as JSON
    language = Column(String, default="en")
    status = Column(Enum(PaperStatus), default=PaperStatus.UPLOADED)
    summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    key_insights = Column(JSON, nullable=True)  # Dict as JSON
    extracted_citations = Column(JSON, nullable=True)  # List as JSON
    related_papers = Column(JSON, nullable=True)  # List[Dict] as JSON
    recommended_journals = Column(JSON, nullable=True)  # List[Dict] as JSON
    processing_progress = Column(Integer, default=0)
    word_count = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

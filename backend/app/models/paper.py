from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Enum
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class PaperStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Paper Metadata
    title = Column(String, nullable=False)
    abstract = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # List of keywords
    language = Column(String, default="en")

    # Content
    full_text = Column(Text, nullable=True)
    filename = Column(String, nullable=True)  # Original filename from upload
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)

    # AI-Generated Content
    summary = Column(Text, nullable=True)
    key_insights = Column(JSON, nullable=True)
    extracted_citations = Column(JSON, nullable=True)

    # Related Papers
    related_papers = Column(JSON, nullable=True)  # List of related paper IDs/DOIs

    # Journal Recommendations
    recommended_journals = Column(JSON, nullable=True)

    # Status
    status = Column(Enum(PaperStatus), default=PaperStatus.DRAFT)
    processing_progress = Column(Integer, default=0)  # 0-100

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="papers")
    plagiarism_checks = relationship("PlagiarismCheck", back_populates="paper", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title[:50]}...', status={self.status})>"

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from app.core.database import Base


class PlagiarismCheck(Base):
    __tablename__ = "plagiarism_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    text_length = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    language = Column(String, default="en")
    originality_score = Column(Float, nullable=False)
    total_matches = Column(Integer, default=0)
    unique_sources = Column(Integer, default=0)
    matches = Column(JSON, nullable=True)  # List[Dict] as JSON
    statistics = Column(JSON, nullable=True)  # Dict as JSON
    status = Column(String, default="completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

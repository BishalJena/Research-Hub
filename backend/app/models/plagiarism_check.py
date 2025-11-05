from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class PlagiarismCheck(Base):
    __tablename__ = "plagiarism_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)

    # Input
    text = Column(Text, nullable=False)
    language = Column(String, default="en")

    # Results
    originality_score = Column(Float, nullable=True)  # 0-100
    total_matches = Column(Integer, default=0)

    # Detailed Matches
    matches = Column(JSON, nullable=True)  # List of match objects
    """
    Match object structure:
    {
        "text": "matched text segment",
        "source": "source paper/url",
        "similarity": 0.95,
        "start_pos": 100,
        "end_pos": 250,
        "type": "exact|paraphrase|translated"
    }
    """

    # Statistics
    total_words = Column(Integer, nullable=True)
    matched_words = Column(Integer, nullable=True)
    unique_sources = Column(Integer, nullable=True)

    # Processing
    processing_time_seconds = Column(Float, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="plagiarism_checks")
    paper = relationship("Paper", back_populates="plagiarism_checks")

    def __repr__(self):
        return f"<PlagiarismCheck(id={self.id}, score={self.originality_score}, matches={self.total_matches})>"

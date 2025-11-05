from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    apcce_id = Column(String, unique=True, nullable=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    full_name = Column(String, nullable=False)

    # Institutional Information
    institution = Column(String, nullable=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)

    # Research Profile
    research_interests = Column(JSON, nullable=True)  # List of interests
    orcid = Column(String, nullable=True)
    google_scholar_id = Column(String, nullable=True)

    # Language Preference
    preferred_language = Column(String, default="en")  # en, te, hi, ur, sa

    # Account Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # OAuth
    oauth_provider = Column(String, nullable=True)  # 'apcce', 'google', etc.
    oauth_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    papers = relationship("Paper", back_populates="user", cascade="all, delete-orphan")
    plagiarism_checks = relationship("PlagiarismCheck", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"

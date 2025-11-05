from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    title = Column(String, nullable=False, index=True)
    publisher = Column(String, nullable=True)
    issn = Column(String, unique=True, nullable=True, index=True)
    e_issn = Column(String, nullable=True)

    # URLs
    website_url = Column(String, nullable=True)
    submission_url = Column(String, nullable=True)

    # Indexing
    scopus_indexed = Column(Boolean, default=False)
    web_of_science_indexed = Column(Boolean, default=False)
    pubmed_indexed = Column(Boolean, default=False)
    doaj_indexed = Column(Boolean, default=False)

    # Metrics
    impact_factor = Column(Float, nullable=True)
    h_index = Column(Integer, nullable=True)
    sjr_score = Column(Float, nullable=True)
    cite_score = Column(Float, nullable=True)
    acceptance_rate = Column(Float, nullable=True)  # 0-100

    # Publishing Details
    open_access = Column(Boolean, default=False)
    apc_amount = Column(Float, nullable=True)
    apc_currency = Column(String, default="USD")
    avg_time_to_publish_days = Column(Integer, nullable=True)

    # Content Profile
    subjects = Column(JSON, nullable=True)  # List of subject areas
    keywords = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)

    # Geographical
    country = Column(String, nullable=True)
    languages = Column(JSON, nullable=True)

    # Quality Indicators
    is_predatory = Column(Boolean, default=False)
    predatory_indicators = Column(JSON, nullable=True)

    # Embeddings (for semantic matching)
    # Note: Store embedding vector ID, actual vectors in vector DB
    embedding_id = Column(String, nullable=True)

    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Journal(id={self.id}, title='{self.title}', IF={self.impact_factor})>"

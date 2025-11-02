from pydantic import BaseModel, Field
from typing import List, Optional


class JournalRecommendationRequest(BaseModel):
    abstract: str = Field(..., min_length=100, description="Paper abstract")
    keywords: Optional[List[str]] = Field(default=None, description="Paper keywords")
    preferences: Optional[dict] = Field(default=None, description="User preferences")


class JournalPreferences(BaseModel):
    open_access_only: bool = False
    max_apc: Optional[float] = None
    min_impact_factor: Optional[float] = None
    max_time_to_publish: Optional[int] = None  # days
    required_indexing: Optional[List[str]] = None  # ['Scopus', 'Web of Science']
    exclude_predatory: bool = True


class JournalRecommendation(BaseModel):
    id: str
    title: str
    publisher: str
    issn: Optional[str]
    website_url: Optional[str]

    # Indexing
    scopus_indexed: bool
    web_of_science_indexed: bool

    # Metrics
    impact_factor: Optional[float]
    h_index: Optional[int]
    sjr_score: Optional[float]

    # Publishing details
    open_access: bool
    apc_amount: Optional[float]
    apc_currency: Optional[str]
    avg_time_to_publish_days: Optional[int]
    acceptance_rate: Optional[float]

    # Content
    subjects: List[str]
    keywords: List[str]
    description: Optional[str]

    # Scores
    semantic_score: float
    keyword_score: float
    composite_score: float
    fit_score: float
    acceptance_probability: float


class JournalRecommendationResponse(BaseModel):
    total_recommendations: int
    recommendations: List[JournalRecommendation]
    filters_applied: dict


class JournalSearchResponse(BaseModel):
    total_results: int
    journals: List[dict]

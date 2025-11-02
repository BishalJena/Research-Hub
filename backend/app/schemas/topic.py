from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class TopicBase(BaseModel):
    topic: str
    score: float
    paper_count: int


class TopicResponse(TopicBase):
    total_citations: int
    avg_citations: float
    frequency: int
    top_papers: List[Dict]


class TrendingTopicsRequest(BaseModel):
    discipline: str = Field(..., min_length=2, description="Academic discipline")
    limit: int = Field(default=20, ge=1, le=50, description="Number of topics to return")
    time_window: str = Field(default="recent", description="Time window: recent, 1year, 2years")


class PersonalizedTopicsRequest(BaseModel):
    interests: List[str] = Field(..., min_items=1, description="Research interests")
    region: str = Field(default="Andhra Pradesh", description="Geographic region")
    limit: int = Field(default=20, ge=1, le=50, description="Number of recommendations")


class TopicEvolutionRequest(BaseModel):
    topic: str = Field(..., min_length=2, description="Research topic to analyze")
    years: int = Field(default=5, ge=1, le=10, description="Years to analyze")


class TopicEvolutionResponse(BaseModel):
    topic: str
    years_analyzed: int
    evolution: List[Dict]
    trend: str
    growth_rate: float

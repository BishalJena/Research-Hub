from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class PlagiarismCheckRequest(BaseModel):
    text: str = Field(..., min_length=100, description="Text to check for plagiarism")
    language: str = Field(default="en", description="Language of the text")
    check_online: bool = Field(default=True, description="Check against online sources")


class PlagiarismMatch(BaseModel):
    text: str
    source: str
    source_url: Optional[str] = None
    similarity: float
    start_pos: int
    end_pos: int
    type: str  # exact, near_duplicate, paraphrase, high_similarity
    source_year: Optional[int] = None
    source_authors: Optional[List[str]] = None


class PlagiarismStatistics(BaseModel):
    total_words: int
    matched_words: int
    match_percentage: float
    unique_sources: int
    matches_by_type: Dict[str, int]
    highest_similarity: float
    average_similarity: float


class PlagiarismCheckResponse(BaseModel):
    originality_score: float
    total_matches: int
    matches: List[PlagiarismMatch]
    statistics: PlagiarismStatistics
    text_length: int
    word_count: int
    language: str


class PlagiarismReportResponse(BaseModel):
    id: int
    originality_score: float
    total_matches: int
    unique_sources: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class CitationSuggestion(BaseModel):
    claim: str
    paper_title: str
    authors: List[str]
    year: Optional[int]
    venue: Optional[str]
    url: Optional[str]
    citation_count: Optional[int]
    relevance: float


class CitationSuggestionRequest(BaseModel):
    text: str = Field(..., min_length=50, description="Text that needs citations")
    context: Optional[str] = Field(None, description="Additional context")


class CitationSuggestionResponse(BaseModel):
    suggestions: List[CitationSuggestion]
    total_suggestions: int

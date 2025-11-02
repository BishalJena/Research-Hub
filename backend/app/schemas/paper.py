from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class PaperUploadResponse(BaseModel):
    paper_id: int
    filename: str
    status: str
    message: str


class PaperSummaryResponse(BaseModel):
    paper_id: int
    overall_summary: str
    section_summaries: Dict[str, str]
    key_insights: Dict
    word_count: int
    page_count: int


class RelatedPaper(BaseModel):
    paper_id: Optional[str]
    title: str
    authors: List[str]
    year: Optional[int]
    abstract: Optional[str]
    citation_count: Optional[int]
    url: Optional[str]
    relevance_score: float


class PaperResponse(BaseModel):
    id: int
    title: str
    abstract: Optional[str]
    keywords: Optional[List[str]]
    language: str
    status: str
    summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaperDetailResponse(PaperResponse):
    full_text: Optional[str]
    key_insights: Optional[Dict]
    extracted_citations: Optional[List]
    related_papers: Optional[List[Dict]]
    recommended_journals: Optional[List[Dict]]
    processing_progress: int

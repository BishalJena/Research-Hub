from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.journal import (
    JournalRecommendationRequest,
    JournalRecommendationResponse,
    JournalRecommendation,
    JournalSearchResponse
)
from app.services.journal_recommendation_service import JournalRecommendationService

router = APIRouter()


@router.post("/recommend", response_model=JournalRecommendationResponse)
async def recommend_journals(
    request: JournalRecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Recommend journals based on paper abstract and keywords

    - **abstract**: Paper abstract (minimum 100 characters)
    - **keywords**: Optional list of paper keywords
    - **preferences**: Optional user preferences for filtering

    Returns ranked list of journals with:
    - Semantic match score
    - Keyword overlap score
    - Impact factor and metrics
    - Publishing details
    - Fit score and acceptance probability
    """
    service = JournalRecommendationService()

    try:
        recommendations = await service.recommend_journals(
            paper_abstract=request.abstract,
            paper_keywords=request.keywords,
            preferences=request.preferences or {}
        )

        return JournalRecommendationResponse(
            total_recommendations=len(recommendations),
            recommendations=[
                JournalRecommendation(**rec) for rec in recommendations
            ],
            filters_applied=request.preferences or {}
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recommending journals: {str(e)}"
        )


@router.get("/{journal_id}")
async def get_journal(journal_id: str):
    """
    Get detailed information about a specific journal

    - **journal_id**: Journal identifier
    """
    service = JournalRecommendationService()

    journal = await service.get_journal_details(journal_id)

    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal not found"
        )

    return journal


@router.get("/search", response_model=JournalSearchResponse)
async def search_journals(q: str, limit: int = 20):
    """
    Search for journals by name or keyword

    - **q**: Search query
    - **limit**: Maximum number of results (default: 20)
    """
    service = JournalRecommendationService()

    results = await service.search_journals(query=q, limit=limit)

    return JournalSearchResponse(
        total_results=len(results),
        journals=results
    )


@router.get("/filters/options")
async def get_filter_options():
    """
    Get available filter options for journal recommendations

    Returns possible values for filtering journals.
    """
    return {
        "indexing_options": ["Scopus", "Web of Science", "PubMed", "DOAJ"],
        "subject_areas": [
            "Computer Science",
            "Engineering",
            "Physics",
            "Biology",
            "Chemistry",
            "Medicine",
            "Mathematics",
            "Social Sciences",
            "Humanities",
            "Multidisciplinary"
        ],
        "open_access_options": [True, False],
        "typical_impact_factors": {
            "low": "< 2.0",
            "medium": "2.0 - 5.0",
            "high": "5.0 - 10.0",
            "very_high": "> 10.0"
        },
        "typical_apc_ranges": {
            "free": 0,
            "low": "< $1000",
            "medium": "$1000 - $2500",
            "high": "> $2500"
        }
    }

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List

from app.services.topic_discovery_service import TopicDiscoveryService
from app.schemas.topic import (
    TrendingTopicsRequest,
    PersonalizedTopicsRequest,
    TopicEvolutionRequest,
    TopicResponse,
    TopicEvolutionResponse
)
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/trending")
async def get_trending_topics(
    discipline: str = "Computer Science",
    limit: int = 20,
    time_window: str = "recent",
    background_tasks: BackgroundTasks = None
):
    """
    Get trending research topics for a discipline

    - **discipline**: Academic discipline (e.g., "Computer Science", "Physics", "Biology")
    - **limit**: Number of topics to return (1-50)
    - **time_window**: Time window for analysis (recent, 1year, 2years)
    """
    service = TopicDiscoveryService()

    try:
        topics = await service.get_trending_topics(
            discipline=discipline,
            limit=limit,
            time_window=time_window
        )
        return topics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching trending topics: {str(e)}"
        )
    finally:
        # Cleanup in background
        if background_tasks:
            background_tasks.add_task(service.close)
        else:
            await service.close()


@router.post("/personalized", response_model=List[TopicResponse])
async def get_personalized_recommendations(
    request: PersonalizedTopicsRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Get personalized topic recommendations based on user interests

    Requires authentication.

    - **interests**: List of research interests
    - **region**: Geographic region for relevance
    - **limit**: Number of recommendations
    """
    service = TopicDiscoveryService()

    try:
        # If user has saved interests, merge with request
        user_interests = request.interests
        if current_user.research_interests:
            user_interests = list(set(user_interests + current_user.research_interests))

        topics = await service.get_personalized_topics(
            user_interests=user_interests,
            region=request.region,
            limit=request.limit
        )
        return topics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching personalized topics: {str(e)}"
        )
    finally:
        if background_tasks:
            background_tasks.add_task(service.close)
        else:
            await service.close()


@router.post("/evolution", response_model=TopicEvolutionResponse)
async def analyze_topic_evolution(
    request: TopicEvolutionRequest,
    background_tasks: BackgroundTasks = None
):
    """
    Analyze how a research topic has evolved over time

    - **topic**: Research topic to analyze
    - **years**: Number of years to analyze (1-10)

    Returns yearly statistics including:
    - Paper counts
    - Citation trends
    - Top papers per year
    - Overall trend direction
    - Growth rate
    """
    service = TopicDiscoveryService()

    try:
        evolution = await service.analyze_topic_evolution(
            topic=request.topic,
            years=request.years
        )
        return evolution
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing topic evolution: {str(e)}"
        )
    finally:
        if background_tasks:
            background_tasks.add_task(service.close)
        else:
            await service.close()


@router.get("/suggest-interests")
async def suggest_research_interests(
    discipline: str,
    limit: int = 10
):
    """
    Suggest research interests based on a discipline

    Helpful for new users to discover potential research areas.

    - **discipline**: Broad academic discipline
    - **limit**: Number of suggestions
    """
    service = TopicDiscoveryService()

    try:
        topics = await service.get_trending_topics(
            discipline=discipline,
            limit=limit,
            time_window="recent"
        )

        # Extract just the topic names
        suggestions = [
            {
                "interest": topic["topic"],
                "popularity": topic["paper_count"],
                "description": f"Trending topic with {topic['paper_count']} recent papers"
            }
            for topic in topics
        ]

        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suggesting interests: {str(e)}"
        )
    finally:
        await service.close()

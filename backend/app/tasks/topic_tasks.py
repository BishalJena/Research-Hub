"""
Celery tasks for Topic Discovery
"""
from app.celery_app import celery_app
from app.services.topic_discovery_service import TopicDiscoveryService
import asyncio
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="discover_trending_topics")
def discover_trending_topics_task(self, discipline: str, limit: int = 20):
    """
    Background task to discover trending topics

    Args:
        discipline: Academic discipline
        limit: Number of topics to return

    Returns:
        List of trending topics
    """
    logger.info(f"Starting topic discovery task for: {discipline}")

    try:
        # Run async function in sync context
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        service = TopicDiscoveryService()

        topics = loop.run_until_complete(
            service.get_trending_topics(discipline=discipline, limit=limit)
        )

        loop.run_until_complete(service.close())

        logger.info(f"Discovered {len(topics)} topics for {discipline}")
        return topics

    except Exception as e:
        logger.error(f"Error in topic discovery task: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="analyze_topic_evolution")
def analyze_topic_evolution_task(self, topic: str, years: int = 5):
    """
    Background task to analyze topic evolution

    Args:
        topic: Research topic
        years: Years to analyze

    Returns:
        Evolution analysis data
    """
    logger.info(f"Starting evolution analysis for: {topic}")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        service = TopicDiscoveryService()

        evolution = loop.run_until_complete(
            service.analyze_topic_evolution(topic=topic, years=years)
        )

        loop.run_until_complete(service.close())

        logger.info(f"Completed evolution analysis for {topic}")
        return evolution

    except Exception as e:
        logger.error(f"Error in evolution analysis task: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)

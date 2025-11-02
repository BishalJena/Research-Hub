"""
Topic Discovery Service - AI-powered research topic recommendation
"""
from typing import List, Dict, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import logging
import asyncio

from app.services.academic_api_client import (
    SemanticScholarClient,
    OpenAlexClient,
    ArXivClient
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class TopicDiscoveryService:
    """Service for discovering trending research topics"""

    def __init__(self):
        self.semantic_scholar = SemanticScholarClient(
            api_key=settings.SEMANTIC_SCHOLAR_API_KEY
        )
        self.openalex = OpenAlexClient(email=settings.OPENALEX_EMAIL)
        self.arxiv = ArXivClient()

    async def get_trending_topics(
        self,
        discipline: str,
        limit: int = 20,
        time_window: str = "recent"  # recent, 1year, 2years
    ) -> List[Dict]:
        """
        Get trending research topics for a discipline

        Args:
            discipline: Academic discipline (e.g., "Computer Science", "Physics")
            limit: Number of topics to return
            time_window: Time window for trend analysis

        Returns:
            List of trending topics with metadata
        """
        logger.info(f"Discovering trending topics for: {discipline}")

        # Define time range based on window
        year_filter = self._get_year_filter(time_window)

        # Fetch papers from multiple sources
        tasks = [
            self.semantic_scholar.search_papers(
                query=discipline,
                limit=100,
                year=year_filter
            ),
            self.openalex.search_works(
                query=discipline,
                per_page=100
            ),
            self.arxiv.search_papers(
                query=discipline,
                max_results=100
            )
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine and process results
        all_papers = []
        for result in results:
            if isinstance(result, list):
                all_papers.extend(result)

        logger.info(f"Fetched {len(all_papers)} papers from academic sources")

        # Extract and analyze topics
        topics = self._extract_topics(all_papers)

        # Calculate trend scores
        scored_topics = self._calculate_trend_scores(topics, all_papers)

        # Sort by score and return top topics
        top_topics = sorted(
            scored_topics,
            key=lambda x: x['score'],
            reverse=True
        )[:limit]

        logger.info(f"Identified {len(top_topics)} trending topics")
        return top_topics

    async def get_personalized_topics(
        self,
        user_interests: List[str],
        region: str = "Andhra Pradesh",
        limit: int = 20
    ) -> List[Dict]:
        """
        Get personalized topic recommendations based on user interests and region

        Args:
            user_interests: List of user's research interests
            region: Geographic region for relevance filtering
            limit: Number of recommendations

        Returns:
            List of personalized topic recommendations
        """
        logger.info(f"Generating personalized topics for interests: {user_interests}")

        # Build query from interests
        query = " OR ".join(user_interests)

        # Get trending topics
        topics = await self.get_trending_topics(query, limit=limit * 2)

        # Add regional relevance scoring
        topics_with_relevance = []
        for topic in topics:
            relevance_score = self._calculate_regional_relevance(
                topic,
                region,
                user_interests
            )
            topic['relevance_score'] = relevance_score
            topic['combined_score'] = (topic['score'] * 0.6) + (relevance_score * 0.4)
            topics_with_relevance.append(topic)

        # Sort by combined score
        personalized_topics = sorted(
            topics_with_relevance,
            key=lambda x: x['combined_score'],
            reverse=True
        )[:limit]

        return personalized_topics

    async def analyze_topic_evolution(
        self,
        topic: str,
        years: int = 5
    ) -> Dict:
        """
        Analyze how a topic has evolved over time

        Args:
            topic: Research topic to analyze
            years: Number of years to analyze

        Returns:
            Dictionary with evolution data
        """
        logger.info(f"Analyzing evolution of topic: {topic}")

        yearly_data = []

        for year in range(datetime.now().year - years, datetime.now().year + 1):
            papers = await self.semantic_scholar.search_papers(
                query=topic,
                year=str(year),
                limit=50
            )

            yearly_data.append({
                'year': year,
                'paper_count': len(papers),
                'total_citations': sum(p.get('citationCount', 0) for p in papers),
                'avg_citations': sum(p.get('citationCount', 0) for p in papers) / len(papers) if papers else 0,
                'top_papers': sorted(
                    papers,
                    key=lambda x: x.get('citationCount', 0),
                    reverse=True
                )[:5]
            })

        return {
            'topic': topic,
            'years_analyzed': years,
            'evolution': yearly_data,
            'trend': self._calculate_trend_direction(yearly_data),
            'growth_rate': self._calculate_growth_rate(yearly_data)
        }

    def _get_year_filter(self, time_window: str) -> str:
        """Get year filter string based on time window"""
        current_year = datetime.now().year

        if time_window == "recent":
            return f"{current_year - 1}-{current_year}"
        elif time_window == "1year":
            return str(current_year)
        elif time_window == "2years":
            return f"{current_year - 1}-{current_year}"
        else:
            return f"{current_year - 2}-{current_year}"

    def _extract_topics(self, papers: List[Dict]) -> List[str]:
        """Extract topics/keywords from papers"""
        topics = []

        for paper in papers:
            # From Semantic Scholar
            if 'fieldsOfStudy' in paper and paper['fieldsOfStudy']:
                topics.extend(paper['fieldsOfStudy'])

            # From arXiv
            if 'categories' in paper and paper['categories']:
                topics.extend(paper['categories'])

            # From OpenAlex
            if 'concepts' in paper and paper['concepts']:
                topics.extend([c.get('display_name') for c in paper['concepts'] if c.get('display_name')])

        return topics

    def _calculate_trend_scores(
        self,
        topics: List[str],
        papers: List[Dict]
    ) -> List[Dict]:
        """Calculate trend scores for topics"""
        # Count topic frequencies
        topic_counts = Counter(topics)

        # Build topic metadata
        topic_data = defaultdict(lambda: {
            'papers': [],
            'total_citations': 0,
            'recent_citations': 0,
            'paper_count': 0
        })

        for paper in papers:
            paper_topics = self._get_paper_topics(paper)
            citations = paper.get('citationCount', 0) or paper.get('cited_by_count', 0) or 0

            for topic in paper_topics:
                topic_data[topic]['papers'].append(paper)
                topic_data[topic]['total_citations'] += citations
                topic_data[topic]['paper_count'] += 1

                # Check if recent (last 2 years)
                year = self._get_paper_year(paper)
                if year and year >= datetime.now().year - 2:
                    topic_data[topic]['recent_citations'] += citations

        # Calculate scores
        scored_topics = []
        for topic, count in topic_counts.most_common(100):
            data = topic_data[topic]

            # Skip if too few papers
            if data['paper_count'] < 3:
                continue

            # Calculate score components
            frequency_score = count / len(papers) if papers else 0
            citation_score = data['total_citations'] / data['paper_count'] if data['paper_count'] else 0
            recency_score = data['recent_citations'] / data['total_citations'] if data['total_citations'] else 0

            # Normalize scores (0-1)
            frequency_score = min(frequency_score * 10, 1.0)
            citation_score = min(citation_score / 100, 1.0)
            recency_score = min(recency_score, 1.0)

            # Weighted combination
            final_score = (
                frequency_score * 0.3 +
                citation_score * 0.4 +
                recency_score * 0.3
            )

            scored_topics.append({
                'topic': topic,
                'score': final_score,
                'paper_count': data['paper_count'],
                'total_citations': data['total_citations'],
                'avg_citations': data['total_citations'] / data['paper_count'],
                'frequency': count,
                'top_papers': sorted(
                    data['papers'],
                    key=lambda x: x.get('citationCount', 0) or x.get('cited_by_count', 0) or 0,
                    reverse=True
                )[:3]
            })

        return scored_topics

    def _calculate_regional_relevance(
        self,
        topic: Dict,
        region: str,
        user_interests: List[str]
    ) -> float:
        """Calculate regional relevance score for a topic"""
        score = 0.0

        # Check if topic matches user interests
        topic_name = topic['topic'].lower()
        for interest in user_interests:
            if interest.lower() in topic_name or topic_name in interest.lower():
                score += 0.4
                break

        # Regional keywords for Andhra Pradesh
        regional_keywords = [
            'agriculture', 'rural', 'education', 'healthcare', 'sustainability',
            'water', 'climate', 'infrastructure', 'technology', 'digital',
            'social', 'economy', 'development', 'india', 'sustainable development goals'
        ]

        # Check for regional relevance
        for keyword in regional_keywords:
            if keyword in topic_name:
                score += 0.3
                break

        # Base score for all topics
        score += 0.3

        return min(score, 1.0)

    def _get_paper_topics(self, paper: Dict) -> List[str]:
        """Extract topics from a paper"""
        topics = []

        if 'fieldsOfStudy' in paper and paper['fieldsOfStudy']:
            topics.extend(paper['fieldsOfStudy'])

        if 'categories' in paper and paper['categories']:
            topics.extend(paper['categories'])

        if 'concepts' in paper and paper['concepts']:
            topics.extend([c.get('display_name') for c in paper['concepts'] if c.get('display_name')])

        return topics

    def _get_paper_year(self, paper: Dict) -> Optional[int]:
        """Extract publication year from paper"""
        if 'year' in paper and paper['year']:
            return int(paper['year'])
        if 'publication_year' in paper:
            return int(paper['publication_year'])
        if 'published' in paper:
            try:
                return datetime.fromisoformat(paper['published'].replace('Z', '+00:00')).year
            except:
                pass
        return None

    def _calculate_trend_direction(self, yearly_data: List[Dict]) -> str:
        """Calculate if trend is growing, declining, or stable"""
        if len(yearly_data) < 2:
            return "insufficient_data"

        recent = yearly_data[-2:]
        growth = (recent[1]['paper_count'] - recent[0]['paper_count']) / recent[0]['paper_count'] if recent[0]['paper_count'] > 0 else 0

        if growth > 0.2:
            return "rapidly_growing"
        elif growth > 0.05:
            return "growing"
        elif growth < -0.2:
            return "declining"
        elif growth < -0.05:
            return "slowly_declining"
        else:
            return "stable"

    def _calculate_growth_rate(self, yearly_data: List[Dict]) -> float:
        """Calculate average growth rate"""
        if len(yearly_data) < 2:
            return 0.0

        growth_rates = []
        for i in range(1, len(yearly_data)):
            if yearly_data[i-1]['paper_count'] > 0:
                rate = (yearly_data[i]['paper_count'] - yearly_data[i-1]['paper_count']) / yearly_data[i-1]['paper_count']
                growth_rates.append(rate)

        return sum(growth_rates) / len(growth_rates) if growth_rates else 0.0

    async def close(self):
        """Close all API clients"""
        await self.semantic_scholar.close()
        await self.openalex.close()

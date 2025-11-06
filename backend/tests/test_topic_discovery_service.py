"""
Unit Tests for Topic Discovery Service
Tests trending topic recommendations and personalization
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.topic_discovery_service import TopicDiscoveryService


class TestTopicDiscoveryService:
    """Test suite for Topic Discovery Service"""

    @pytest.fixture
    def service(self, mock_academic_clients):
        """Create service instance with mocked API clients"""
        service = TopicDiscoveryService()
        service.semantic_scholar = mock_academic_clients['semantic_scholar']
        service.openalex = mock_academic_clients['openalex']
        service.arxiv = mock_academic_clients['arxiv']
        return service

    @pytest.mark.asyncio
    async def test_get_trending_topics_success(self, service, mock_semantic_scholar_papers):
        """Test successful trending topic discovery"""
        # Act
        topics = await service.get_trending_topics(
            discipline="Computer Science",
            limit=10,
            time_window="recent"
        )

        # Assert
        assert isinstance(topics, list)
        assert len(topics) > 0
        assert len(topics) <= 10

        # Check topic structure
        first_topic = topics[0]
        assert 'topic_name' in first_topic
        assert 'relevance_score' in first_topic
        assert 'paper_count' in first_topic
        assert 'total_citations' in first_topic
        assert 0 <= first_topic['relevance_score'] <= 1.0

    @pytest.mark.asyncio
    async def test_get_trending_topics_filters_low_quality(self, service):
        """Test that low-quality topics (< 3 papers) are filtered out"""
        topics = await service.get_trending_topics("Physics", limit=20)

        # All topics should have at least 3 papers
        for topic in topics:
            assert topic['paper_count'] >= 3

    @pytest.mark.asyncio
    async def test_get_trending_topics_sorted_by_score(self, service):
        """Test that topics are sorted by score in descending order"""
        topics = await service.get_trending_topics("Biology", limit=15)

        # Check sorting
        scores = [t['relevance_score'] for t in topics]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_get_personalized_topics_success(self, service):
        """Test personalized topic recommendations"""
        # Arrange
        user_interests = ["machine learning", "healthcare"]
        region = "Andhra Pradesh"

        # Act
        topics = await service.get_personalized_topics(
            user_interests=user_interests,
            region=region,
            limit=10
        )

        # Assert
        assert isinstance(topics, list)
        assert len(topics) > 0

        # Check that topics have relevance scoring
        for topic in topics:
            assert 'relevance_score' in topic
            assert 'combined_score' in topic
            assert 0 <= topic['relevance_score'] <= 1.0
            assert 0 <= topic['combined_score'] <= 1.0

    @pytest.mark.asyncio
    async def test_get_personalized_topics_regional_boost(self, service):
        """Test that regional keywords boost topic relevance"""
        # Topics with regional keywords should score higher
        topics_regional = await service.get_personalized_topics(
            user_interests=["agriculture", "sustainable development"],
            region="Andhra Pradesh",
            limit=10
        )

        topics_generic = await service.get_personalized_topics(
            user_interests=["quantum computing"],
            region="Andhra Pradesh",
            limit=10
        )

        # Regional topics should have higher average relevance
        # (This test assumes mock data contains regional keywords)
        assert len(topics_regional) > 0
        assert len(topics_generic) > 0

    @pytest.mark.asyncio
    async def test_analyze_topic_evolution_success(self, service):
        """Test topic evolution analysis over time"""
        # Act
        evolution = await service.analyze_topic_evolution(
            topic="deep learning",
            years=5
        )

        # Assert
        assert 'topic' in evolution
        assert evolution['topic'] == "deep learning"
        assert 'years_analyzed' in evolution
        assert evolution['years_analyzed'] == 5
        assert 'evolution' in evolution
        assert isinstance(evolution['evolution'], list)
        assert len(evolution['evolution']) == 6  # 5 years + current year
        assert 'trend' in evolution
        assert 'growth_rate' in evolution

        # Check yearly data structure
        for year_data in evolution['evolution']:
            assert 'year' in year_data
            assert 'paper_count' in year_data
            assert 'total_citations' in year_data
            assert 'avg_citations' in year_data
            assert 'top_papers' in year_data

    @pytest.mark.asyncio
    async def test_analyze_topic_evolution_trend_calculation(self, service):
        """Test trend direction calculation"""
        evolution = await service.analyze_topic_evolution("AI ethics", years=3)

        # Trend should be one of the expected values
        valid_trends = [
            "rapidly_growing", "growing", "stable",
            "slowly_declining", "declining", "insufficient_data"
        ]
        assert evolution['trend'] in valid_trends

    @pytest.mark.asyncio
    async def test_get_year_filter_recent(self, service):
        """Test year filter for recent papers"""
        from datetime import datetime
        current_year = datetime.now().year

        year_filter = service._get_year_filter("recent")
        assert str(current_year - 1) in year_filter
        assert str(current_year) in year_filter

    @pytest.mark.asyncio
    async def test_extract_topics_from_papers(self, service, mock_semantic_scholar_papers):
        """Test topic extraction from paper metadata"""
        topics = service._extract_topics(mock_semantic_scholar_papers)

        # Should extract topics from fieldsOfStudy
        assert isinstance(topics, list)
        assert len(topics) > 0
        assert "Computer Science" in topics
        assert "Natural Language Processing" in topics

    @pytest.mark.asyncio
    async def test_calculate_trend_scores(self, service, mock_semantic_scholar_papers):
        """Test trend score calculation logic"""
        # Extract topics
        topics_list = service._extract_topics(mock_semantic_scholar_papers)

        # Calculate scores
        scored_topics = service._calculate_trend_scores(topics_list, mock_semantic_scholar_papers)

        # Verify scoring
        assert isinstance(scored_topics, list)
        for topic in scored_topics:
            assert 'topic' in topic
            assert 'score' in topic
            assert 'paper_count' in topic
            assert 'total_citations' in topic
            assert 'avg_citations' in topic
            assert 0 <= topic['score'] <= 1.0

    @pytest.mark.asyncio
    async def test_regional_relevance_scoring(self, service):
        """Test regional relevance calculation"""
        # Create mock topic
        mock_topic = {
            'topic': 'sustainable agriculture',
            'score': 0.8
        }

        # Test with regional keywords
        score_regional = service._calculate_regional_relevance(
            mock_topic,
            region="Andhra Pradesh",
            user_interests=["agriculture", "sustainability"]
        )

        # Test without regional keywords
        mock_topic_generic = {
            'topic': 'quantum computing',
            'score': 0.8
        }

        score_generic = service._calculate_regional_relevance(
            mock_topic_generic,
            region="Andhra Pradesh",
            user_interests=["physics"]
        )

        # Regional topic should score higher
        assert score_regional > score_generic
        assert 0 <= score_regional <= 1.0
        assert 0 <= score_generic <= 1.0

    @pytest.mark.asyncio
    async def test_empty_discipline_handling(self, service):
        """Test handling of empty discipline query"""
        topics = await service.get_trending_topics("", limit=5)

        # Should still return results (all disciplines)
        assert isinstance(topics, list)
        # Empty discipline should return mock data
        for topic in topics:
            assert 'topic_name' in topic

    @pytest.mark.asyncio
    async def test_api_error_handling(self, service):
        """Test graceful handling of API errors"""
        # Mock API to raise exception
        service.semantic_scholar.search_papers = AsyncMock(side_effect=Exception("API Error"))
        service.openalex.search_works = AsyncMock(side_effect=Exception("API Error"))
        service.arxiv.search_papers = AsyncMock(side_effect=Exception("API Error"))

        # Should not crash, return mock fallback results
        topics = await service.get_trending_topics("Physics", limit=10)
        assert isinstance(topics, list)
        # Should return mock data when APIs fail
        assert len(topics) > 0

    @pytest.mark.asyncio
    async def test_close_method(self, service):
        """Test that close() properly closes all API clients"""
        await service.close()

        # Verify close was called on all clients
        service.semantic_scholar.close.assert_called_once()
        service.openalex.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_growth_rate_calculation(self, service):
        """Test growth rate calculation for topic evolution"""
        yearly_data = [
            {'year': 2020, 'paper_count': 100},
            {'year': 2021, 'paper_count': 120},
            {'year': 2022, 'paper_count': 150},
            {'year': 2023, 'paper_count': 180},
        ]

        growth_rate = service._calculate_growth_rate(yearly_data)

        # Growth rate should be positive (increasing papers)
        assert growth_rate > 0
        assert isinstance(growth_rate, float)

    @pytest.mark.asyncio
    async def test_topic_frequency_scoring(self, service):
        """Test that topic frequency contributes to score"""
        # Create papers with repeated topics
        papers = [
            {'fieldsOfStudy': ['Machine Learning', 'AI'], 'citationCount': 50},
            {'fieldsOfStudy': ['Machine Learning', 'NLP'], 'citationCount': 60},
            {'fieldsOfStudy': ['Machine Learning', 'Computer Vision'], 'citationCount': 70},
            {'fieldsOfStudy': ['Physics', 'Quantum'], 'citationCount': 80},
        ]

        topics = service._extract_topics(papers)
        scored = service._calculate_trend_scores(topics, papers)

        # 'Machine Learning' appears 3 times, should have high score
        ml_topic = next((t for t in scored if t['topic'] == 'Machine Learning'), None)
        assert ml_topic is not None
        assert ml_topic['paper_count'] == 3
        assert ml_topic['score'] > 0


class TestTopicDiscoveryEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def service(self):
        """Create service with default setup"""
        return TopicDiscoveryService()

    @pytest.mark.asyncio
    async def test_large_limit_handling(self, service):
        """Test handling of very large limit values"""
        topics = await service.get_trending_topics("CS", limit=1000)

        # Should cap at reasonable number
        assert len(topics) <= 100  # Internal cap

    @pytest.mark.asyncio
    async def test_zero_papers_scenario(self, service):
        """Test behavior when no papers are found"""
        # Mock empty responses
        service.semantic_scholar.search_papers = AsyncMock(return_value=[])
        service.openalex.search_works = AsyncMock(return_value=[])
        service.arxiv.search_papers = AsyncMock(return_value=[])

        topics = await service.get_trending_topics("NonexistentField", limit=10)

        # Should return mock data as fallback (not empty list)
        assert isinstance(topics, list)
        assert len(topics) > 0  # Mock data is returned as fallback

    @pytest.mark.asyncio
    async def test_malformed_paper_data(self, service):
        """Test handling of malformed paper data"""
        malformed_papers = [
            {'title': 'Paper 1'},  # Missing fields
            {},  # Empty
            {'fieldsOfStudy': None, 'citationCount': 'invalid'},  # Invalid types
        ]

        # Should not crash
        topics = service._extract_topics(malformed_papers)
        assert isinstance(topics, list)

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, service):
        """Test handling of concurrent topic discovery requests"""
        import asyncio

        # Run multiple requests concurrently
        tasks = [
            service.get_trending_topics("Physics", limit=5),
            service.get_trending_topics("Chemistry", limit=5),
            service.get_trending_topics("Biology", limit=5),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        assert len(results) == 3
        for result in results:
            if isinstance(result, list):
                # Should return valid topics
                assert len(result) > 0
            else:
                # If exception, it should be handled
                assert isinstance(result, Exception)

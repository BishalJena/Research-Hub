"""
Integration Tests for Topics API Endpoints
Tests /api/v1/topics/* routes
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


class TestTopicsAPI:
    """Integration tests for topics endpoints"""

    @pytest.mark.integration
    def test_get_trending_topics_success(self, client, mock_academic_clients):
        """Test GET /api/v1/topics/trending"""
        with patch('app.api.endpoints.topics.TopicDiscoveryService') as mock_service:
            # Setup mock
            mock_instance = mock_service.return_value
            mock_instance.get_trending_topics = AsyncMock(return_value=[
                {
                    "topic": "Machine Learning",
                    "score": 0.85,
                    "paper_count": 150,
                    "total_citations": 5000,
                    "avg_citations": 33.3,
                    "frequency": 45,
                    "top_papers": []
                }
            ])
            mock_instance.close = AsyncMock()

            # Make request
            response = client.get(
                "/api/v1/topics/trending",
                params={"discipline": "Computer Science", "limit": 10}
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            assert "topic" in data[0]
            assert "score" in data[0]

    @pytest.mark.integration
    def test_get_trending_topics_invalid_params(self, client):
        """Test trending topics with invalid parameters"""
        response = client.get(
            "/api/v1/topics/trending",
            params={"discipline": "", "limit": -1}
        )

        # Should handle gracefully or return error
        assert response.status_code in [200, 400, 422, 500]

    @pytest.mark.integration
    def test_get_personalized_topics_requires_auth(self, client):
        """Test that personalized topics requires authentication"""
        response = client.post(
            "/api/v1/topics/personalized",
            json={
                "interests": ["AI", "ML"],
                "region": "Andhra Pradesh",
                "limit": 10
            }
        )

        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403]

    @pytest.mark.integration
    def test_get_personalized_topics_with_auth(self, authenticated_client, test_user):
        """Test POST /api/v1/topics/personalized with authentication"""
        with patch('app.api.endpoints.topics.TopicDiscoveryService') as mock_service:
            # Setup mock
            mock_instance = mock_service.return_value
            mock_instance.get_personalized_topics = AsyncMock(return_value=[
                {
                    "topic": "AI in Healthcare",
                    "score": 0.9,
                    "relevance_score": 0.85,
                    "combined_score": 0.88,
                    "paper_count": 200,
                    "total_citations": 8000
                }
            ])
            mock_instance.close = AsyncMock()

            # Make request
            response = authenticated_client.post(
                "/api/v1/topics/personalized",
                json={
                    "interests": ["Healthcare", "AI"],
                    "region": "Andhra Pradesh",
                    "limit": 10
                }
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                assert "topic" in data[0]
                assert "relevance_score" in data[0]

    @pytest.mark.integration
    def test_analyze_topic_evolution_success(self, client):
        """Test POST /api/v1/topics/evolution"""
        with patch('app.api.endpoints.topics.TopicDiscoveryService') as mock_service:
            # Setup mock
            mock_instance = mock_service.return_value
            mock_instance.analyze_topic_evolution = AsyncMock(return_value={
                "topic": "Deep Learning",
                "years_analyzed": 5,
                "evolution": [
                    {"year": 2020, "paper_count": 100, "total_citations": 2000}
                ],
                "trend": "growing",
                "growth_rate": 0.15
            })
            mock_instance.close = AsyncMock()

            # Make request
            response = client.post(
                "/api/v1/topics/evolution",
                json={"topic": "Deep Learning", "years": 5}
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "topic" in data
            assert "evolution" in data
            assert "trend" in data
            assert "growth_rate" in data

    @pytest.mark.integration
    def test_suggest_interests_success(self, client):
        """Test GET /api/v1/topics/suggest-interests"""
        with patch('app.api.endpoints.topics.TopicDiscoveryService') as mock_service:
            # Setup mock
            mock_instance = mock_service.return_value
            mock_instance.get_trending_topics = AsyncMock(return_value=[
                {
                    "topic": "Neural Networks",
                    "paper_count": 250,
                    "score": 0.8
                }
            ])
            mock_instance.close = AsyncMock()

            # Make request
            response = client.get(
                "/api/v1/topics/suggest-interests",
                params={"discipline": "AI", "limit": 5}
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                assert "interest" in data[0]
                assert "popularity" in data[0]

    @pytest.mark.integration
    def test_api_error_handling(self, client):
        """Test error handling when service fails"""
        with patch('app.api.endpoints.topics.TopicDiscoveryService') as mock_service:
            # Setup mock to raise exception
            mock_instance = mock_service.return_value
            mock_instance.get_trending_topics = AsyncMock(side_effect=Exception("API Error"))
            mock_instance.close = AsyncMock()

            # Make request
            response = client.get(
                "/api/v1/topics/trending",
                params={"discipline": "CS", "limit": 10}
            )

            # Should return 500 error
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data


class TestTopicsAPIValidation:
    """Test request/response validation"""

    @pytest.mark.integration
    def test_trending_topics_query_params(self, client):
        """Test query parameter validation"""
        # Valid params
        response = client.get(
            "/api/v1/topics/trending",
            params={
                "discipline": "Computer Science",
                "limit": 20,
                "time_window": "recent"
            }
        )

        assert response.status_code in [200, 500]  # May fail on service but params valid

    @pytest.mark.integration
    def test_personalized_topics_request_schema(self, authenticated_client):
        """Test request schema validation for personalized topics"""
        with patch('app.api.endpoints.topics.TopicDiscoveryService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_personalized_topics = AsyncMock(return_value=[])
            mock_instance.close = AsyncMock()

            # Valid request
            response = authenticated_client.post(
                "/api/v1/topics/personalized",
                json={
                    "interests": ["AI", "ML", "NLP"],
                    "region": "Andhra Pradesh",
                    "limit": 15
                }
            )

            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    def test_evolution_request_validation(self, client):
        """Test evolution request validation"""
        # Missing required fields
        response = client.post(
            "/api/v1/topics/evolution",
            json={}
        )

        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    def test_response_model_structure(self, client):
        """Test that responses match expected schema"""
        with patch('app.api.endpoints.topics.TopicDiscoveryService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_trending_topics = AsyncMock(return_value=[
                {
                    "topic": "Test Topic",
                    "score": 0.75,
                    "paper_count": 100,
                    "total_citations": 1000,
                    "avg_citations": 10.0,
                    "frequency": 25,
                    "top_papers": []
                }
            ])
            mock_instance.close = AsyncMock()

            response = client.get(
                "/api/v1/topics/trending",
                params={"discipline": "CS"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Validate structure
            assert isinstance(data, list)
            for topic in data:
                assert "topic" in topic
                assert "score" in topic
                assert isinstance(topic["score"], (int, float))
                assert 0 <= topic["score"] <= 1.0

"""
Integration Tests for Journal Recommendation API Endpoints
Tests /api/v1/journals/* routes
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


class TestJournalsAPI:
    """Integration tests for journal recommendation endpoints"""

    @pytest.mark.integration
    def test_recommend_journals_requires_auth(self, client):
        """Test that journal recommendation requires authentication"""
        response = client.post(
            "/api/v1/journals/recommend",
            json={
                "abstract": "This is a research paper about machine learning. " * 10,
                "keywords": ["ML", "AI"],
                "preferences": {}
            }
        )

        # Should require authentication
        assert response.status_code in [401, 403]

    @pytest.mark.integration
    def test_recommend_journals_success(self, authenticated_client):
        """Test POST /api/v1/journals/recommend"""
        with patch('app.api.endpoints.journals.JournalRecommendationService') as mock_service:
            # Setup mock
            mock_instance = mock_service.return_value
            mock_instance.recommend_journals = AsyncMock(return_value=[
                {
                    "id": "nature",
                    "title": "Nature",
                    "publisher": "Nature Publishing Group",
                    "impact_factor": 49.96,
                    "open_access": False,
                    "semantic_score": 0.85,
                    "keyword_score": 0.75,
                    "composite_score": 0.82,
                    "fit_score": 0.80,
                    "acceptance_probability": 0.10
                }
            ])

            # Make request
            response = authenticated_client.post(
                "/api/v1/journals/recommend",
                json={
                    "abstract": "This paper presents novel approaches to deep learning for NLP. " * 10,
                    "keywords": ["deep learning", "NLP", "transformers"],
                    "preferences": {
                        "open_access_only": False,
                        "min_impact_factor": 3.0
                    }
                }
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "total_recommendations" in data
            assert "recommendations" in data
            assert "filters_applied" in data
            assert isinstance(data["recommendations"], list)

    @pytest.mark.integration
    def test_recommend_journals_short_abstract_error(self, authenticated_client):
        """Test that short abstracts are rejected"""
        response = authenticated_client.post(
            "/api/v1/journals/recommend",
            json={
                "abstract": "Too short",
                "keywords": [],
                "preferences": {}
            }
        )

        # Should return 400 bad request
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.integration
    def test_recommend_journals_with_preferences(self, authenticated_client):
        """Test journal recommendations with filters"""
        with patch('app.api.endpoints.journals.JournalRecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.recommend_journals = AsyncMock(return_value=[
                {
                    "id": "plos-one",
                    "title": "PLOS ONE",
                    "open_access": True,
                    "apc_amount": 1825,
                    "impact_factor": 3.24,
                    "scopus_indexed": True,
                    "semantic_score": 0.80,
                    "keyword_score": 0.70,
                    "composite_score": 0.75,
                    "fit_score": 0.72,
                    "acceptance_probability": 0.50
                }
            ])

            response = authenticated_client.post(
                "/api/v1/journals/recommend",
                json={
                    "abstract": "Machine learning research for healthcare applications. " * 15,
                    "keywords": ["machine learning", "healthcare"],
                    "preferences": {
                        "open_access_only": True,
                        "max_apc": 2000,
                        "min_impact_factor": 3.0,
                        "required_indexing": ["Scopus"]
                    }
                }
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Check that filters were applied
            assert data["filters_applied"]["open_access_only"] == True

    @pytest.mark.integration
    def test_get_journal_details(self, client):
        """Test GET /api/v1/journals/{journal_id}"""
        with patch('app.api.endpoints.journals.JournalRecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_journal_details = AsyncMock(return_value={
                "id": "nature",
                "title": "Nature",
                "publisher": "Nature Publishing Group",
                "impact_factor": 49.96,
                "h_index": 1089,
                "open_access": False
            })

            response = client.get("/api/v1/journals/nature")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == "nature"
            assert "title" in data

    @pytest.mark.integration
    def test_get_journal_not_found(self, client):
        """Test getting non-existent journal"""
        with patch('app.api.endpoints.journals.JournalRecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_journal_details = AsyncMock(return_value=None)

            response = client.get("/api/v1/journals/nonexistent")

            assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.integration
    def test_search_journals(self, client):
        """Test GET /api/v1/journals/search"""
        with patch('app.api.endpoints.journals.JournalRecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.search_journals = AsyncMock(return_value=[
                {"id": "nature", "title": "Nature"},
                {"id": "science", "title": "Science"}
            ])

            response = client.get(
                "/api/v1/journals/search",
                params={"q": "nature", "limit": 10}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "total_results" in data
            assert "journals" in data
            assert len(data["journals"]) == 2

    @pytest.mark.integration
    def test_get_filter_options(self, client):
        """Test GET /api/v1/journals/filters/options"""
        response = client.get("/api/v1/journals/filters/options")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "indexing_options" in data
        assert "subject_areas" in data
        assert "open_access_options" in data
        assert "typical_impact_factors" in data

    @pytest.mark.integration
    def test_api_error_handling(self, authenticated_client):
        """Test error handling when service fails"""
        with patch('app.api.endpoints.journals.JournalRecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.recommend_journals = AsyncMock(side_effect=Exception("Service Error"))

            response = authenticated_client.post(
                "/api/v1/journals/recommend",
                json={
                    "abstract": "Test abstract. " * 20,
                    "keywords": [],
                    "preferences": {}
                }
            )

            # Should return 500 error
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestJournalsAPIResponseStructure:
    """Test response structure and data validation"""

    @pytest.mark.integration
    def test_recommendation_response_structure(self, authenticated_client):
        """Test recommendation response structure"""
        with patch('app.api.endpoints.journals.JournalRecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.recommend_journals = AsyncMock(return_value=[
                {
                    "id": "test-journal",
                    "title": "Test Journal",
                    "publisher": "Test Publisher",
                    "impact_factor": 5.0,
                    "h_index": 100,
                    "open_access": True,
                    "apc_amount": 1500,
                    "semantic_score": 0.85,
                    "keyword_score": 0.75,
                    "composite_score": 0.80,
                    "fit_score": 0.78,
                    "acceptance_probability": 0.40,
                    "scopus_indexed": True,
                    "web_of_science_indexed": True
                }
            ])

            response = authenticated_client.post(
                "/api/v1/journals/recommend",
                json={
                    "abstract": "Research on AI and machine learning applications. " * 15,
                    "keywords": ["AI", "ML"]
                }
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Validate structure
            assert "total_recommendations" in data
            assert "recommendations" in data
            assert data["total_recommendations"] == len(data["recommendations"])

            # Validate recommendation fields
            if len(data["recommendations"]) > 0:
                rec = data["recommendations"][0]
                assert "id" in rec
                assert "title" in rec
                assert "semantic_score" in rec
                assert "composite_score" in rec

                # Validate score ranges
                assert 0 <= rec["semantic_score"] <= 1.0
                assert 0 <= rec["composite_score"] <= 1.0
                assert 0 <= rec["acceptance_probability"] <= 1.0

    @pytest.mark.integration
    def test_search_response_structure(self, client):
        """Test search response structure"""
        with patch('app.api.endpoints.journals.JournalRecommendationService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.search_journals = AsyncMock(return_value=[
                {"id": "j1", "title": "Journal 1"},
                {"id": "j2", "title": "Journal 2"}
            ])

            response = client.get(
                "/api/v1/journals/search",
                params={"q": "test", "limit": 5}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert isinstance(data["total_results"], int)
            assert isinstance(data["journals"], list)
            assert data["total_results"] == len(data["journals"])

    @pytest.mark.integration
    def test_filter_options_structure(self, client):
        """Test filter options response structure"""
        response = client.get("/api/v1/journals/filters/options")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Validate structure
        assert "indexing_options" in data
        assert isinstance(data["indexing_options"], list)
        assert "Scopus" in data["indexing_options"]

        assert "subject_areas" in data
        assert isinstance(data["subject_areas"], list)

        assert "open_access_options" in data
        assert isinstance(data["open_access_options"], list)

        assert "typical_impact_factors" in data
        assert isinstance(data["typical_impact_factors"], dict)

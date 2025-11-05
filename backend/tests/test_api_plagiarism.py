"""
Integration Tests for Plagiarism API Endpoints
Tests /api/v1/plagiarism/* routes
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


class TestPlagiarismAPI:
    """Integration tests for plagiarism endpoints"""

    @pytest.mark.integration
    def test_check_plagiarism_requires_auth(self, client):
        """Test that plagiarism check requires authentication"""
        response = client.post(
            "/api/v1/plagiarism/check",
            json={
                "text": "This is sample text to check for plagiarism.",
                "language": "en",
                "check_online": True
            }
        )

        # Should require authentication
        assert response.status_code in [401, 403]

    @pytest.mark.integration
    def test_check_plagiarism_success(self, authenticated_client, test_user):
        """Test POST /api/v1/plagiarism/check"""
        with patch('app.api.endpoints.plagiarism.PlagiarismDetectionService') as mock_service:
            # Setup mock
            mock_instance = mock_service.return_value
            mock_instance.check_plagiarism = AsyncMock(return_value={
                "originality_score": 85.5,
                "total_matches": 2,
                "matches": [
                    {
                        "text": "sample text",
                        "source": "Test Source",
                        "similarity": 0.75,
                        "type": "paraphrase"
                    }
                ],
                "statistics": {
                    "total_words": 100,
                    "matched_words": 15,
                    "match_percentage": 15.0,
                    "unique_sources": 1,
                    "matches_by_type": {"paraphrase": 2},
                    "highest_similarity": 0.75,
                    "average_similarity": 0.70
                },
                "text_length": 500,
                "word_count": 100,
                "language": "en"
            })
            mock_instance.close = AsyncMock()

            # Make request
            response = authenticated_client.post(
                "/api/v1/plagiarism/check",
                json={
                    "text": "This is sample text to check for plagiarism. " * 10,
                    "language": "en",
                    "check_online": True
                }
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "originality_score" in data
            assert "total_matches" in data
            assert "matches" in data
            assert "statistics" in data
            assert 0 <= data["originality_score"] <= 100

    @pytest.mark.integration
    def test_check_plagiarism_validation(self, authenticated_client):
        """Test request validation for plagiarism check"""
        # Missing required field
        response = authenticated_client.post(
            "/api/v1/plagiarism/check",
            json={"language": "en"}
        )

        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    def test_get_plagiarism_report(self, authenticated_client, test_user, test_db):
        """Test GET /api/v1/plagiarism/report/{check_id}"""
        from app.models.plagiarism_check import PlagiarismCheck
        from datetime import datetime

        # Create plagiarism check record
        check = PlagiarismCheck(
            user_id=test_user.id,
            text="Sample text",
            language="en",
            originality_score=90.0,
            total_matches=1,
            matches=[],
            total_words=50,
            matched_words=5,
            unique_sources=1,
            status="completed",
            completed_at=datetime.utcnow()
        )

        test_db.add(check)
        test_db.commit()
        test_db.refresh(check)

        # Get report
        response = authenticated_client.get(f"/api/v1/plagiarism/report/{check.id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == check.id
        assert data["originality_score"] == 90.0

    @pytest.mark.integration
    def test_get_plagiarism_report_not_found(self, authenticated_client):
        """Test getting non-existent report"""
        response = authenticated_client.get("/api/v1/plagiarism/report/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.integration
    def test_get_plagiarism_history(self, authenticated_client, test_user, test_db):
        """Test GET /api/v1/plagiarism/history"""
        from app.models.plagiarism_check import PlagiarismCheck
        from datetime import datetime

        # Create multiple checks
        for i in range(3):
            check = PlagiarismCheck(
                user_id=test_user.id,
                text=f"Sample text {i}",
                language="en",
                originality_score=85.0 + i,
                total_matches=i,
                matches=[],
                total_words=100,
                matched_words=10,
                unique_sources=1,
                status="completed",
                completed_at=datetime.utcnow()
            )
            test_db.add(check)

        test_db.commit()

        # Get history
        response = authenticated_client.get("/api/v1/plagiarism/history?limit=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.integration
    def test_suggest_citations_success(self, authenticated_client):
        """Test POST /api/v1/plagiarism/citations/suggest"""
        with patch('app.api.endpoints.plagiarism.PlagiarismDetectionService') as mock_service:
            # Setup mock
            mock_instance = mock_service.return_value
            mock_instance.suggest_citations = AsyncMock(return_value=[
                {
                    "claim": "Research shows...",
                    "paper_title": "Study on X",
                    "authors": ["Author A"],
                    "year": 2023,
                    "venue": "Conference",
                    "url": "https://example.com",
                    "citation_count": 100,
                    "relevance": 0.85
                }
            ])
            mock_instance.close = AsyncMock()

            # Make request
            response = authenticated_client.post(
                "/api/v1/plagiarism/citations/suggest",
                json={
                    "text": "Research shows that AI is effective. Studies have demonstrated this.",
                    "context": "Machine learning research"
                }
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "suggestions" in data
            assert "total_suggestions" in data

    @pytest.mark.integration
    def test_delete_plagiarism_check(self, authenticated_client, test_user, test_db):
        """Test DELETE /api/v1/plagiarism/{check_id}"""
        from app.models.plagiarism_check import PlagiarismCheck
        from datetime import datetime

        # Create check
        check = PlagiarismCheck(
            user_id=test_user.id,
            text="Sample",
            language="en",
            originality_score=90.0,
            total_matches=0,
            matches=[],
            total_words=10,
            matched_words=0,
            unique_sources=0,
            status="completed",
            completed_at=datetime.utcnow()
        )

        test_db.add(check)
        test_db.commit()
        test_db.refresh(check)

        # Delete
        response = authenticated_client.delete(f"/api/v1/plagiarism/{check.id}")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deleted
        from app.models.plagiarism_check import PlagiarismCheck
        deleted_check = test_db.query(PlagiarismCheck).filter_by(id=check.id).first()
        assert deleted_check is None

    @pytest.mark.integration
    def test_api_error_handling(self, authenticated_client):
        """Test error handling when service fails"""
        with patch('app.api.endpoints.plagiarism.PlagiarismDetectionService') as mock_service:
            # Setup mock to raise exception
            mock_instance = mock_service.return_value
            mock_instance.check_plagiarism = AsyncMock(side_effect=Exception("Service Error"))
            mock_instance.close = AsyncMock()

            # Make request
            response = authenticated_client.post(
                "/api/v1/plagiarism/check",
                json={"text": "Test text " * 50, "language": "en", "check_online": True}
            )

            # Should return 500 error
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestPlagiarismAPIResponseStructure:
    """Test response structure and data types"""

    @pytest.mark.integration
    def test_plagiarism_check_response_structure(self, authenticated_client):
        """Test response structure matches schema"""
        with patch('app.api.endpoints.plagiarism.PlagiarismDetectionService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.check_plagiarism = AsyncMock(return_value={
                "originality_score": 92.5,
                "total_matches": 1,
                "matches": [
                    {
                        "text": "matched text",
                        "source": "Source A",
                        "source_url": "http://example.com",
                        "similarity": 0.8,
                        "start_pos": 0,
                        "end_pos": 100,
                        "type": "high_similarity"
                    }
                ],
                "statistics": {
                    "total_words": 200,
                    "matched_words": 20,
                    "match_percentage": 10.0,
                    "unique_sources": 1,
                    "matches_by_type": {"high_similarity": 1},
                    "highest_similarity": 0.8,
                    "average_similarity": 0.8
                },
                "text_length": 1000,
                "word_count": 200,
                "language": "en"
            })
            mock_instance.close = AsyncMock()

            response = authenticated_client.post(
                "/api/v1/plagiarism/check",
                json={"text": "Test " * 100, "language": "en", "check_online": True}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Validate types
            assert isinstance(data["originality_score"], (int, float))
            assert isinstance(data["total_matches"], int)
            assert isinstance(data["matches"], list)
            assert isinstance(data["statistics"], dict)

            # Validate ranges
            assert 0 <= data["originality_score"] <= 100
            assert data["total_matches"] >= 0

    @pytest.mark.integration
    def test_citation_suggestion_response_structure(self, authenticated_client):
        """Test citation suggestion response structure"""
        with patch('app.api.endpoints.plagiarism.PlagiarismDetectionService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.suggest_citations = AsyncMock(return_value=[
                {
                    "claim": "Test claim",
                    "paper_title": "Paper Title",
                    "authors": ["Author 1", "Author 2"],
                    "year": 2024,
                    "venue": "Conference",
                    "url": "http://example.com",
                    "citation_count": 50,
                    "relevance": 0.9
                }
            ])
            mock_instance.close = AsyncMock()

            response = authenticated_client.post(
                "/api/v1/plagiarism/citations/suggest",
                json={"text": "Research shows this works well."}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert "suggestions" in data
            assert "total_suggestions" in data
            assert isinstance(data["suggestions"], list)
            assert data["total_suggestions"] == len(data["suggestions"])

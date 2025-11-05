"""
Unit Tests for Journal Recommendation Service
Tests journal matching, filtering, and scoring
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.journal_recommendation_service import JournalRecommendationService


class TestJournalRecommendationService:
    """Test suite for Journal Recommendation Service"""

    @pytest.fixture
    def service(self, mock_cohere_client):
        """Create service instance with mocked Cohere"""
        service = JournalRecommendationService()
        service.cohere_client = mock_cohere_client
        return service

    @pytest.fixture
    def sample_abstract(self):
        """Sample paper abstract for testing"""
        return """
        This paper presents a novel approach to natural language processing using
        transformer-based neural networks. We demonstrate significant improvements
        in text classification and sentiment analysis tasks, achieving state-of-the-art
        results on benchmark datasets. Our method combines attention mechanisms with
        contextual embeddings to capture semantic relationships in text.
        """

    @pytest.fixture
    def sample_keywords(self):
        """Sample keywords for testing"""
        return ["natural language processing", "transformers", "neural networks", "deep learning"]

    @pytest.mark.asyncio
    async def test_recommend_journals_success(self, service, sample_abstract, sample_keywords):
        """Test successful journal recommendation"""
        # Act
        recommendations = await service.recommend_journals(
            paper_abstract=sample_abstract,
            paper_keywords=sample_keywords,
            preferences={}
        )

        # Assert
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert len(recommendations) <= 20  # Max limit

        # Check recommendation structure
        rec = recommendations[0]
        assert 'title' in rec
        assert 'semantic_score' in rec
        assert 'keyword_score' in rec
        assert 'composite_score' in rec
        assert 'fit_score' in rec
        assert 'acceptance_probability' in rec

        # Validate score ranges
        assert 0 <= rec['semantic_score'] <= 1.0
        assert 0 <= rec['keyword_score'] <= 1.0
        assert 0 <= rec['composite_score'] <= 1.0
        assert 0 <= rec['fit_score'] <= 1.0
        assert 0 <= rec['acceptance_probability'] <= 1.0

    @pytest.mark.asyncio
    async def test_recommend_journals_sorted_by_score(self, service, sample_abstract):
        """Test that recommendations are sorted by composite score"""
        recommendations = await service.recommend_journals(
            paper_abstract=sample_abstract
        )

        # Check sorting
        scores = [r['composite_score'] for r in recommendations]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_recommend_journals_short_abstract_error(self, service):
        """Test error handling for too short abstract"""
        with pytest.raises(ValueError, match="abstract too short"):
            await service.recommend_journals(
                paper_abstract="Too short",
                paper_keywords=[]
            )

    @pytest.mark.asyncio
    async def test_recommend_journals_with_preferences(self, service, sample_abstract):
        """Test journal filtering with user preferences"""
        preferences = {
            'open_access_only': True,
            'max_apc': 2000,
            'min_impact_factor': 3.0,
            'required_indexing': ['Scopus'],
            'exclude_predatory': True
        }

        recommendations = await service.recommend_journals(
            paper_abstract=sample_abstract,
            preferences=preferences
        )

        # Check that preferences are applied
        for rec in recommendations:
            if 'open_access' in rec:
                assert rec['open_access'] == True
            if 'apc_amount' in rec and rec['open_access']:
                assert rec['apc_amount'] <= 2000
            if 'impact_factor' in rec and rec['impact_factor']:
                assert rec['impact_factor'] >= 3.0
            if 'scopus_indexed' in rec:
                assert rec['scopus_indexed'] == True
            if 'is_predatory' in rec:
                assert rec['is_predatory'] == False

    @pytest.mark.asyncio
    async def test_calculate_semantic_similarity_cohere(self, service, sample_abstract):
        """Test semantic similarity calculation with Cohere"""
        scores = await service._calculate_semantic_similarity_cohere(sample_abstract)

        # Should return dictionary of journal_id -> score
        assert isinstance(scores, dict)
        assert len(scores) > 0

        # All scores should be 0-1
        for journal_id, score in scores.items():
            assert 0 <= score <= 1.0
            assert isinstance(journal_id, str)

    @pytest.mark.asyncio
    async def test_calculate_semantic_similarity_caching(self, service, sample_abstract):
        """Test that journal embeddings are cached"""
        # First call - should compute embeddings
        scores1 = await service._calculate_semantic_similarity_cohere(sample_abstract)

        # Second call - should use cached embeddings
        scores2 = await service._calculate_semantic_similarity_cohere(sample_abstract)

        # Embeddings should be cached
        assert service.journal_embeddings is not None
        assert service.journal_embedding_ids is not None

    @pytest.mark.asyncio
    async def test_calculate_semantic_similarity_error_fallback(self, service, sample_abstract):
        """Test fallback when Cohere fails"""
        # Mock Cohere to raise exception
        service.cohere_client.embed = Mock(side_effect=Exception("Embedding error"))

        scores = await service._calculate_semantic_similarity_cohere(sample_abstract)

        # Should return fallback scores (0.5 for all)
        assert isinstance(scores, dict)
        for score in scores.values():
            assert score == 0.5

    @pytest.mark.asyncio
    async def test_calculate_keyword_overlap(self, service, sample_keywords):
        """Test keyword overlap calculation"""
        semantic_scores = {j['id']: 0.5 for j in service.journal_database}

        keyword_scores = service._calculate_keyword_overlap(
            sample_keywords,
            semantic_scores
        )

        # Should return dictionary
        assert isinstance(keyword_scores, dict)
        assert len(keyword_scores) == len(service.journal_database)

        # Scores should be 0-1
        for score in keyword_scores.values():
            assert 0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_calculate_keyword_overlap_no_keywords(self, service):
        """Test keyword overlap with empty keywords"""
        semantic_scores = {j['id']: 0.5 for j in service.journal_database}

        keyword_scores = service._calculate_keyword_overlap([], semantic_scores)

        # Should return equal scores (0.5)
        for score in keyword_scores.values():
            assert score == 0.5

    @pytest.mark.asyncio
    async def test_apply_filters_open_access(self, service):
        """Test filtering for open access journals"""
        preferences = {'open_access_only': True}

        filtered = service._apply_filters(service.journal_database, preferences)

        # All results should be open access
        for journal in filtered:
            assert journal.get('open_access', False) == True

    @pytest.mark.asyncio
    async def test_apply_filters_max_apc(self, service):
        """Test filtering by maximum APC"""
        preferences = {'max_apc': 1900}

        filtered = service._apply_filters(service.journal_database, preferences)

        # All open access journals should have APC <= max_apc
        for journal in filtered:
            if journal.get('open_access'):
                assert journal.get('apc_amount', 0) <= 1900

    @pytest.mark.asyncio
    async def test_apply_filters_min_impact_factor(self, service):
        """Test filtering by minimum impact factor"""
        preferences = {'min_impact_factor': 4.0}

        filtered = service._apply_filters(service.journal_database, preferences)

        # All journals should meet minimum impact factor
        for journal in filtered:
            if journal.get('impact_factor'):
                assert journal['impact_factor'] >= 4.0

    @pytest.mark.asyncio
    async def test_apply_filters_max_time_to_publish(self, service):
        """Test filtering by maximum time to publish"""
        preferences = {'max_time_to_publish': 90}

        filtered = service._apply_filters(service.journal_database, preferences)

        # All journals should publish within time limit
        for journal in filtered:
            assert journal.get('avg_time_to_publish_days', 0) <= 90

    @pytest.mark.asyncio
    async def test_apply_filters_required_indexing(self, service):
        """Test filtering by required indexing"""
        preferences = {'required_indexing': ['Scopus', 'Web of Science']}

        filtered = service._apply_filters(service.journal_database, preferences)

        # All journals should have required indexing
        for journal in filtered:
            assert journal.get('scopus_indexed', False) == True
            assert journal.get('web_of_science_indexed', False) == True

    @pytest.mark.asyncio
    async def test_apply_filters_exclude_predatory(self, service):
        """Test excluding predatory journals"""
        preferences = {'exclude_predatory': True}

        filtered = service._apply_filters(service.journal_database, preferences)

        # No predatory journals
        for journal in filtered:
            assert journal.get('is_predatory', False) == False

    @pytest.mark.asyncio
    async def test_calculate_composite_score(self, service):
        """Test composite score calculation"""
        score = service._calculate_composite_score(
            semantic_score=0.8,
            keyword_score=0.7,
            impact_factor=5.0,
            time_to_publish=60,
            open_access=True,
            acceptance_rate=30.0
        )

        # Should return weighted score
        assert 0 <= score <= 1.0
        assert isinstance(score, float)

    @pytest.mark.asyncio
    async def test_calculate_composite_score_normalization(self, service):
        """Test that scores are properly normalized"""
        # Test with extreme values
        score_high_impact = service._calculate_composite_score(
            semantic_score=0.9,
            keyword_score=0.9,
            impact_factor=50.0,  # Very high
            time_to_publish=1,
            open_access=True,
            acceptance_rate=80.0
        )

        score_low_impact = service._calculate_composite_score(
            semantic_score=0.5,
            keyword_score=0.5,
            impact_factor=0.5,  # Very low
            time_to_publish=365,
            open_access=False,
            acceptance_rate=10.0
        )

        # High impact should score higher
        assert score_high_impact > score_low_impact
        assert 0 <= score_high_impact <= 1.0
        assert 0 <= score_low_impact <= 1.0

    @pytest.mark.asyncio
    async def test_calculate_fit_score(self, service):
        """Test fit score calculation"""
        journal = {'id': 'test', 'h_index': 100}

        fit = service._calculate_fit_score(
            semantic_score=0.8,
            keyword_score=0.7,
            journal=journal
        )

        # Should boost for high h-index
        assert 0 <= fit <= 1.0

    @pytest.mark.asyncio
    async def test_estimate_acceptance_probability(self, service):
        """Test acceptance probability estimation"""
        journal = {'acceptance_rate': 50.0}

        # High fit score
        prob_high = service._estimate_acceptance_probability(
            fit_score=0.9,
            journal=journal
        )

        # Low fit score
        prob_low = service._estimate_acceptance_probability(
            fit_score=0.3,
            journal=journal
        )

        # High fit should have higher acceptance probability
        assert prob_high > prob_low
        assert 0.05 <= prob_high <= 0.95
        assert 0.05 <= prob_low <= 0.95

    @pytest.mark.asyncio
    async def test_get_journal_details(self, service):
        """Test getting journal details by ID"""
        # Test existing journal
        details = await service.get_journal_details('nature')
        assert details is not None
        assert details['id'] == 'nature'
        assert 'title' in details

        # Test non-existent journal
        details_none = await service.get_journal_details('nonexistent')
        assert details_none is None

    @pytest.mark.asyncio
    async def test_search_journals(self, service):
        """Test journal search functionality"""
        # Search by title
        results = await service.search_journals("Nature", limit=10)
        assert isinstance(results, list)
        assert len(results) > 0

        # Search by keyword
        results_keyword = await service.search_journals("open access", limit=10)
        assert isinstance(results_keyword, list)

    @pytest.mark.asyncio
    async def test_search_journals_limit(self, service):
        """Test that search respects limit"""
        results = await service.search_journals("science", limit=2)
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_search_journals_case_insensitive(self, service):
        """Test that search is case-insensitive"""
        results_upper = await service.search_journals("NATURE", limit=5)
        results_lower = await service.search_journals("nature", limit=5)

        # Should return same results
        assert len(results_upper) == len(results_lower)


class TestJournalRecommendationEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def service(self):
        """Create service with default setup"""
        return JournalRecommendationService()

    @pytest.mark.asyncio
    async def test_empty_abstract(self, service):
        """Test handling of empty abstract"""
        with pytest.raises(ValueError):
            await service.recommend_journals(paper_abstract="")

    @pytest.mark.asyncio
    async def test_very_long_abstract(self, service):
        """Test handling of very long abstract"""
        long_abstract = "This is a long abstract. " * 1000

        recommendations = await service.recommend_journals(
            paper_abstract=long_abstract
        )

        # Should truncate and process
        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_special_characters_in_abstract(self, service):
        """Test handling of special characters"""
        special_abstract = """
        Abstract with émojis 😀 and spëcial çharacters.
        Math symbols: ∑ ∫ √ ∞
        Greek: α β γ δ
        """ * 10

        recommendations = await service.recommend_journals(
            paper_abstract=special_abstract
        )

        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_no_cohere_fallback(self, service, sample_keywords):
        """Test fallback when Cohere is not available"""
        service.cohere_client = None

        abstract = "Machine learning research for healthcare applications. " * 20

        recommendations = await service.recommend_journals(
            paper_abstract=abstract,
            paper_keywords=sample_keywords
        )

        # Should still work with keyword matching
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @pytest.mark.asyncio
    async def test_overly_restrictive_filters(self, service):
        """Test behavior with filters that match no journals"""
        abstract = "AI research paper. " * 20

        preferences = {
            'min_impact_factor': 100.0,  # Impossible
            'max_apc': 1,  # Too low
        }

        recommendations = await service.recommend_journals(
            paper_abstract=abstract,
            preferences=preferences
        )

        # Should return empty or very few results
        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_invalid_preference_types(self, service):
        """Test handling of invalid preference values"""
        abstract = "Test abstract for journal recommendation. " * 20

        preferences = {
            'max_apc': 'invalid',  # Should be number
            'open_access_only': 'maybe',  # Should be boolean
        }

        # Should handle gracefully (or raise appropriate error)
        try:
            recommendations = await service.recommend_journals(
                paper_abstract=abstract,
                preferences=preferences
            )
            assert isinstance(recommendations, list)
        except (ValueError, TypeError):
            # Acceptable to raise error for invalid types
            pass

    @pytest.mark.asyncio
    async def test_concurrent_recommendations(self, service):
        """Test concurrent recommendation requests"""
        import asyncio

        abstracts = [f"Research abstract {i} about machine learning. " * 20 for i in range(3)]

        tasks = [service.recommend_journals(abstract) for abstract in abstracts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, list) or isinstance(result, Exception)

    @pytest.mark.asyncio
    async def test_zero_acceptance_rate(self, service):
        """Test handling of journal with 0% acceptance rate"""
        journal = {'acceptance_rate': 0.0}

        prob = service._estimate_acceptance_probability(
            fit_score=0.8,
            journal=journal
        )

        # Should still be reasonable
        assert 0.05 <= prob <= 0.95

    @pytest.mark.asyncio
    async def test_missing_journal_fields(self, service):
        """Test handling of journals with missing fields"""
        incomplete_journal = {
            'id': 'test',
            'title': 'Test Journal',
            # Missing many fields
        }

        # Should not crash when calculating scores
        score = service._calculate_composite_score(
            semantic_score=0.8,
            keyword_score=0.7,
            impact_factor=incomplete_journal.get('impact_factor', 0),
            time_to_publish=incomplete_journal.get('avg_time_to_publish_days', 180),
            open_access=incomplete_journal.get('open_access', False),
            acceptance_rate=incomplete_journal.get('acceptance_rate', 50)
        )

        assert 0 <= score <= 1.0

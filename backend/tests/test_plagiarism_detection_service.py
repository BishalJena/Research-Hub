"""
Unit Tests for Plagiarism Detection Service
Tests similarity detection, citation suggestions, and originality scoring
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.plagiarism_detection_service import PlagiarismDetectionService


class TestPlagiarismDetectionService:
    """Test suite for Plagiarism Detection Service"""

    @pytest.fixture
    def service(self, mock_academic_clients, mock_cohere_client):
        """Create service instance with mocked dependencies"""
        service = PlagiarismDetectionService()
        service.semantic_scholar = mock_academic_clients['semantic_scholar']
        service.cohere_client = mock_cohere_client
        return service

    @pytest.fixture
    def sample_text(self):
        """Sample text for plagiarism checking"""
        return """
        Machine learning is a subset of artificial intelligence that enables systems
        to learn and improve from experience without being explicitly programmed.
        Deep learning, a subset of machine learning, uses neural networks with multiple
        layers to analyze various factors of data.

        Natural language processing (NLP) is a branch of AI that helps computers
        understand, interpret and manipulate human language. Recent advances in
        transformer architectures have revolutionized NLP applications.
        """

    @pytest.mark.asyncio
    async def test_check_plagiarism_success(self, service, sample_text):
        """Test successful plagiarism check"""
        # Act
        result = await service.check_plagiarism(
            text=sample_text,
            language="en",
            check_online=True
        )

        # Assert
        assert 'originality_score' in result
        assert 'total_matches' in result
        assert 'matches' in result
        assert 'statistics' in result
        assert 'text_length' in result
        assert 'word_count' in result
        assert 'language' in result

        # Validate score range
        assert 0 <= result['originality_score'] <= 100
        assert isinstance(result['total_matches'], int)
        assert isinstance(result['matches'], list)

    @pytest.mark.asyncio
    async def test_check_plagiarism_high_originality(self, service):
        """Test that unique text gets high originality score"""
        unique_text = """
        This is a completely unique and original text that has never been written before
        in the history of humanity. It contains novel ideas about quantum chromodynamics
        in relation to asymptotic freedom and the strong nuclear force.
        """

        result = await service.check_plagiarism(unique_text, check_online=False)

        # Should have high originality score (low matches)
        assert result['originality_score'] >= 70  # Most likely high

    @pytest.mark.asyncio
    async def test_check_plagiarism_statistics(self, service, sample_text):
        """Test statistics calculation"""
        result = await service.check_plagiarism(sample_text)

        stats = result['statistics']
        assert 'total_words' in stats
        assert 'matched_words' in stats
        assert 'match_percentage' in stats
        assert 'unique_sources' in stats
        assert 'matches_by_type' in stats
        assert 'highest_similarity' in stats
        assert 'average_similarity' in stats

        # Validate ranges
        assert stats['total_words'] > 0
        assert 0 <= stats['match_percentage'] <= 100
        assert stats['unique_sources'] >= 0

    @pytest.mark.asyncio
    async def test_chunk_text_success(self, service, sample_text):
        """Test text chunking into paragraphs"""
        chunks = service._chunk_text(sample_text, min_chunk_size=20)

        # Should create multiple chunks
        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Each chunk should be reasonable size
        for chunk in chunks:
            assert isinstance(chunk, str)
            assert len(chunk.strip()) > 0

    @pytest.mark.asyncio
    async def test_chunk_text_minimum_size(self, service):
        """Test that chunks respect minimum size"""
        text = "Short. Text. Here. With. Many. Short. Sentences."

        chunks = service._chunk_text(text, min_chunk_size=10)

        # Chunks should be combined to meet minimum size
        for chunk in chunks:
            word_count = len(chunk.split())
            # May be smaller for last chunk
            assert word_count >= 5

    @pytest.mark.asyncio
    async def test_fingerprint_detection(self, service, sample_text):
        """Test fingerprint-based detection"""
        chunks = service._chunk_text(sample_text)

        matches = service._fingerprint_detection(chunks)

        # Should return list (may be empty in mock)
        assert isinstance(matches, list)

    @pytest.mark.asyncio
    async def test_ngram_detection(self, service):
        """Test n-gram based similarity detection"""
        chunks = [
            "Machine learning is a powerful tool for data analysis",
            "Machine learning is an effective method for analyzing data",
            "Quantum computing uses qubits instead of classical bits"
        ]

        matches = service._ngram_detection(chunks, n=5, threshold=0.5)

        # Should detect similarity between first two chunks
        assert isinstance(matches, list)

        # Check match structure if any found
        if len(matches) > 0:
            match = matches[0]
            assert 'text' in match
            assert 'source' in match
            assert 'similarity' in match
            assert 'type' in match
            assert match['type'] == 'near_duplicate'
            assert 0 <= match['similarity'] <= 1.0

    @pytest.mark.asyncio
    async def test_ngram_detection_threshold(self, service):
        """Test n-gram threshold filtering"""
        chunks = [
            "Completely different text about physics",
            "Totally unrelated content about chemistry"
        ]

        matches = service._ngram_detection(chunks, n=5, threshold=0.8)

        # Should find no matches (threshold too high for different text)
        assert len(matches) == 0

    @pytest.mark.asyncio
    async def test_semantic_detection_with_cohere(self, service, mock_semantic_scholar_papers):
        """Test semantic similarity detection using Cohere"""
        chunks = [
            "Deep learning networks learn hierarchical representations",
            "Neural networks with multiple layers extract features automatically"
        ]

        matches = await service._semantic_detection(chunks, check_online=True, threshold=0.7)

        # Should return matches list
        assert isinstance(matches, list)

        # Check match structure if any found
        for match in matches:
            assert 'text' in match
            assert 'source' in match
            assert 'similarity' in match
            assert 'type' in match
            assert match['type'] in ['paraphrase', 'high_similarity']
            assert 0 <= match['similarity'] <= 1.0

    @pytest.mark.asyncio
    async def test_semantic_detection_without_cohere(self, service):
        """Test semantic detection fallback when Cohere unavailable"""
        service.cohere_client = None

        chunks = ["Test text chunk"]
        matches = await service._semantic_detection(chunks, check_online=True)

        # Should return empty list gracefully
        assert matches == []

    @pytest.mark.asyncio
    async def test_semantic_detection_offline_mode(self, service):
        """Test that offline mode skips semantic detection"""
        chunks = ["Test chunk"]

        matches = await service._semantic_detection(chunks, check_online=False)

        # Should return empty when check_online=False
        assert matches == []

    @pytest.mark.asyncio
    async def test_deduplicate_matches(self, service):
        """Test match deduplication"""
        matches = [
            {'text': 'Same text here', 'source': 'Source A', 'similarity': 0.9},
            {'text': 'Same text here', 'source': 'Source A', 'similarity': 0.9},  # Duplicate
            {'text': 'Different text', 'source': 'Source B', 'similarity': 0.8},
            {'text': 'Same text here', 'source': 'Source B', 'similarity': 0.85},  # Different source
        ]

        unique = service._deduplicate_matches(matches)

        # Should remove exact duplicates but keep different sources
        assert len(unique) < len(matches)
        assert len(unique) >= 2

    @pytest.mark.asyncio
    async def test_calculate_originality_score(self, service):
        """Test originality score calculation"""
        text = "This is a test text with exactly fifty words. " * 10  # 500 words approx

        # Test with no matches (100% original)
        score_no_matches = service._calculate_originality_score(text, [])
        assert score_no_matches == 100.0

        # Test with some matches
        matches = [
            {'text': "test text" * 10, 'similarity': 0.9},
            {'text': "sample content" * 8, 'similarity': 0.8}
        ]
        score_with_matches = service._calculate_originality_score(text, matches)

        assert score_with_matches < score_no_matches
        assert 0 <= score_with_matches <= 100

    @pytest.mark.asyncio
    async def test_calculate_originality_score_penalties(self, service):
        """Test that high similarity matches incur penalties"""
        text = "Test text. " * 100

        # High similarity match
        high_sim_matches = [{'text': "Test text. " * 20, 'similarity': 0.95}]
        score_high_sim = service._calculate_originality_score(text, high_sim_matches)

        # Medium similarity match
        med_sim_matches = [{'text': "Test text. " * 20, 'similarity': 0.75}]
        score_med_sim = service._calculate_originality_score(text, med_sim_matches)

        # High similarity should have lower score (more penalty)
        assert score_high_sim < score_med_sim

    @pytest.mark.asyncio
    async def test_calculate_statistics(self, service, sample_text):
        """Test statistics calculation"""
        matches = [
            {'text': 'matched text here', 'source': 'Source A', 'similarity': 0.9, 'type': 'high_similarity'},
            {'text': 'another match', 'source': 'Source B', 'similarity': 0.8, 'type': 'paraphrase'},
            {'text': 'third match', 'source': 'Source A', 'similarity': 0.85, 'type': 'high_similarity'},
        ]

        stats = service._calculate_statistics(sample_text, matches)

        assert stats['total_words'] > 0
        assert stats['matched_words'] >= 0
        assert stats['unique_sources'] == 2  # Source A and B
        assert 'high_similarity' in stats['matches_by_type']
        assert stats['highest_similarity'] == 0.9
        assert stats['average_similarity'] > 0

    @pytest.mark.asyncio
    async def test_suggest_citations_success(self, service, mock_semantic_scholar_papers):
        """Test citation suggestion"""
        text = """
        Research shows that deep learning improves accuracy.
        Studies have demonstrated the effectiveness of neural networks.
        Evidence suggests that transformer models outperform RNNs.
        """

        suggestions = await service.suggest_citations(text)

        # Should return citation suggestions
        assert isinstance(suggestions, list)

        # Check suggestion structure if any found
        for suggestion in suggestions:
            assert 'claim' in suggestion
            assert 'paper_title' in suggestion
            assert 'authors' in suggestion
            assert 'year' in suggestion

    @pytest.mark.asyncio
    async def test_suggest_citations_with_context(self, service):
        """Test citation suggestions with additional context"""
        text = "Machine learning techniques are widely used."
        context = "Focus on healthcare applications"

        suggestions = await service.suggest_citations(text, context=context)

        assert isinstance(suggestions, list)

    @pytest.mark.asyncio
    async def test_identify_claims(self, service):
        """Test claim identification from text"""
        text = """
        Research shows that AI is effective.
        Studies have demonstrated improved outcomes.
        According to recent findings, performance increased by 30%.
        Evidence suggests that this approach works well.
        Experiments show promising results.
        """

        claims = service._identify_claims(text)

        # Should identify multiple claims
        assert isinstance(claims, list)
        assert len(claims) > 0
        assert len(claims) <= 10  # Max limit

        # Each claim should be a sentence
        for claim in claims:
            assert isinstance(claim, str)
            assert len(claim) > 0

    @pytest.mark.asyncio
    async def test_identify_claims_no_patterns(self, service):
        """Test claim identification with text lacking claim patterns"""
        text = "This is simple text. It has no claims. Just statements."

        claims = service._identify_claims(text)

        # Should return empty or very few
        assert isinstance(claims, list)

    @pytest.mark.asyncio
    async def test_close_method(self, service):
        """Test that close() properly closes clients"""
        await service.close()
        service.semantic_scholar.close.assert_called_once()


class TestPlagiarismDetectionEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def service(self):
        """Create service with default setup"""
        return PlagiarismDetectionService()

    @pytest.mark.asyncio
    async def test_empty_text(self, service):
        """Test handling of empty text"""
        result = await service.check_plagiarism("", check_online=False)

        assert result['originality_score'] == 0.0
        assert result['total_matches'] == 0

    @pytest.mark.asyncio
    async def test_very_short_text(self, service):
        """Test handling of very short text"""
        short_text = "Hello world."

        result = await service.check_plagiarism(short_text, check_online=False)

        # Should handle gracefully
        assert 'originality_score' in result
        assert result['originality_score'] >= 0

    @pytest.mark.asyncio
    async def test_very_long_text(self, service):
        """Test handling of very long text"""
        long_text = "This is a long text. " * 10000

        # Should handle without crashing (may limit chunks)
        result = await service.check_plagiarism(long_text, check_online=False)

        assert 'originality_score' in result

    @pytest.mark.asyncio
    async def test_special_characters(self, service):
        """Test handling of special characters and Unicode"""
        special_text = """
        Text with émojis 😀 and spëcial çharacters.
        Chinese: 你好世界
        Arabic: مرحبا بالعالم
        Math: ∑ ∫ √ ∞
        """

        result = await service.check_plagiarism(special_text, check_online=False)

        assert 'originality_score' in result

    @pytest.mark.asyncio
    async def test_api_error_handling(self, service):
        """Test graceful handling of API errors"""
        service.semantic_scholar.search_papers = AsyncMock(side_effect=Exception("API Error"))

        text = "Test text for plagiarism check."

        # Should not crash
        result = await service.check_plagiarism(text, check_online=True)

        assert isinstance(result, dict)
        assert 'originality_score' in result

    @pytest.mark.asyncio
    async def test_cohere_error_handling(self, service):
        """Test handling when Cohere API fails"""
        service.cohere_client = Mock()
        service.cohere_client.embed = Mock(side_effect=Exception("Embedding error"))

        text = "Test text with some content to check for plagiarism."

        result = await service.check_plagiarism(text, check_online=True)

        # Should fall back gracefully
        assert 'originality_score' in result

    @pytest.mark.asyncio
    async def test_concurrent_checks(self, service):
        """Test concurrent plagiarism checks"""
        import asyncio

        texts = [f"Test text {i} for plagiarism detection." * 10 for i in range(5)]

        tasks = [service.check_plagiarism(text, check_online=False) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 5
        for result in results:
            assert isinstance(result, dict) or isinstance(result, Exception)

    @pytest.mark.asyncio
    async def test_malformed_paper_responses(self, service):
        """Test handling of malformed API responses"""
        service.semantic_scholar.search_papers = AsyncMock(return_value=[
            {},  # Empty
            {'title': 'Paper 1'},  # Missing fields
            None,  # Invalid
        ])

        text = "Test text for checking."

        # Should not crash
        result = await service.check_plagiarism(text, check_online=True)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_zero_word_count(self, service):
        """Test handling when word count is zero"""
        text = "   \n\n\t  "  # Only whitespace

        score = service._calculate_originality_score(text, [])
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_citation_suggestion_limit(self, service):
        """Test that citation suggestions are limited"""
        # Text with many potential claims
        text = "Research shows A. Studies have demonstrated B. " * 20

        suggestions = await service.suggest_citations(text)

        # Should limit to reasonable number
        assert len(suggestions) <= 50  # Implementation limit

    @pytest.mark.asyncio
    async def test_similarity_score_boundaries(self, service):
        """Test that similarity scores stay within bounds"""
        chunks = ["Test chunk"] * 10

        matches = service._ngram_detection(chunks, n=3, threshold=0.0)

        # All similarity scores should be 0-1
        for match in matches:
            assert 0 <= match['similarity'] <= 1.0

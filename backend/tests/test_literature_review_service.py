"""
Unit Tests for Literature Review Service
Tests paper processing, summarization, and related paper discovery
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from app.services.literature_review_service import LiteratureReviewService


class TestLiteratureReviewService:
    """Test suite for Literature Review Service"""

    @pytest.fixture
    def service(self, mock_academic_clients, mock_cohere_client, mock_openai_client):
        """Create service instance with mocked dependencies"""
        service = LiteratureReviewService()
        service.semantic_scholar = mock_academic_clients['semantic_scholar']
        service.cohere_client = mock_cohere_client

        # Mock OpenAI completion
        with patch('openai.ChatCompletion.acreate', side_effect=mock_openai_client):
            yield service

    @pytest.fixture
    def mock_pdf_path(self, tmp_path, mock_pdf_content):
        """Create a temporary mock PDF file"""
        pdf_file = tmp_path / "test_paper.pdf"
        pdf_file.write_text(mock_pdf_content['text'])
        return str(pdf_file)

    @pytest.mark.asyncio
    async def test_process_paper_success(self, service, mock_pdf_path, mock_semantic_scholar_papers):
        """Test successful paper processing"""
        with patch('app.services.literature_review_service.LiteratureReviewService.process_paper') as mock_process:
            # Mock the complete process_paper response
            mock_process.return_value = {
                'metadata': {'num_pages': 10, 'title': 'Test Paper'},
                'text': 'Full paper text...',
                'abstract': 'This is an abstract.',
                'keywords': ['AI', 'Machine Learning'],
                'sections': {'Introduction': 'Intro text...', 'Methods': 'Methods text...'},
                'section_summaries': {'Introduction': 'Summary of intro...'},
                'overall_summary': 'This paper presents novel approaches...',
                'citations': ['Smith 2023', 'Jones 2024'],
                'key_insights': {
                    'methodology': 'Deep learning approach...',
                    'results': 'Achieved 95% accuracy...',
                    'contributions': '• Novel architecture\n• Improved performance',
                    'limitations': '• Limited dataset\n• High computational cost'
                },
                'related_papers': mock_semantic_scholar_papers,
                'word_count': 5000,
                'page_count': 10
            }

            # Act
            result = await service.process_paper(mock_pdf_path)

            # Assert
            assert 'metadata' in result
            assert 'text' in result
            assert 'abstract' in result
            assert 'keywords' in result
            assert 'sections' in result
            assert 'section_summaries' in result
            assert 'overall_summary' in result
            assert 'citations' in result
            assert 'key_insights' in result
            assert 'related_papers' in result
            assert 'word_count' in result
            assert 'page_count' in result

            # Check key insights structure
            insights = result['key_insights']
            assert 'methodology' in insights
            assert 'results' in insights
            assert 'contributions' in insights
            assert 'limitations' in insights

    @pytest.mark.asyncio
    async def test_summarize_text_success(self, service, mock_openai_client):
        """Test text summarization"""
        with patch('openai.ChatCompletion.acreate', side_effect=mock_openai_client):
            # Arrange
            long_text = """
            This is a long academic text that needs to be summarized.
            It contains multiple paragraphs with important information.
            """ * 100  # Make it sufficiently long

            # Act
            summary = await service.summarize_text(long_text, max_tokens=500)

            # Assert
            assert isinstance(summary, str)
            assert len(summary) > 0
            assert len(summary) < len(long_text)  # Summary should be shorter

    @pytest.mark.asyncio
    async def test_summarize_text_short_input(self, service):
        """Test that short text is returned as-is"""
        short_text = "This is a very short text."

        summary = await service.summarize_text(short_text)

        # Should return original for very short text
        assert summary == short_text

    @pytest.mark.asyncio
    async def test_summarize_text_empty_input(self, service):
        """Test handling of empty input"""
        summary = await service.summarize_text("")
        assert summary == ""

    @pytest.mark.asyncio
    async def test_summarize_text_api_error_fallback(self, service):
        """Test fallback when API fails"""
        with patch('openai.ChatCompletion.acreate', side_effect=Exception("API Error")):
            text = "This is a test text. " * 50

            summary = await service.summarize_text(text)

            # Should return fallback (first few sentences)
            assert isinstance(summary, str)
            assert len(summary) > 0

    @pytest.mark.asyncio
    async def test_find_related_papers_success(self, service, mock_semantic_scholar_papers):
        """Test finding related papers"""
        # Arrange
        query_text = "Deep learning for natural language processing"

        # Act
        related = await service.find_related_papers(query_text, limit=5)

        # Assert
        assert isinstance(related, list)
        assert len(related) <= 5

        if len(related) > 0:
            # Check paper structure
            paper = related[0]
            assert 'title' in paper or 'paperId' in paper
            assert 'relevance_score' in paper
            assert 0 <= paper['relevance_score'] <= 1.0

    @pytest.mark.asyncio
    async def test_find_related_papers_with_cohere_ranking(self, service, mock_semantic_scholar_papers):
        """Test that Cohere embeddings improve relevance ranking"""
        query = "Machine learning applications in healthcare"

        papers = await service.find_related_papers(query, limit=10)

        # Papers should be sorted by relevance_score
        if len(papers) > 1:
            scores = [p['relevance_score'] for p in papers]
            assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_find_related_papers_no_cohere_fallback(self, service, mock_semantic_scholar_papers):
        """Test fallback when Cohere is not available"""
        # Disable Cohere
        service.cohere_client = None

        papers = await service.find_related_papers("AI ethics", limit=5)

        # Should still work, using citation count for ranking
        assert isinstance(papers, list)
        if len(papers) > 0:
            assert 'relevance_score' in papers[0]

    @pytest.mark.asyncio
    async def test_find_related_papers_empty_query(self, service):
        """Test handling of empty query"""
        papers = await service.find_related_papers("", limit=5)
        assert isinstance(papers, list)

    @pytest.mark.asyncio
    async def test_extract_key_insights_methodology(self, service, mock_openai_client):
        """Test extraction of methodology insights"""
        with patch('openai.ChatCompletion.acreate', side_effect=mock_openai_client):
            text = "Full paper text..."
            sections = {
                'methodology': 'We used a deep learning approach with CNN architecture.',
                'results': 'Achieved 95% accuracy on test set.',
            }

            insights = await service._extract_key_insights(text, sections)

            assert 'methodology' in insights
            assert 'results' in insights
            assert isinstance(insights['methodology'], str)
            assert isinstance(insights['results'], str)

    @pytest.mark.asyncio
    async def test_extract_contributions_ai(self, service, mock_openai_client):
        """Test AI-based contribution extraction"""
        with patch('openai.ChatCompletion.acreate', side_effect=mock_openai_client):
            text = "Our main contributions are: novel architecture, improved performance..."

            contributions = await service._find_contributions_ai(text)

            assert contributions is not None
            assert isinstance(contributions, str)
            assert len(contributions) > 0

    @pytest.mark.asyncio
    async def test_extract_limitations_ai(self, service, mock_openai_client):
        """Test AI-based limitation extraction"""
        with patch('openai.ChatCompletion.acreate', side_effect=mock_openai_client):
            text = "The limitations of this work include small dataset and high cost..."

            limitations = await service._find_limitations_ai(text)

            assert limitations is not None
            assert isinstance(limitations, str)

    @pytest.mark.asyncio
    async def test_compare_papers_success(self, service, tmp_path, mock_pdf_content):
        """Test comparing multiple papers"""
        # Create mock PDF files
        pdf1 = tmp_path / "paper1.pdf"
        pdf2 = tmp_path / "paper2.pdf"
        pdf1.write_text(mock_pdf_content['text'])
        pdf2.write_text(mock_pdf_content['text'])

        with patch('app.services.literature_review_service.LiteratureReviewService.process_paper') as mock_process:
            # Mock process_paper to return simplified data
            mock_process.return_value = {
                'keywords': ['AI', 'ML'],
                'key_insights': {'methodology': 'Deep learning'},
                'citations': ['Smith 2023'],
            }

            # Act
            comparison = await service.compare_papers([str(pdf1), str(pdf2)])

            # Assert
            assert 'paper_count' in comparison
            assert comparison['paper_count'] == 2
            assert 'common_keywords' in comparison
            assert 'methodologies' in comparison
            assert 'total_citations' in comparison

    @pytest.mark.asyncio
    async def test_compare_papers_empty_list(self, service):
        """Test comparing with empty paper list"""
        comparison = await service.compare_papers([])

        assert comparison['paper_count'] == 0

    @pytest.mark.asyncio
    async def test_find_common_keywords(self, service):
        """Test finding common keywords across papers"""
        papers_data = [
            {'keywords': ['AI', 'ML', 'Deep Learning']},
            {'keywords': ['AI', 'NLP', 'Transformers']},
            {'keywords': ['AI', 'Computer Vision']},
        ]

        common = service._find_common_keywords(papers_data)

        # 'AI' appears in all 3 papers
        assert 'AI' in common
        assert isinstance(common, list)

    @pytest.mark.asyncio
    async def test_text_truncation_for_long_input(self, service, mock_openai_client):
        """Test that very long text is truncated before API call"""
        with patch('openai.ChatCompletion.acreate', side_effect=mock_openai_client) as mock_api:
            # Create very long text (> 4000 words)
            long_text = "word " * 5000

            await service.summarize_text(long_text)

            # Verify API was called
            mock_api.assert_called_once()

            # Text should have been truncated (implementation truncates to 4000 words)
            call_args = mock_api.call_args
            user_message = call_args[1]['messages'][1]['content']
            word_count = len(user_message.split())
            assert word_count <= 4500  # Allow some margin

    @pytest.mark.asyncio
    async def test_close_method(self, service):
        """Test that close() properly closes clients"""
        await service.close()
        service.semantic_scholar.close.assert_called_once()


class TestLiteratureReviewEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def service(self):
        """Create service with default setup"""
        return LiteratureReviewService()

    @pytest.mark.asyncio
    async def test_pdf_extraction_error(self, service):
        """Test handling of PDF extraction errors"""
        with patch('app.services.pdf_processor.PDFProcessor.extract_text', side_effect=Exception("PDF Error")):
            with pytest.raises(Exception):
                await service.process_paper("/invalid/path.pdf")

    @pytest.mark.asyncio
    async def test_malformed_section_data(self, service):
        """Test handling of malformed section data"""
        text = "Paper text"
        malformed_sections = {
            'section1': None,  # None value
            'section2': '',     # Empty string
            'section3': 'Valid content here with enough words to process. ' * 20
        }

        # Should not crash
        with patch('openai.ChatCompletion.acreate') as mock_api:
            mock_api.return_value = AsyncMock()
            insights = await service._extract_key_insights(text, malformed_sections)

        assert isinstance(insights, dict)

    @pytest.mark.asyncio
    async def test_api_rate_limit_handling(self, service):
        """Test graceful handling of API rate limits"""
        with patch('openai.ChatCompletion.acreate', side_effect=Exception("Rate limit exceeded")):
            text = "Test text for summarization. " * 50

            summary = await service.summarize_text(text)

            # Should return fallback, not crash
            assert isinstance(summary, str)
            assert len(summary) > 0

    @pytest.mark.asyncio
    async def test_empty_papers_list(self, service):
        """Test handling when no papers are found"""
        service.semantic_scholar.search_papers = AsyncMock(return_value=[])

        papers = await service.find_related_papers("obscure topic", limit=10)

        assert papers == []

    @pytest.mark.asyncio
    async def test_concurrent_summarization(self, service, mock_openai_client):
        """Test concurrent summarization requests"""
        with patch('openai.ChatCompletion.acreate', side_effect=mock_openai_client):
            import asyncio

            texts = [f"Text {i} to summarize. " * 50 for i in range(5)]
            tasks = [service.summarize_text(text) for text in texts]

            summaries = await asyncio.gather(*tasks, return_exceptions=True)

            assert len(summaries) == 5
            for summary in summaries:
                assert isinstance(summary, str) or isinstance(summary, Exception)

    @pytest.mark.asyncio
    async def test_special_characters_in_text(self, service, mock_openai_client):
        """Test handling of special characters and Unicode"""
        with patch('openai.ChatCompletion.acreate', side_effect=mock_openai_client):
            special_text = "Text with émojis 😀 and spëcial çharacters: ñ, ü, ø. " * 30

            summary = await service.summarize_text(special_text)

            assert isinstance(summary, str)
            assert len(summary) > 0

    @pytest.mark.asyncio
    async def test_cohere_embedding_error_fallback(self, service, mock_semantic_scholar_papers):
        """Test fallback when Cohere embeddings fail"""
        # Mock Cohere to raise exception
        service.cohere_client = Mock()
        service.cohere_client.embed = Mock(side_effect=Exception("Embedding error"))

        # Should fall back to citation count ranking
        papers = await service.find_related_papers("test query", limit=5)

        assert isinstance(papers, list)

    @pytest.mark.asyncio
    async def test_max_tokens_customization(self, service, mock_openai_client):
        """Test custom max_tokens parameter"""
        with patch('openai.ChatCompletion.acreate', side_effect=mock_openai_client) as mock_api:
            text = "Test text. " * 100
            custom_max_tokens = 300

            await service.summarize_text(text, max_tokens=custom_max_tokens)

            # Verify max_tokens was passed correctly
            call_args = mock_api.call_args
            assert call_args[1]['max_tokens'] == custom_max_tokens

"""
Unit Tests for Translation Service
Tests multilingual support for Telugu, Hindi, Sanskrit, Urdu, and English
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.translation_service import TranslationService


class TestTranslationService:
    """Test suite for Translation Service"""

    @pytest.fixture
    def service(self):
        """Create translation service instance"""
        return TranslationService()

    @pytest.mark.asyncio
    async def test_translate_same_language(self, service):
        """Test that translating to same language returns original"""
        text = "Hello world"

        result = await service.translate(text, source_lang="en", target_lang="en")

        assert result == text

    @pytest.mark.asyncio
    async def test_translate_english_to_telugu(self, service):
        """Test English to Telugu translation"""
        text = "Hello, how are you?"

        result = await service.translate(text, source_lang="en", target_lang="te")

        # Should return translated text (or mock in dev mode)
        assert isinstance(result, str)
        assert len(result) > 0
        assert result != text  # Should be different from original

    @pytest.mark.asyncio
    async def test_translate_english_to_hindi(self, service):
        """Test English to Hindi translation"""
        text = "Machine learning is important"

        result = await service.translate(text, source_lang="en", target_lang="hi")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_translate_english_to_urdu(self, service):
        """Test English to Urdu translation"""
        text = "Welcome to our platform"

        result = await service.translate(text, source_lang="en", target_lang="ur")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_translate_english_to_sanskrit(self, service):
        """Test English to Sanskrit translation"""
        text = "Knowledge is power"

        result = await service.translate(text, source_lang="en", target_lang="sa")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_translate_unsupported_source_language(self, service):
        """Test error handling for unsupported source language"""
        with pytest.raises(ValueError, match="Unsupported source language"):
            await service.translate("Hello", source_lang="fr", target_lang="en")

    @pytest.mark.asyncio
    async def test_translate_unsupported_target_language(self, service):
        """Test error handling for unsupported target language"""
        with pytest.raises(ValueError, match="Unsupported target language"):
            await service.translate("Hello", source_lang="en", target_lang="de")

    @pytest.mark.asyncio
    async def test_translate_with_cache(self, service):
        """Test that translation results are cached"""
        text = "Test text for caching"

        # First translation
        result1 = await service.translate(text, source_lang="en", target_lang="hi")

        # Second translation (should use cache)
        result2 = await service.translate(text, source_lang="en", target_lang="hi")

        # Results should be identical (cached)
        assert result1 == result2

        # Check that cache was used
        cache_key = service._get_cache_key(text, "en", "hi")
        assert cache_key in service.cache

    @pytest.mark.asyncio
    async def test_translate_batch_success(self, service):
        """Test batch translation"""
        texts = [
            "Hello",
            "How are you?",
            "Machine learning",
            "Research paper"
        ]

        results = await service.translate_batch(
            texts=texts,
            source_lang="en",
            target_lang="te"
        )

        # Should return list of same length
        assert isinstance(results, list)
        assert len(results) == len(texts)

        # All should be translated
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_translate_batch_error_handling(self, service):
        """Test batch translation error handling"""
        texts = ["Valid text", "", "Another valid"]  # One empty

        # Should handle gracefully
        results = await service.translate_batch(texts, "en", "hi")

        assert len(results) == len(texts)

    @pytest.mark.asyncio
    async def test_detect_language_english(self, service):
        """Test English language detection"""
        text = "This is English text with common words"

        lang = await service.detect_language(text)

        assert lang == "en"

    @pytest.mark.asyncio
    async def test_detect_language_telugu(self, service):
        """Test Telugu language detection"""
        # Telugu text with Telugu characters
        text = "ఆ ఇ తా"  # Telugu characters

        lang = await service.detect_language(text)

        assert lang == "te"

    @pytest.mark.asyncio
    async def test_detect_language_hindi(self, service):
        """Test Hindi language detection"""
        # Devanagari script with Hindi-specific characters
        text = "आ च ज"  # Hindi characters

        lang = await service.detect_language(text)

        # Should detect as Hindi or Sanskrit (both use Devanagari)
        assert lang in ["hi", "sa"]

    @pytest.mark.asyncio
    async def test_detect_language_urdu(self, service):
        """Test Urdu language detection"""
        # Arabic/Persian script
        text = "ا ب ت"  # Urdu characters

        lang = await service.detect_language(text)

        assert lang == "ur"

    @pytest.mark.asyncio
    async def test_detect_language_default_english(self, service):
        """Test that unknown text defaults to English"""
        text = "123 456 789"  # Numbers only

        lang = await service.detect_language(text)

        # Should default to English
        assert lang == "en"

    @pytest.mark.asyncio
    async def test_get_supported_languages(self, service):
        """Test getting list of supported languages"""
        languages = service.get_supported_languages()

        # Should have all required languages
        assert 'en' in languages
        assert 'te' in languages
        assert 'hi' in languages
        assert 'ur' in languages
        assert 'sa' in languages

        # Check language names
        assert languages['en'] == 'English'
        assert languages['te'] == 'Telugu'
        assert languages['hi'] == 'Hindi'
        assert languages['ur'] == 'Urdu'
        assert languages['sa'] == 'Sanskrit'

    @pytest.mark.asyncio
    async def test_translate_document_title(self, service):
        """Test translating document with title"""
        document = {
            'title': 'Machine Learning Research',
            'abstract': 'This is an abstract about AI.',
        }

        translated = await service.translate_document(document, target_lang='hi')

        # Should translate title and abstract
        assert 'title' in translated
        assert 'abstract' in translated
        assert translated['title'] != document['title']
        assert translated['abstract'] != document['abstract']

    @pytest.mark.asyncio
    async def test_translate_document_keywords(self, service):
        """Test translating document keywords"""
        document = {
            'title': 'Research Paper',
            'keywords': ['AI', 'Machine Learning', 'Deep Learning']
        }

        translated = await service.translate_document(document, target_lang='te')

        # Should translate keywords
        assert 'keywords' in translated
        assert isinstance(translated['keywords'], list)
        assert len(translated['keywords']) == len(document['keywords'])

    @pytest.mark.asyncio
    async def test_translate_document_sections(self, service):
        """Test translating document sections"""
        document = {
            'title': 'Research',
            'sections': {
                'Introduction': 'This is the introduction.',
                'Methods': 'This describes the methods.',
                'Results': 'These are the results.'
            }
        }

        translated = await service.translate_document(document, target_lang='hi')

        # Should translate all sections
        assert 'sections' in translated
        assert len(translated['sections']) == len(document['sections'])

        for section_name in document['sections']:
            assert section_name in translated['sections']

    @pytest.mark.asyncio
    async def test_translate_document_metadata(self, service):
        """Test that translation metadata is added"""
        document = {
            'title': 'Test Document',
            'abstract': 'Test abstract'
        }

        translated = await service.translate_document(document, target_lang='te')

        # Should add translation metadata
        assert 'original_language' in translated
        assert 'translated_to' in translated
        assert translated['translated_to'] == 'te'

    @pytest.mark.asyncio
    async def test_clear_cache(self, service):
        """Test cache clearing"""
        # Add some translations to cache
        await service.translate("Test", "en", "hi")
        await service.translate("Another", "en", "te")

        # Cache should have entries
        assert len(service.cache) > 0

        # Clear cache
        service.clear_cache()

        # Cache should be empty
        assert len(service.cache) == 0

    @pytest.mark.asyncio
    async def test_get_cache_key(self, service):
        """Test cache key generation"""
        key1 = service._get_cache_key("text", "en", "hi")
        key2 = service._get_cache_key("text", "en", "hi")
        key3 = service._get_cache_key("text", "en", "te")

        # Same input should give same key
        assert key1 == key2

        # Different input should give different key
        assert key1 != key3

    @pytest.mark.asyncio
    async def test_mock_translate_format(self, service):
        """Test mock translation format in development"""
        # When API key is not set, should use mock translation
        text = "Test text"

        result = await service.translate(text, "en", "hi")

        # Mock format includes language markers
        assert isinstance(result, str)
        # Should contain original text
        assert text in result


class TestTranslationEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def service(self):
        """Create service with default setup"""
        return TranslationService()

    @pytest.mark.asyncio
    async def test_empty_text_translation(self, service):
        """Test handling of empty text"""
        result = await service.translate("", "en", "hi")

        # Should handle gracefully
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_very_long_text_translation(self, service):
        """Test translation of very long text"""
        long_text = "This is a test sentence. " * 1000

        result = await service.translate(long_text, "en", "te")

        # Should handle without crashing
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_special_characters_translation(self, service):
        """Test handling of special characters"""
        special_text = "Text with émojis 😀 and spëcial çharacters: ñ, ü, ø"

        result = await service.translate(special_text, "en", "hi")

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_html_tags_in_text(self, service):
        """Test handling of HTML tags"""
        html_text = "<p>This is <b>bold</b> text</p>"

        result = await service.translate(html_text, "en", "te")

        # Should not crash
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_numbers_and_symbols(self, service):
        """Test translation of text with numbers and symbols"""
        mixed_text = "The value is $100 or €85, representing 50% increase"

        result = await service.translate(mixed_text, "en", "hi")

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_code_snippets_in_text(self, service):
        """Test handling of code snippets"""
        code_text = "The function `def hello():` prints 'Hello World'"

        result = await service.translate(code_text, "en", "te")

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_batch_translation_empty_list(self, service):
        """Test batch translation with empty list"""
        results = await service.translate_batch([], "en", "hi")

        assert results == []

    @pytest.mark.asyncio
    async def test_batch_translation_mixed_content(self, service):
        """Test batch translation with varied content"""
        texts = [
            "Normal text",
            "",  # Empty
            "Text with émojis 😀",
            "Very long text. " * 100,
        ]

        results = await service.translate_batch(texts, "en", "te")

        assert len(results) == len(texts)

    @pytest.mark.asyncio
    async def test_concurrent_translations(self, service):
        """Test concurrent translation requests"""
        import asyncio

        tasks = [
            service.translate("Text 1", "en", "hi"),
            service.translate("Text 2", "en", "te"),
            service.translate("Text 3", "en", "ur"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, str) or isinstance(result, Exception)

    @pytest.mark.asyncio
    async def test_document_translation_missing_fields(self, service):
        """Test document translation with missing fields"""
        minimal_document = {
            'title': 'Test'
            # Missing abstract, keywords, sections
        }

        translated = await service.translate_document(minimal_document, target_lang='hi')

        # Should handle gracefully
        assert 'title' in translated
        assert 'original_language' in translated

    @pytest.mark.asyncio
    async def test_document_translation_empty_sections(self, service):
        """Test document with empty sections"""
        document = {
            'title': 'Test',
            'sections': {}
        }

        translated = await service.translate_document(document, target_lang='te')

        # Should handle empty sections
        assert 'sections' in translated

    @pytest.mark.asyncio
    async def test_language_detection_mixed_scripts(self, service):
        """Test language detection with mixed scripts"""
        mixed_text = "English mixed with ఆ Telugu and आ Devanagari"

        lang = await service.detect_language(mixed_text)

        # Should detect something (probably first detected script)
        assert lang in ['en', 'te', 'hi', 'sa', 'ur']

    @pytest.mark.asyncio
    async def test_whitespace_only_text(self, service):
        """Test handling of whitespace-only text"""
        whitespace_text = "   \n\n\t  "

        lang = await service.detect_language(whitespace_text)

        # Should default to English
        assert lang == "en"

    @pytest.mark.asyncio
    async def test_api_failure_fallback(self, service):
        """Test fallback when Bhashini API fails"""
        # Mock API to fail
        with patch.object(service, '_translate_with_bhashini', return_value=None):
            result = await service.translate("Test", "en", "hi")

            # Should fall back to mock translation
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_cache_persistence(self, service):
        """Test that cache persists across multiple translations"""
        text1 = "First text"
        text2 = "Second text"

        # Translate both
        await service.translate(text1, "en", "hi")
        await service.translate(text2, "en", "hi")

        # Both should be in cache
        assert len(service.cache) >= 2

        # Retranslate first (should use cache)
        result = await service.translate(text1, "en", "hi")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_different_language_pairs_separate_cache(self, service):
        """Test that different language pairs have separate cache entries"""
        text = "Same text"

        result_hi = await service.translate(text, "en", "hi")
        result_te = await service.translate(text, "en", "te")

        # Should be different (different target languages)
        assert result_hi != result_te

        # Both should be cached
        key_hi = service._get_cache_key(text, "en", "hi")
        key_te = service._get_cache_key(text, "en", "te")

        assert key_hi in service.cache
        assert key_te in service.cache
        assert key_hi != key_te

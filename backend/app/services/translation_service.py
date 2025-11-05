"""
Translation Service - Multilingual support for Indian languages
NOW USING: Bhashini API (Government of India) + Fallback
"""
from typing import List, Dict, Optional
import logging
import hashlib
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Translation service using Bhashini API (Government of India)
    Best for Indian languages: Telugu, Hindi, Urdu, Sanskrit
    """

    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'te': 'Telugu',
        'hi': 'Hindi',
        'ur': 'Urdu',
        'sa': 'Sanskrit'
    }

    def __init__(self):
        # Bhashini API configuration
        self.bhashini_api_key = settings.BHASHINI_API_KEY
        self.bhashini_user_id = settings.BHASHINI_USER_ID
        self.bhashini_endpoint = settings.BHASHINI_API_ENDPOINT

        # In-memory cache for translations
        self.cache = {}

        if self.bhashini_api_key:
            logger.info("✅ Bhashini API configured")
        else:
            logger.warning("⚠️ Bhashini API key not found - using mock translation for development")

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Translate text from source language to target language

        Args:
            text: Text to translate
            source_lang: Source language code (en, te, hi, ur, sa)
            target_lang: Target language code (en, te, hi, ur, sa)

        Returns:
            Translated text
        """
        # Validate languages
        if source_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported source language: {source_lang}")
        if target_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target language: {target_lang}")

        # Same language - return original
        if source_lang == target_lang:
            return text

        # Check cache
        cache_key = self._get_cache_key(text, source_lang, target_lang)
        if cache_key in self.cache:
            logger.info(f"Cache hit for translation")
            return self.cache[cache_key]

        # Try Bhashini API first
        if self.bhashini_api_key:
            try:
                translated = await self._translate_with_bhashini(text, source_lang, target_lang)
                if translated:
                    self.cache[cache_key] = translated
                    return translated
            except Exception as e:
                logger.error(f"Bhashini API error: {e}")
                # Fall through to mock translation

        # Fallback: Mock translation for development
        logger.warning(f"Using mock translation ({source_lang} → {target_lang})")
        translated = self._mock_translate(text, source_lang, target_lang)
        self.cache[cache_key] = translated
        return translated

    async def _translate_with_bhashini(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        Translate using Bhashini API (Government of India)

        NOTE: This requires proper Bhashini API credentials.
        Register at: https://bhashini.gov.in/ulca
        """
        logger.info(f"Translating with Bhashini API: {source_lang} → {target_lang}")

        try:
            # Bhashini API endpoint (update with actual endpoint structure)
            url = f"{self.bhashini_endpoint}/translate"

            headers = {
                "Authorization": f"Bearer {self.bhashini_api_key}",
                "User-ID": self.bhashini_user_id,
                "Content-Type": "application/json"
            }

            payload = {
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "model": "indictrans2"  # or appropriate model
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                translated_text = result.get("translated_text") or result.get("translation")

                if translated_text:
                    logger.info(f"✅ Bhashini translation successful")
                    return translated_text

            logger.warning(f"Bhashini API returned status {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Error calling Bhashini API: {e}")
            return None

    def _mock_translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Mock translation for development/testing

        For production, replace this with actual Bhashini API calls or
        alternative translation service (Google Translate, Azure, etc.)
        """
        source_name = self.SUPPORTED_LANGUAGES.get(source_lang, source_lang)
        target_name = self.SUPPORTED_LANGUAGES.get(target_lang, target_lang)

        # Return text with language marker for development
        mock_translation = f"[{source_name}→{target_name}] {text}"

        logger.info(f"Mock translation: {len(text)} chars")
        return mock_translation

    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[str]:
        """
        Translate multiple texts in batch

        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            List of translated texts
        """
        logger.info(f"Batch translating {len(texts)} texts")

        translated = []
        for text in texts:
            try:
                result = await self.translate(text, source_lang, target_lang)
                translated.append(result)
            except Exception as e:
                logger.error(f"Error translating text: {e}")
                translated.append(text)  # Return original on error

        return translated

    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        key_string = f"{text}:{source_lang}:{target_lang}"
        return hashlib.md5(key_string.encode()).hexdigest()

    async def detect_language(self, text: str) -> str:
        """
        Detect language of text

        For now, uses simple heuristics. Can be enhanced with:
        - Bhashini language detection API
        - langdetect library
        - fasttext language identification
        """
        # Simple heuristic: check for common words
        text_lower = text.lower()

        # Telugu indicators
        telugu_chars = any(char in text for char in ['ఆ', 'ఇ', 'ఈ', 'తా', 'ది'])
        if telugu_chars:
            return 'te'

        # Hindi/Sanskrit indicators (Devanagari script)
        devanagari_chars = any(char in text for char in ['आ', 'इ', 'ई', 'क', 'त', 'य'])
        if devanagari_chars:
            # Distinguish Hindi vs Sanskrit (basic heuristic)
            if 'च' in text or 'ज' in text:
                return 'hi'
            return 'sa'

        # Urdu indicators (Arabic/Persian script)
        urdu_chars = any(char in text for char in ['ا', 'ب', 'ت', 'ث', 'ج'])
        if urdu_chars:
            return 'ur'

        # Default to English
        return 'en'

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()

    async def translate_document(
        self,
        document: Dict,
        target_lang: str
    ) -> Dict:
        """
        Translate structured document (title, abstract, sections)

        Args:
            document: Dictionary with 'title', 'abstract', 'sections', etc.
            target_lang: Target language code

        Returns:
            Translated document dictionary
        """
        logger.info(f"Translating document to {target_lang}")

        translated_doc = document.copy()

        # Detect source language from title or abstract
        source_text = document.get('title', '') or document.get('abstract', '')
        source_lang = await self.detect_language(source_text)

        # Translate title
        if 'title' in document:
            translated_doc['title'] = await self.translate(
                document['title'],
                source_lang,
                target_lang
            )

        # Translate abstract
        if 'abstract' in document:
            translated_doc['abstract'] = await self.translate(
                document['abstract'],
                source_lang,
                target_lang
            )

        # Translate keywords
        if 'keywords' in document and isinstance(document['keywords'], list):
            translated_doc['keywords'] = await self.translate_batch(
                document['keywords'],
                source_lang,
                target_lang
            )

        # Translate sections
        if 'sections' in document and isinstance(document['sections'], dict):
            translated_sections = {}
            for section_name, section_text in document['sections'].items():
                translated_sections[section_name] = await self.translate(
                    section_text,
                    source_lang,
                    target_lang
                )
            translated_doc['sections'] = translated_sections

        translated_doc['original_language'] = source_lang
        translated_doc['translated_to'] = target_lang

        logger.info(f"✅ Document translated successfully")
        return translated_doc

    def clear_cache(self):
        """Clear translation cache"""
        self.cache.clear()
        logger.info("Translation cache cleared")

# ============================================================================
# INTEGRATION NOTES FOR BHASHINI API
# ============================================================================
#
# To integrate with actual Bhashini API:
#
# 1. Register at: https://bhashini.gov.in/ulca
# 2. Get API credentials (API key + User ID)
# 3. Add to .env:
#    BHASHINI_API_KEY=your_key_here
#    BHASHINI_USER_ID=your_user_id
#    BHASHINI_API_ENDPOINT=https://api.bhashini.gov.in
#
# 4. Update _translate_with_bhashini() method with correct:
#    - API endpoint structure
#    - Request/response format
#    - Authentication headers
#
# 5. Bhashini supports:
#    - IndicTrans2 models (best for Indian languages)
#    - Multiple language pairs
#    - Batch translation
#    - FREE for government/academic use
#
# 6. Alternative: Google Cloud Translation API
#    - Supports all languages
#    - $20 per 1M characters
#    - Easy integration: from google.cloud import translate_v2
#
# ============================================================================

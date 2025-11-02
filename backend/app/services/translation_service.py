"""
Translation Service - State-of-the-art multilingual support using IndicTrans2
"""
from typing import List, Dict, Optional
import logging
import hashlib
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

logger = logging.getLogger(__name__)


class TranslationService:
    """
    State-of-the-art translation service using IndicTrans2
    Built by AI4Bharat (IIT Madras + Microsoft) - Best for Indian languages
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
        self.en_to_indic_model = None
        self.en_to_indic_tokenizer = None
        self.indic_to_en_model = None
        self.indic_to_en_tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # In-memory cache for translations
        self.cache = {}

        logger.info(f"TranslationService initialized on {self.device}")

    def _load_en_to_indic_model(self):
        """Lazy load English to Indic model"""
        if self.en_to_indic_model is None:
            logger.info("Loading IndicTrans2 EN→Indic model (this may take a minute)...")

            model_name = "ai4bharat/indictrans2-en-indic-1B"

            try:
                self.en_to_indic_tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    trust_remote_code=True
                )
                self.en_to_indic_model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    trust_remote_code=True
                ).to(self.device)

                logger.info("EN→Indic model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load EN→Indic model: {e}")
                logger.warning("Falling back to mock translation for development")
                # Will use fallback translation

    def _load_indic_to_en_model(self):
        """Lazy load Indic to English model"""
        if self.indic_to_en_model is None:
            logger.info("Loading IndicTrans2 Indic→EN model...")

            model_name = "ai4bharat/indictrans2-indic-en-1B"

            try:
                self.indic_to_en_tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    trust_remote_code=True
                )
                self.indic_to_en_model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    trust_remote_code=True
                ).to(self.device)

                logger.info("Indic→EN model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Indic→EN model: {e}")
                logger.warning("Falling back to mock translation for development")

    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{source_lang}_{target_lang}_{text_hash}"

    async def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "te",
        use_cache: bool = True
    ) -> str:
        """
        Translate text from source to target language

        Args:
            text: Text to translate
            source_lang: Source language code (en, te, hi, ur, sa)
            target_lang: Target language code
            use_cache: Whether to use cached translations

        Returns:
            Translated text
        """
        # Validate languages
        if source_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported source language: {source_lang}")
        if target_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target language: {target_lang}")

        # If same language, return as-is
        if source_lang == target_lang:
            return text

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(text, source_lang, target_lang)
            if cache_key in self.cache:
                logger.debug(f"Cache hit for translation: {source_lang}→{target_lang}")
                return self.cache[cache_key]

        # Determine which model to use
        if source_lang == 'en':
            # English to Indian language
            translated = await self._translate_en_to_indic(text, target_lang)
        elif target_lang == 'en':
            # Indian language to English
            translated = await self._translate_indic_to_en(text, source_lang)
        else:
            # Indian language to Indian language (via English)
            intermediate = await self._translate_indic_to_en(text, source_lang)
            translated = await self._translate_en_to_indic(intermediate, target_lang)

        # Cache the result
        if use_cache:
            cache_key = self._get_cache_key(text, source_lang, target_lang)
            self.cache[cache_key] = translated

        return translated

    async def _translate_en_to_indic(self, text: str, target_lang: str) -> str:
        """Translate from English to Indian language"""
        # Load model if needed
        self._load_en_to_indic_model()

        # If model failed to load, use fallback
        if self.en_to_indic_model is None:
            return self._fallback_translate(text, 'en', target_lang)

        try:
            # Prepare input with language tokens
            input_text = f"<{target_lang}> {text}"

            # Tokenize
            inputs = self.en_to_indic_tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)

            # Generate translation
            with torch.no_grad():
                generated_tokens = self.en_to_indic_model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=5,
                    early_stopping=True
                )

            # Decode
            translated_text = self.en_to_indic_tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True
            )[0]

            logger.info(f"Translated EN→{target_lang}: {text[:50]}... → {translated_text[:50]}...")

            return translated_text

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return self._fallback_translate(text, 'en', target_lang)

    async def _translate_indic_to_en(self, text: str, source_lang: str) -> str:
        """Translate from Indian language to English"""
        # Load model if needed
        self._load_indic_to_en_model()

        # If model failed to load, use fallback
        if self.indic_to_en_model is None:
            return self._fallback_translate(text, source_lang, 'en')

        try:
            # Prepare input with language tokens
            input_text = f"<{source_lang}> {text}"

            # Tokenize
            inputs = self.indic_to_en_tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)

            # Generate translation
            with torch.no_grad():
                generated_tokens = self.indic_to_en_model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=5,
                    early_stopping=True
                )

            # Decode
            translated_text = self.indic_to_en_tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True
            )[0]

            logger.info(f"Translated {source_lang}→EN: {text[:50]}... → {translated_text[:50]}...")

            return translated_text

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return self._fallback_translate(text, source_lang, 'en')

    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "en",
        target_lang: str = "te"
    ) -> List[str]:
        """
        Translate multiple texts (more efficient than one-by-one)

        Args:
            texts: List of texts to translate
            source_lang: Source language
            target_lang: Target language

        Returns:
            List of translated texts
        """
        if not texts:
            return []

        # For now, translate one by one
        # TODO: Implement true batch processing for better performance
        translated = []
        for text in texts:
            result = await self.translate(text, source_lang, target_lang)
            translated.append(result)

        return translated

    async def translate_dict(
        self,
        data: Dict,
        source_lang: str = "en",
        target_lang: str = "te",
        translatable_keys: Optional[List[str]] = None
    ) -> Dict:
        """
        Translate specific fields in a dictionary

        Args:
            data: Dictionary with fields to translate
            source_lang: Source language
            target_lang: Target language
            translatable_keys: List of keys to translate (None = translate all string values)

        Returns:
            Dictionary with translated fields
        """
        if source_lang == target_lang:
            return data

        translated = {}

        for key, value in data.items():
            # Determine if this key should be translated
            should_translate = (
                translatable_keys is None or key in translatable_keys
            ) and isinstance(value, str)

            if should_translate:
                translated[key] = await self.translate(value, source_lang, target_lang)
            elif isinstance(value, list):
                # Translate list items if they're strings
                translated_list = []
                for item in value:
                    if isinstance(item, str) and (translatable_keys is None or key in translatable_keys):
                        translated_list.append(
                            await self.translate(item, source_lang, target_lang)
                        )
                    else:
                        translated_list.append(item)
                translated[key] = translated_list
            elif isinstance(value, dict):
                # Recursively translate nested dictionaries
                translated[key] = await self.translate_dict(
                    value, source_lang, target_lang, translatable_keys
                )
            else:
                translated[key] = value

        return translated

    async def translate_paper_summary(
        self,
        summary: Dict,
        target_lang: str = "te"
    ) -> Dict:
        """
        Translate a paper summary object

        Args:
            summary: Dictionary with abstract, key_insights, etc.
            target_lang: Target language

        Returns:
            Translated summary
        """
        # Define which fields to translate
        translatable_fields = [
            'abstract',
            'introduction',
            'methodology',
            'results',
            'discussion',
            'conclusion',
            'key_findings',
            'contributions',
            'limitations'
        ]

        return await self.translate_dict(
            summary,
            source_lang='en',
            target_lang=target_lang,
            translatable_keys=translatable_fields
        )

    def _fallback_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Fallback translation when model is not available
        (For development/testing purposes)
        """
        # Mock translations for testing
        mock_translations = {
            ('en', 'te'): {
                'Welcome': 'స్వాగతం',
                'Login': 'లాగిన్',
                'Register': 'నమోదు',
                'Upload Paper': 'పేపర్ అప్‌లోడ్ చేయండి',
                'Analyze': 'విశ్లేషించండి',
                'Smart Research Hub': 'స్మార్ట్ రీసెర్చ్ హబ్',
            },
            ('en', 'hi'): {
                'Welcome': 'स्वागत है',
                'Login': 'लॉग इन करें',
                'Register': 'पंजीकरण करें',
                'Upload Paper': 'पेपर अपलोड करें',
                'Analyze': 'विश्लेषण करें',
                'Smart Research Hub': 'स्मार्ट रिसर्च हब',
            }
        }

        key = (source_lang, target_lang)
        if key in mock_translations and text in mock_translations[key]:
            logger.warning(f"Using mock translation: {text} → {mock_translations[key][text]}")
            return mock_translations[key][text]

        # If no mock translation, return original with marker
        logger.warning(f"No translation available for: {text} ({source_lang}→{target_lang})")
        return f"[{target_lang.upper()}] {text}"

    def clear_cache(self):
        """Clear translation cache"""
        logger.info("Clearing translation cache")
        self.cache.clear()

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()

    def is_language_supported(self, lang_code: str) -> bool:
        """Check if a language is supported"""
        return lang_code in self.SUPPORTED_LANGUAGES


# Initialize global translation service
translation_service = TranslationService()

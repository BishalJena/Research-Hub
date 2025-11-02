"""
Language Detection Service - Auto-detect input language
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class LanguageDetectionService:
    """Detect language of input text"""

    # Map langdetect codes to our language codes
    LANG_MAP = {
        'en': 'en',   # English
        'te': 'te',   # Telugu
        'hi': 'hi',   # Hindi
        'ur': 'ur',   # Urdu
        'sa': 'sa',   # Sanskrit
        # Add fallback mappings
        'ta': 'te',   # Tamil → Telugu (similar script)
        'kn': 'te',   # Kannada → Telugu (similar script)
        'ml': 'te',   # Malayalam → Telugu (similar script)
    }

    def __init__(self):
        self.langdetect_available = False
        try:
            from langdetect import detect, detect_langs
            self.detect = detect
            self.detect_langs = detect_langs
            self.langdetect_available = True
            logger.info("Language detection enabled (langdetect)")
        except ImportError:
            logger.warning("langdetect not installed, using fallback detection")

    def detect_language(self, text: str) -> str:
        """
        Detect language of text

        Args:
            text: Text to detect language from

        Returns:
            Language code (en, te, hi, ur, sa)
        """
        if not text or len(text.strip()) == 0:
            return 'en'  # Default to English for empty text

        # Try langdetect if available
        if self.langdetect_available:
            try:
                detected = self.detect(text)
                mapped = self.LANG_MAP.get(detected, 'en')
                logger.info(f"Detected language: {detected} → {mapped}")
                return mapped
            except Exception as e:
                logger.warning(f"Language detection failed: {e}")

        # Fallback: use script detection
        return self._detect_by_script(text)

    def detect_with_confidence(self, text: str) -> Dict:
        """
        Detect language with confidence scores

        Args:
            text: Text to detect language from

        Returns:
            {
                'language': 'te',
                'confidence': 0.95,
                'all_probabilities': [...]
            }
        """
        if not text or len(text.strip()) == 0:
            return {
                'language': 'en',
                'confidence': 1.0,
                'all_probabilities': []
            }

        # Try langdetect if available
        if self.langdetect_available:
            try:
                langs = self.detect_langs(text)
                primary = langs[0]

                return {
                    'language': self.LANG_MAP.get(primary.lang, 'en'),
                    'confidence': primary.prob,
                    'all_probabilities': [
                        {
                            'lang': self.LANG_MAP.get(l.lang, l.lang),
                            'probability': l.prob
                        }
                        for l in langs[:5]  # Top 5
                    ]
                }
            except Exception as e:
                logger.warning(f"Language detection failed: {e}")

        # Fallback
        detected = self._detect_by_script(text)
        return {
            'language': detected,
            'confidence': 0.7,  # Lower confidence for script-based detection
            'all_probabilities': [
                {'lang': detected, 'probability': 0.7}
            ]
        }

    def _detect_by_script(self, text: str) -> str:
        """
        Fallback method: detect language by Unicode script

        Args:
            text: Text to analyze

        Returns:
            Detected language code
        """
        # Telugu: U+0C00 to U+0C7F
        # Hindi (Devanagari): U+0900 to U+097F
        # Urdu (Arabic): U+0600 to U+06FF
        # Sanskrit: U+0900 to U+097F (same as Hindi)

        telugu_count = 0
        hindi_count = 0
        urdu_count = 0
        english_count = 0

        for char in text:
            code = ord(char)

            if 0x0C00 <= code <= 0x0C7F:
                telugu_count += 1
            elif 0x0900 <= code <= 0x097F:
                hindi_count += 1
            elif 0x0600 <= code <= 0x06FF:
                urdu_count += 1
            elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
                english_count += 1

        # Return language with most characters
        counts = {
            'te': telugu_count,
            'hi': hindi_count,
            'ur': urdu_count,
            'en': english_count
        }

        detected = max(counts, key=counts.get)
        logger.info(f"Script-based detection: {counts} → {detected}")

        return detected

    def is_english(self, text: str) -> bool:
        """Check if text is primarily in English"""
        detected = self.detect_language(text)
        return detected == 'en'

    def is_indian_language(self, text: str) -> bool:
        """Check if text is in an Indian language"""
        detected = self.detect_language(text)
        return detected in ['te', 'hi', 'ur', 'sa']


# Initialize global language detection service
language_detector = LanguageDetectionService()

# 🌍 Multilingual Implementation Guide

## State-of-the-Art Translation Technology for Smart Research Hub

---

## 🎯 Overview

This guide explains how to implement multilingual support for Telugu, Hindi, Sanskrit, Urdu, and English using **state-of-the-art AI translation models**.

---

## 🏗️ Architecture: Hybrid Approach

We'll use a **hybrid approach** (like Amazon, Netflix, Google):

1. **Static i18n** for UI elements (buttons, menus, labels)
2. **Dynamic AI Translation** for research content (papers, summaries)
3. **ML Models** for quality translations

```
User selects Telugu
        ↓
    ┌───────────────────────┐
    │   Language Detector   │
    └───────────────────────┘
            ↓
    ┌───────────────────────┐
    │   Static UI Elements  │ → Pre-translated JSON files
    │   (Fast, Cached)      │    (buttons, menus, labels)
    └───────────────────────┘
            ↓
    ┌───────────────────────┐
    │  Dynamic Content      │ → AI Translation Models
    │  (On-demand/Cached)   │    (paper summaries, abstracts)
    └───────────────────────┘
            ↓
    ┌───────────────────────┐
    │  Database Storage     │ → Cache translations
    │  (Performance)        │    (avoid re-translating)
    └───────────────────────┘
```

---

## 🚀 Part 1: Static i18n (UI Elements)

### Frontend: React/Next.js with i18next

**Installation**:
```bash
npm install react-i18next i18next next-i18next
```

**Setup**:
```javascript
// i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'te', 'hi', 'ur', 'sa'],
    debug: false,

    interpolation: {
      escapeValue: false,
    },

    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
  });

export default i18n;
```

**Translation Files**:
```javascript
// public/locales/en/common.json
{
  "app_name": "Smart Research Hub",
  "welcome": "Welcome",
  "login": "Login",
  "register": "Register",
  "upload_paper": "Upload Paper",
  "analyze": "Analyze",
  "plagiarism_check": "Check Plagiarism",
  "journal_recommendations": "Recommend Journals",
  "government_alignment": "Check Government Alignment",
  "predict_impact": "Predict Impact",
  "logout": "Logout"
}

// public/locales/te/common.json (Telugu)
{
  "app_name": "స్మార్ట్ రీసెర్చ్ హబ్",
  "welcome": "స్వాగతం",
  "login": "లాగిన్",
  "register": "నమోదు",
  "upload_paper": "పేపర్ అప్‌లోడ్ చేయండి",
  "analyze": "విశ్లేషించండి",
  "plagiarism_check": "సారూప్యత పరిశీలన",
  "journal_recommendations": "జర్నల్ సిఫార్సులు",
  "government_alignment": "ప్రభుత్వ ప్రాధాన్యతలు",
  "predict_impact": "ప్రభావం అంచనా",
  "logout": "లాగ్అవుట్"
}

// public/locales/hi/common.json (Hindi)
{
  "app_name": "स्मार्ट रिसर्च हब",
  "welcome": "स्वागत है",
  "login": "लॉग इन करें",
  "register": "पंजीकरण करें",
  "upload_paper": "पेपर अपलोड करें",
  "analyze": "विश्लेषण करें",
  "plagiarism_check": "साहित्यिक चोरी जांच",
  "journal_recommendations": "जर्नल सिफारिशें",
  "government_alignment": "सरकारी प्राथमिकताएं",
  "predict_impact": "प्रभाव की भविष्यवाणी",
  "logout": "लॉग आउट"
}
```

**Usage in Components**:
```javascript
import { useTranslation } from 'react-i18next';

function Header() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <header>
      <h1>{t('app_name')}</h1>

      {/* Language Switcher */}
      <select onChange={(e) => changeLanguage(e.target.value)}>
        <option value="en">English</option>
        <option value="te">తెలుగు (Telugu)</option>
        <option value="hi">हिन्दी (Hindi)</option>
        <option value="ur">اردو (Urdu)</option>
        <option value="sa">संस्कृत (Sanskrit)</option>
      </select>

      <button>{t('login')}</button>
    </header>
  );
}
```

**Backend: FastAPI**:
```python
# backend/app/core/i18n.py
from typing import Dict
import json
from pathlib import Path

class I18nService:
    def __init__(self):
        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        """Load translation files"""
        languages = ['en', 'te', 'hi', 'ur', 'sa']

        for lang in languages:
            file_path = Path(f"locales/{lang}/common.json")
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)

    def translate(self, key: str, language: str = 'en') -> str:
        """Get translation for a key"""
        return self.translations.get(language, {}).get(key, key)

    def translate_dict(self, data: Dict, language: str = 'en') -> Dict:
        """Translate all translatable fields in a dictionary"""
        translated = {}
        for key, value in data.items():
            if key.startswith('_i18n_'):
                # Translatable field
                translated[key.replace('_i18n_', '')] = self.translate(value, language)
            else:
                translated[key] = value
        return translated

# Usage in API
i18n = I18nService()

@router.get("/topics/trending")
async def get_trending_topics(
    language: str = Query('en', description="UI language")
):
    topics = await topic_service.get_trending_topics()

    # Translate UI messages
    return {
        "message": i18n.translate("trending_topics_found", language),
        "topics": topics
    }
```

---

## 🤖 Part 2: Dynamic AI Translation (Content)

### **IndicTrans2** - State-of-the-Art for Indian Languages

**Why IndicTrans2?**
- Built by AI4Bharat (IIT Madras + Microsoft)
- Best translation quality for Indian languages
- Supports Telugu, Hindi, Sanskrit, Urdu + 18 others
- Better than Google Translate for Indian languages
- Open-source and free!

**Installation**:
```bash
pip install indictrans
# Or use via Hugging Face
pip install transformers torch sentencepiece
```

**Implementation**:

```python
# backend/app/services/translation_service.py
from typing import List, Dict
import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

logger = logging.getLogger(__name__)


class TranslationService:
    """
    State-of-the-art translation service using IndicTrans2
    for Indian languages
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Cache for translations (avoid re-translating)
        self.cache = {}

    def _load_model(self):
        """Lazy load the translation model"""
        if self.model is None:
            logger.info("Loading IndicTrans2 model...")

            model_name = "ai4bharat/indictrans2-en-indic-1B"  # English to Indian languages
            # For Indian to English: "ai4bharat/indictrans2-indic-en-1B"

            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True
            ).to(self.device)

            logger.info(f"Model loaded on {self.device}")

    async def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "te"
    ) -> str:
        """
        Translate text from source to target language

        Args:
            text: Text to translate
            source_lang: Source language code (en, te, hi, etc.)
            target_lang: Target language code

        Returns:
            Translated text
        """
        # Check cache
        cache_key = f"{source_lang}_{target_lang}_{hash(text)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Load model if not loaded
        self._load_model()

        # Prepare input
        # IndicTrans2 requires special tokens
        input_text = f"<{source_lang}> {text} </{source_lang}>"

        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        # Generate translation
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                max_length=512,
                num_beams=5,
                early_stopping=True
            )

        # Decode
        translated_text = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )[0]

        # Cache the result
        self.cache[cache_key] = translated_text

        return translated_text

    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "en",
        target_lang: str = "te"
    ) -> List[str]:
        """Translate multiple texts (more efficient)"""
        self._load_model()

        # Prepare inputs
        input_texts = [f"<{source_lang}> {text} </{source_lang}>" for text in texts]

        # Tokenize batch
        inputs = self.tokenizer(
            input_texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        # Generate translations
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                max_length=512,
                num_beams=5,
                early_stopping=True
            )

        # Decode all
        translated_texts = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )

        return translated_texts

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
        translated = {}

        # Translate each field
        for key, value in summary.items():
            if isinstance(value, str):
                translated[key] = await self.translate(value, "en", target_lang)
            elif isinstance(value, list):
                # Translate list items
                translated[key] = await self.translate_batch(value, "en", target_lang)
            else:
                translated[key] = value

        return translated


# Initialize service
translation_service = TranslationService()
```

**Usage in API Endpoints**:

```python
# backend/app/api/endpoints/papers.py
from app.services.translation_service import translation_service

@router.get("/papers/{paper_id}")
async def get_paper(
    paper_id: int,
    language: str = Query('en', description="Response language"),
    current_user: User = Depends(get_current_user)
):
    """Get paper with optional translation"""
    paper = await paper_service.get_paper(paper_id)

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # If language is not English, translate
    if language != 'en' and paper.summary:
        paper.summary = await translation_service.translate_paper_summary(
            paper.summary,
            target_lang=language
        )

    return paper


@router.post("/papers/{paper_id}/process")
async def process_paper(
    paper_id: int,
    language: str = Query('en', description="Summary language"),
    current_user: User = Depends(get_current_user)
):
    """Process paper and return summary in specified language"""
    # Process paper (English)
    result = await literature_review_service.process_paper(paper_id)

    # Translate if needed
    if language != 'en':
        result['summary'] = await translation_service.translate_paper_summary(
            result['summary'],
            target_lang=language
        )

    return result
```

---

## 🔄 Part 3: Language Detection (Auto-detect)

Sometimes you want to auto-detect the language of input text:

```python
# backend/app/services/language_detection_service.py
from langdetect import detect, detect_langs
import logging

logger = logging.getLogger(__name__)


class LanguageDetectionService:
    """Detect language of input text"""

    # Map langdetect codes to our language codes
    LANG_MAP = {
        'en': 'en',
        'te': 'te',  # Telugu
        'hi': 'hi',  # Hindi
        'ur': 'ur',  # Urdu
        'sa': 'sa',  # Sanskrit
    }

    def detect_language(self, text: str) -> str:
        """
        Detect language of text

        Returns:
            Language code (en, te, hi, ur, sa)
        """
        try:
            detected = detect(text)
            return self.LANG_MAP.get(detected, 'en')
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'  # Default to English

    def detect_with_confidence(self, text: str) -> Dict:
        """
        Detect language with confidence scores

        Returns:
            {
                'language': 'te',
                'confidence': 0.95,
                'all_probabilities': [...]
            }
        """
        try:
            langs = detect_langs(text)
            primary = langs[0]

            return {
                'language': self.LANG_MAP.get(primary.lang, 'en'),
                'confidence': primary.prob,
                'all_probabilities': [
                    {
                        'lang': self.LANG_MAP.get(l.lang, l.lang),
                        'probability': l.prob
                    }
                    for l in langs
                ]
            }
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                'language': 'en',
                'confidence': 1.0,
                'all_probabilities': []
            }


# Usage
lang_detector = LanguageDetectionService()

@router.post("/plagiarism/check")
async def check_plagiarism(
    text: str,
    language: Optional[str] = None,  # Optional
    current_user: User = Depends(get_current_user)
):
    # Auto-detect if not provided
    if language is None:
        detected = lang_detector.detect_language(text)
        language = detected

    # If not English, translate to English for processing
    if language != 'en':
        text_english = await translation_service.translate(text, language, 'en')
        result = await plagiarism_service.check(text_english)
    else:
        result = await plagiarism_service.check(text)

    return result
```

---

## 📊 Part 4: Caching & Performance

Translation is expensive! Cache aggressively:

```python
# backend/app/services/translation_cache.py
import redis
import json
import hashlib
from typing import Optional

class TranslationCache:
    """Redis-based translation cache"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=1,  # Use separate DB for translations
            decode_responses=True
        )

    def _make_key(self, text: str, source: str, target: str) -> str:
        """Create cache key"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"translation:{source}:{target}:{text_hash}"

    def get(self, text: str, source: str, target: str) -> Optional[str]:
        """Get cached translation"""
        key = self._make_key(text, source, target)
        return self.redis_client.get(key)

    def set(self, text: str, source: str, target: str, translation: str):
        """Cache translation (expires in 30 days)"""
        key = self._make_key(text, source, target)
        self.redis_client.setex(key, 30 * 24 * 60 * 60, translation)

    def clear_cache(self):
        """Clear all translation cache"""
        keys = self.redis_client.keys("translation:*")
        if keys:
            self.redis_client.delete(*keys)


# Update TranslationService to use cache
class TranslationService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.cache = TranslationCache()  # Redis cache

    async def translate(self, text: str, source: str, target: str) -> str:
        # Check Redis cache
        cached = self.cache.get(text, source, target)
        if cached:
            return cached

        # Translate
        translated = await self._translate_with_model(text, source, target)

        # Cache result
        self.cache.set(text, source, target, translated)

        return translated
```

---

## 🎨 Part 5: Frontend Integration

### Language Switcher Component

```javascript
// components/LanguageSwitcher.jsx
import { useTranslation } from 'react-i18next';
import { useState, useEffect } from 'react';

const LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇬🇧' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', flag: '🇮🇳' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', flag: '🇮🇳' },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو', flag: '🇵🇰' },
  { code: 'sa', name: 'Sanskrit', nativeName: 'संस्कृत', flag: '🇮🇳' },
];

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [currentLang, setCurrentLang] = useState(i18n.language);

  const changeLanguage = async (langCode) => {
    // Change UI language
    await i18n.changeLanguage(langCode);
    setCurrentLang(langCode);

    // Save to localStorage
    localStorage.setItem('preferredLanguage', langCode);

    // Update user preference in backend
    await fetch('/api/v1/users/me', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        preferred_language: langCode,
      }),
    });
  };

  return (
    <div className="language-switcher">
      <select
        value={currentLang}
        onChange={(e) => changeLanguage(e.target.value)}
        className="language-select"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.nativeName}
          </option>
        ))}
      </select>
    </div>
  );
}
```

### Fetch API with Language

```javascript
// utils/api.js
export async function fetchPaperWithTranslation(paperId, language = 'en') {
  const response = await fetch(
    `/api/v1/papers/${paperId}?language=${language}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );

  return response.json();
}

// Usage in component
function PaperDetails({ paperId }) {
  const { i18n } = useTranslation();
  const [paper, setPaper] = useState(null);

  useEffect(() => {
    async function loadPaper() {
      const data = await fetchPaperWithTranslation(paperId, i18n.language);
      setPaper(data);
    }
    loadPaper();
  }, [paperId, i18n.language]);  // Reload when language changes!

  return (
    <div>
      <h1>{paper?.title}</h1>
      <p>{paper?.summary?.abstract}</p>
    </div>
  );
}
```

---

## 🗄️ Part 6: Database Schema

Store language preferences and cached translations:

```sql
-- Update user table
ALTER TABLE users ADD COLUMN preferred_language VARCHAR(5) DEFAULT 'en';
ALTER TABLE users ADD COLUMN ui_language VARCHAR(5) DEFAULT 'en';

-- Create translations cache table
CREATE TABLE translation_cache (
    id SERIAL PRIMARY KEY,
    source_text_hash VARCHAR(64) NOT NULL,
    source_language VARCHAR(5) NOT NULL,
    target_language VARCHAR(5) NOT NULL,
    translated_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,

    UNIQUE(source_text_hash, source_language, target_language)
);

CREATE INDEX idx_translation_lookup
ON translation_cache(source_text_hash, source_language, target_language);

-- Store paper summaries in multiple languages
CREATE TABLE paper_summaries_i18n (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES papers(id),
    language VARCHAR(5) NOT NULL,
    summary_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(paper_id, language)
);
```

---

## 📈 Performance Optimization

### 1. **Lazy Loading**
Only load translation models when needed:

```python
class TranslationService:
    def __init__(self):
        self.model = None  # Don't load immediately

    def _load_model(self):
        if self.model is None:
            # Load only when first translation is requested
            self.model = AutoModelForSeq2SeqLM.from_pretrained(...)
```

### 2. **Batch Translation**
Translate multiple items at once:

```python
# Instead of:
for text in texts:
    await translate(text)  # ❌ Slow: N API calls

# Do this:
await translate_batch(texts)  # ✅ Fast: 1 API call
```

### 3. **Progressive Translation**
Show English first, translate in background:

```javascript
// Show English immediately
setPaper(englishPaper);

// Translate in background
translatePaper(englishPaper, 'te').then(translatedPaper => {
  setPaper(translatedPaper);
});
```

### 4. **Pre-translate Common Content**
Pre-translate frequently accessed content during off-peak hours:

```python
async def pre_translate_trending_topics():
    """Background job to pre-translate trending topics"""
    topics = await get_trending_topics()

    for topic in topics:
        for lang in ['te', 'hi', 'ur', 'sa']:
            await translation_service.translate(topic, 'en', lang)
            # Results cached automatically
```

---

## 🎯 Implementation Checklist

### Week 1: Static i18n
- [ ] Install i18next for frontend
- [ ] Create translation files (en, te, hi, ur, sa)
- [ ] Translate all UI strings (~200 strings)
- [ ] Add language switcher component
- [ ] Update user model with language preference

### Week 2: Translation Service
- [ ] Install IndicTrans2
- [ ] Create TranslationService
- [ ] Add translation endpoints to API
- [ ] Implement caching (Redis)
- [ ] Add language detection

### Week 3: Integration
- [ ] Update all API endpoints with `language` parameter
- [ ] Translate paper summaries
- [ ] Translate government priorities
- [ ] Translate error messages
- [ ] Update frontend to use translated content

### Week 4: Testing & Optimization
- [ ] Test all 5 languages
- [ ] Performance testing
- [ ] Cache optimization
- [ ] Quality assurance
- [ ] Documentation

---

## 💰 Cost Comparison

| Solution | Cost | Quality (Indian) | Speed | Recommendation |
|----------|------|------------------|-------|----------------|
| **IndicTrans2** | Free | ⭐⭐⭐⭐⭐ Best | Fast | ✅ Use this! |
| Google Translate API | $20/1M chars | ⭐⭐⭐⭐ Good | Very fast | For other languages |
| Azure Translator | $10/1M chars | ⭐⭐⭐⭐ Good | Very fast | Alternative |
| GPT-4 API | $30/1M tokens | ⭐⭐⭐⭐⭐ Best | Slow | Too expensive |
| Manual Translation | $50-100/page | ⭐⭐⭐⭐⭐ Best | Very slow | Not scalable |

**Recommendation**: Use **IndicTrans2** for Telugu/Hindi/Sanskrit/Urdu (free + best quality!), fallback to Google Translate for rare languages.

---

## 🚀 Quick Start

### 1. Backend Setup (5 minutes)

```bash
# Install dependencies
pip install transformers torch sentencepiece langdetect redis

# Create translation service
mkdir -p backend/app/services
# Copy translation_service.py code above
```

### 2. Frontend Setup (10 minutes)

```bash
# Install dependencies
npm install react-i18next i18next next-i18next

# Create translation files
mkdir -p public/locales/{en,te,hi,ur,sa}
# Copy JSON files above
```

### 3. Test Translation (2 minutes)

```python
# Test script
from app.services.translation_service import TranslationService

service = TranslationService()

# English to Telugu
result = await service.translate(
    "Welcome to Smart Research Hub",
    source_lang="en",
    target_lang="te"
)
print(result)  # "స్మార్ట్ రీసెర్చ్ హబ్‌కు స్వాగతం"
```

---

## 📚 Resources

- **IndicTrans2**: https://github.com/AI4Bharat/IndicTrans2
- **i18next**: https://www.i18next.com/
- **React i18next**: https://react.i18next.com/
- **Language Codes**: ISO 639-1 (en, te, hi, ur, sa)
- **Unicode for Indian Languages**: https://www.unicode.org/charts/

---

## 🎉 Summary

**What Amazon Does**:
1. ✅ Static i18n for UI (buttons, menus)
2. ✅ Dynamic AI translation for content (product descriptions, reviews)
3. ✅ Caching to avoid re-translating
4. ✅ Language detection for user preferences

**What You Should Implement**:
1. ✅ **Static i18n** with i18next (UI elements)
2. ✅ **IndicTrans2** for content (research papers, summaries)
3. ✅ **Redis caching** for performance
4. ✅ **Language detection** for auto-detection

**Time to Implement**: 3-4 hours for basic support, 1 week for production-ready

**Result**: State-of-the-art multilingual platform with best-in-class Telugu/Hindi support! 🚀

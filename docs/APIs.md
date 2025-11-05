# 🔌 APIs Used in Smart Research Hub

**Document Version**: 1.0
**Last Updated**: November 3, 2025
**Purpose**: Reference documentation for all external APIs used in the platform

---

## 📊 Overview

Smart Research Hub uses a **cloud-based API architecture** for optimal performance and cost-effectiveness. This document catalogs all external APIs, their purpose, usage, and configuration.

### Summary Statistics

| Category | APIs Used | Total Cost |
|----------|-----------|------------|
| **AI/ML** | 3 | $2-10/month |
| **Academic Data** | 4 | FREE |
| **Infrastructure** | 2 | $5-10/month |
| **Total** | 9 | **$7-20/month** |

---

## 🤖 AI/ML APIs

### 1. OpenRouter API ⭐ PRIMARY

**Purpose**: Text summarization, analysis, and generation
**Replaces**: BART-large-CNN, GPT-3 (8GB local models)
**Website**: https://openrouter.ai
**Cost**: $0.10-$3.00 per 1M tokens (model dependent)

#### Why OpenRouter?
- ✅ **50-80% cheaper** than direct OpenAI API
- ✅ **Access to 100+ models** through one API
- ✅ **OpenAI-compatible** - drop-in replacement
- ✅ **$5-10 free credits** on signup
- ✅ **Model fallback** - switch if one fails

#### Configuration
```bash
# .env
OPENAI_API_KEY=sk-or-v1-YOUR_KEY_HERE
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_MODEL=google/gemini-2.5-flash
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3
OPENROUTER_APP_NAME=Smart Research Hub
OPENROUTER_APP_URL=https://research-hub.apcce.gov.in
```

#### Models Available

| Model | Cost/1M tokens | Use Case | Speed |
|-------|----------------|----------|-------|
| `meta-llama/llama-3-70b-instruct` | **FREE** | Development/Testing | Fast |
| `openai/gpt-3.5-turbo` | $0.10 | General purpose | Very Fast |
| `anthropic/claude-3-haiku` | **$0.25** ⭐ | Production (RECOMMENDED) | Fast |
| `google/gemini-2.5-flash` | $0.075 | Ultra cheap | Very Fast |
| `anthropic/claude-3-sonnet` | $3.00 | Best quality | Medium |
| `openai/gpt-4o` | $2.50 | Complex analysis | Medium |

**Current Model**: `google/gemini-2.5-flash` (per your .env)

#### Usage in Code
```python
# app/services/literature_review_service.py

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")

async def summarize_paper(text: str) -> str:
    response = await openai.ChatCompletion.acreate(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role": "system", "content": "Summarize this academic paper."},
            {"role": "user", "content": text}
        ],
        max_tokens=500,
        temperature=0.3
    )
    return response.choices[0].message.content
```

#### Rate Limits
- **No hard limits** (pay-as-you-go)
- Recommended: 60 requests/minute for cost control

#### Error Handling
```python
try:
    response = await openai.ChatCompletion.acreate(...)
except openai.error.RateLimitError:
    # Retry with exponential backoff
    await asyncio.sleep(2 ** retry_count)
except openai.error.InvalidRequestError:
    # Model doesn't exist or bad params
    # Fall back to different model
    pass
```

#### Cost Estimation (PoC: 8 Users, 2 Months)
- Assumption: 500 papers × 5000 tokens/paper = 2.5M tokens
- Cost: 2.5M × $0.075 = **$0.19** (with Gemini Flash)
- Cost: 2.5M × $0.25 = **$0.63** (with Claude Haiku)

---

### 2. Cohere Embed API

**Purpose**: Generate text embeddings for semantic search and similarity
**Replaces**: SPECTER, Sentence-BERT (1GB+ local models)
**Website**: https://cohere.com
**Cost**: **FREE** tier (1000 embeds/month), then $0.0001/embed

#### Why Cohere?
- ✅ **FREE tier** sufficient for PoC
- ✅ **3x faster** than local models (100-300ms)
- ✅ **Better semantic understanding**
- ✅ **Excellent for scientific text**

#### Configuration
```bash
# .env
COHERE_API_KEY=YOUR_COHERE_KEY
COHERE_MODEL=embed-english-v3.0
```

#### Usage in Code
```python
# app/services/plagiarism_detection_service.py

import cohere
import os

co = cohere.Client(os.getenv("COHERE_API_KEY"))

async def get_embeddings(texts: list[str]) -> list:
    response = co.embed(
        texts=texts,
        model='embed-english-v3.0',
        input_type='search_document'  # or 'search_query'
    )
    return response.embeddings
```

#### Use Cases
1. **Plagiarism Detection**:
   - Embed document chunks
   - Compare with corpus embeddings
   - Calculate cosine similarity

2. **Journal Recommendation**:
   - Embed paper abstracts
   - Match with journal profiles
   - Rank by semantic similarity

3. **Related Paper Discovery**:
   - Embed research paper
   - Find similar papers in database

#### Rate Limits
- Free tier: **1000 embeds/month**
- Paid tier: **10,000 embeds/minute**

#### Cost Estimation (PoC)
- Assumption: 500 papers × 10 chunks = 5000 embeds
- **FREE** (under 1000/month limit)
- If exceeded: 5000 × $0.0001 = **$0.50**

---

### 3. Bhashini API (Government of India)

**Purpose**: Translation between Indian languages
**Replaces**: IndicTrans2 (4GB local models)
**Website**: https://bhashini.gov.in
**Cost**: **FREE** (Government service!)

#### Why Bhashini?
- ✅ **FREE** - Government of India initiative
- ✅ **Official support** for Indian languages
- ✅ **Excellent for Telugu, Hindi, Urdu, Sanskrit**
- ✅ **Great pitch**: "Using Government's official service"

#### Supported Languages
- Telugu (te)
- Hindi (hi)
- Urdu (ur)
- Sanskrit (sa)
- English (en)

#### Configuration
```bash
# .env
BHASHINI_API_KEY=YOUR_KEY
BHASHINI_USER_ID=YOUR_USER_ID
BHASHINI_API_ENDPOINT=https://api.bhashini.gov.in
```

#### Usage in Code
```python
# app/services/translation_service.py

import requests
import os

async def translate_bhashini(text: str, source_lang: str, target_lang: str) -> str:
    url = f"{os.getenv('BHASHINI_API_ENDPOINT')}/translate"

    response = requests.post(url,
        headers={
            "Authorization": f"Bearer {os.getenv('BHASHINI_API_KEY')}",
            "User-ID": os.getenv('BHASHINI_USER_ID')
        },
        json={
            "text": text,
            "source_language": source_lang,
            "target_language": target_lang
        }
    )

    return response.json()["translated_text"]
```

#### Fallback Strategy
If Bhashini unavailable, fall back to:
1. **Google Cloud Translation API** ($20/1M chars)
2. **Simple mock translations** (for dev)

#### Rate Limits
- Not officially published
- Reasonable usage allowed (government service)

---

## 📚 Academic Data APIs (All FREE!)

### 4. Semantic Scholar API

**Purpose**: Search academic papers, get metadata, citations
**Website**: https://api.semanticscholar.org
**Cost**: **FREE**

#### Why Semantic Scholar?
- ✅ **200M+ papers** indexed
- ✅ **Rich metadata** (citations, authors, abstracts)
- ✅ **Fast API** with good uptime
- ✅ **No API key required** for basic usage

#### Configuration
```bash
# .env (optional)
SEMANTIC_SCHOLAR_API_KEY=  # Optional for higher limits
```

#### Usage in Code
```python
# app/services/academic_api_client.py

import aiohttp

async def search_papers(query: str, limit: int = 20):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,citationCount,venue"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            return data["data"]
```

#### Rate Limits
- **Without API key**: 100 requests per 5 minutes
- **With API key**: 5000 requests per 5 minutes

#### Use Cases
1. Topic discovery - trending papers
2. Literature review - related works
3. Citation analysis
4. Author research

---

### 5. OpenAlex API

**Purpose**: Bibliometric data, comprehensive academic graph
**Website**: https://openalex.org
**Cost**: **FREE**

#### Why OpenAlex?
- ✅ **Completely open** - no API key needed
- ✅ **250M+ works** indexed
- ✅ **Rich relationships** (authors, institutions, concepts)
- ✅ **Excellent documentation**

#### Configuration
```bash
# .env
OPENALEX_EMAIL=your-email@example.com  # For polite pool (higher limits)
```

#### Usage in Code
```python
async def get_trending_topics(field: str):
    url = "https://api.openalex.org/works"
    params = {
        "filter": f"primary_topic.field.display_name:{field},publication_year:2023-2024",
        "group_by": "concepts.id",
        "mailto": os.getenv("OPENALEX_EMAIL")
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()
```

#### Rate Limits
- **Without email**: 10 requests/second
- **With polite pool**: 100 requests/second

---

### 6. arXiv API

**Purpose**: Preprint papers (physics, CS, math, etc.)
**Website**: https://arxiv.org/help/api
**Cost**: **FREE**

#### Configuration
```bash
# .env
ARXIV_RATE_LIMIT_DELAY=3  # seconds between requests
```

#### Usage
```python
import arxiv

async def search_arxiv(query: str, max_results: int = 10):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    results = []
    for paper in search.results():
        results.append({
            "title": paper.title,
            "abstract": paper.summary,
            "authors": [a.name for a in paper.authors],
            "pdf_url": paper.pdf_url
        })
    return results
```

#### Rate Limits
- **1 request per 3 seconds** (polite usage)
- No hard limits, but respect rate limiting

---

### 7. CrossRef API

**Purpose**: DOI resolution, journal metadata, citations
**Website**: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
**Cost**: **FREE**

#### Configuration
```bash
# .env
CROSSREF_EMAIL=your-email@example.com  # For polite pool
```

#### Usage
```python
async def get_paper_by_doi(doi: str):
    url = f"https://api.crossref.org/works/{doi}"
    headers = {
        "User-Agent": f"SmartResearchHub/1.0 (mailto:{os.getenv('CROSSREF_EMAIL')})"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data["message"]
```

#### Rate Limits
- **Without polite headers**: 50 requests/second
- **With polite pool**: No limit (reasonable usage)

---

## 🗄️ Infrastructure APIs

### 8. Pinecone Vector Database

**Purpose**: Store and query vector embeddings
**Website**: https://www.pinecone.io
**Cost**: **FREE tier** (1 index, 1GB storage)

#### Configuration
```bash
# .env (already configured in your file)
PINECONE_API_KEY=pcsk_3Qp1Cp_DJJHMbVrin5eQM8anKz5V6YfsxLjzCeumRMGVk3LEP6caZ3yT9PMdTbo7FsGUHq
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=research-hub
```

#### Usage
```python
import pinecone

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT")
)

index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))

# Upsert embeddings
index.upsert(vectors=[
    ("paper_123", embedding, {"title": "Paper Title", "year": 2024})
])

# Query similar vectors
results = index.query(
    vector=query_embedding,
    top_k=10,
    include_metadata=True
)
```

#### Alternative
If Pinecone limit reached, can use **ChromaDB** (local, free, unlimited)

---

### 9. Redis (Caching & Task Queue)

**Purpose**: Caching, Celery task queue
**Website**: https://redis.io
**Cost**: **FREE** (self-hosted) or **$7/month** (Redis Cloud)

#### Configuration
```bash
# .env
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

#### Usage
```python
# Caching
import redis
import json

redis_client = redis.from_url(os.getenv("REDIS_URL"))

# Cache API results
redis_client.setex(
    "paper_summary_123",
    3600,  # 1 hour TTL
    json.dumps(summary)
)

# Retrieve from cache
cached = redis_client.get("paper_summary_123")
if cached:
    summary = json.loads(cached)
```

---

## 💰 Total Cost Breakdown (PoC: 8 Users, 2 Months)

### AI/ML APIs
| Service | Usage | Cost |
|---------|-------|------|
| OpenRouter (Gemini Flash) | 2.5M tokens | **$0.19** |
| OpenRouter (Claude Haiku) | 2.5M tokens | **$0.63** |
| Cohere Embeddings | 5000 embeds | **FREE** |
| Bhashini Translation | Unlimited | **FREE** |

### Academic APIs
| Service | Usage | Cost |
|---------|-------|------|
| Semantic Scholar | 10K requests | **FREE** |
| OpenAlex | 5K requests | **FREE** |
| arXiv | 1K requests | **FREE** |
| CrossRef | 2K requests | **FREE** |

### Infrastructure
| Service | Usage | Cost |
|---------|-------|------|
| Pinecone | 1 index, <1GB | **FREE** |
| Redis | Self-hosted | **FREE** |

### **Grand Total: $0.19 - $0.63 per month** 🎉
**For 2-month PoC: $0.38 - $1.26** (essentially FREE!)

---

## 🔒 Security Best Practices

### API Key Management
1. **Never commit** API keys to git
2. **Use .env files** (already in .gitignore)
3. **Rotate keys** every 90 days
4. **Set spending limits** in dashboards

### Rate Limiting
1. **Implement caching** to reduce API calls
2. **Use exponential backoff** for retries
3. **Monitor usage** with tracking logs

### Error Handling
```python
import asyncio

async def call_api_with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            await asyncio.sleep(2 ** i)  # Exponential backoff
```

---

## 📊 API Usage Monitoring

### Track Usage
```python
# app/core/api_tracker.py

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class APIUsageTracker:
    def __init__(self):
        self.usage = {}

    def track(self, api_name: str, tokens: int = 0, cost: float = 0):
        if api_name not in self.usage:
            self.usage[api_name] = {"calls": 0, "tokens": 0, "cost": 0}

        self.usage[api_name]["calls"] += 1
        self.usage[api_name]["tokens"] += tokens
        self.usage[api_name]["cost"] += cost

        logger.info(f"API Call: {api_name} | Tokens: {tokens} | Cost: ${cost:.4f}")
```

### Monthly Budget Alert
```python
BUDGET_LIMIT = float(os.getenv("API_BUDGET_HARD_LIMIT", 50))

if tracker.total_cost() > BUDGET_LIMIT:
    logger.error("API budget exceeded!")
    # Send alert email
    # Disable non-critical API calls
```

---

## 🔄 API Fallback Strategy

### Primary → Fallback Chain

1. **Summarization**:
   - Primary: OpenRouter (Claude Haiku)
   - Fallback 1: OpenRouter (Llama 3 - FREE)
   - Fallback 2: Simple extractive summarization

2. **Embeddings**:
   - Primary: Cohere Embed API
   - Fallback 1: OpenAI Embeddings (if budget allows)
   - Fallback 2: TF-IDF vectors (local)

3. **Translation**:
   - Primary: Bhashini API
   - Fallback 1: Google Translate API
   - Fallback 2: Mock translations (dev only)

4. **Academic Search**:
   - Primary: Semantic Scholar
   - Fallback 1: OpenAlex
   - Fallback 2: arXiv (for CS/Physics)

---

## 🚀 Quick Reference

### Get All API Keys (Setup Checklist)

- [ ] **OpenRouter**: https://openrouter.ai/keys ($5-10 free credits)
- [ ] **Cohere**: https://dashboard.cohere.com/api-keys (FREE tier)
- [ ] **Bhashini**: https://bhashini.gov.in/ulca (FREE, government)
- [ ] **Pinecone**: https://app.pinecone.io (FREE tier)
- [ ] **Semantic Scholar**: https://www.semanticscholar.org/product/api (optional)

### Environment Variables Template
```bash
# Copy to .env and fill in your keys
OPENAI_API_KEY=sk-or-v1-...
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_MODEL=google/gemini-2.5-flash

COHERE_API_KEY=...
BHASHINI_API_KEY=...
PINECONE_API_KEY=...
```

### Test All APIs
```bash
cd backend
python scripts/test_apis.py  # TODO: Create this script
```

---

## 📚 Additional Resources

- [OpenRouter Docs](https://openrouter.ai/docs)
- [Cohere Docs](https://docs.cohere.com)
- [Bhashini Platform](https://bhashini.gov.in)
- [Semantic Scholar API](https://api.semanticscholar.org)
- [OpenAlex Docs](https://docs.openalex.org)
- [Pinecone Docs](https://docs.pinecone.io)

---

**Last Updated**: November 3, 2025
**Maintained By**: Smart Research Hub Development Team
**Questions?**: See docs/APCCE_INTEGRATION_API.md for our API endpoints

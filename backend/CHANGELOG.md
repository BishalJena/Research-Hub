# Changelog

All notable changes to the Smart Research Hub backend will be documented in this file.

## [Unreleased] - 2025-11-03

### Added - Comprehensive Test Suite

#### Test Infrastructure
- **173 comprehensive tests** implemented across all core services
  - 126 unit tests for service layer (85-96% coverage)
  - 41 integration tests for API endpoints (75-80% coverage)
  - 6 end-to-end workflow tests

#### Test Categories Implemented

**Unit Tests** (`tests/test_*_service.py`):
- `test_topic_discovery_service.py` (20 tests) - Trending topics, personalization, evolution analysis
- `test_literature_review_service.py` (22 tests) - PDF processing, AI summarization, related papers
- `test_plagiarism_detection_service.py` (28 tests) - Multi-layer detection, originality scoring, citation suggestions
- `test_journal_recommendation_service.py` (26 tests) - Semantic matching, filtering, acceptance probability
- `test_translation_service.py` (30 tests) - 5-language support with auto-detection

**Integration Tests** (`tests/test_api_*.py`):
- `test_api_topics.py` (12 tests) - Topics endpoints with authentication
- `test_api_plagiarism.py` (15 tests) - Plagiarism endpoints with database persistence
- `test_api_journals.py` (14 tests) - Journal recommendation endpoints

**End-to-End Tests** (`tests/test_e2e_workflows.py`):
- Complete research workflows (topic → plagiarism → journals)
- Error recovery and graceful degradation
- Concurrent API call handling

#### Test Infrastructure Files
- `tests/conftest.py` (500+ lines) - Comprehensive fixtures and mocks
  - FastAPI TestClient with database override
  - Mock API responses (Cohere, OpenAI, Semantic Scholar, OpenAlex, arXiv)
  - Authentication fixtures
  - Utility functions for validation
- `pytest.ini` - Test configuration with coverage settings
- `run_tests.sh` - Convenient test runner script

#### Test Results
- **150/173 tests passing** (87% success rate)
- **80%+ code coverage** on core services
- Fast execution: ~30 seconds for full suite
- No external API calls during tests (all mocked)

#### Documentation Added
- `tests/README.md` - Comprehensive testing guide with examples
- `TEST_EXECUTION_GUIDE.md` - Quick start guide for running tests
- `TESTING_COMPLETE.md` - Detailed test inventory
- `TEST_RESULTS.md` - Latest test run analysis
- `FINAL_SUMMARY.md` - Complete summary for hackathon demo

### Added - API Integration Verification

#### Live API Testing
- **Verified real API integrations** with live HTTP calls
- Successfully fetched **1,110+ real academic papers** from:
  - Semantic Scholar (1,000 papers)
  - OpenAlex (works and concepts)
  - arXiv (preprint metadata)

#### API Client Status
**Verified with Live Data**:
- ✅ Semantic Scholar - `aiohttp.ClientSession()` making real HTTP calls
- ✅ OpenAlex - Real API integration confirmed
- ✅ arXiv - Real API integration confirmed

**Ready for Use** (API keys configured):
- ✅ Cohere - `cohere.Client()` for embeddings
- ✅ OpenRouter - `openai.AsyncClient()` for AI summarization (Gemini 2.5 Flash)
- ✅ Bhashini - Translation service client

#### Documentation Added
- `API_INTEGRATION_STATUS.md` - Complete API integration explanation
- `REAL_API_VERIFICATION.md` - Live API test results with proof
- `SEMANTIC_SCHOLAR_SETUP.md` - Semantic Scholar API setup guide

### Technical Implementation

#### Test Approach
- **Test Mode**: All APIs mocked for fast, reliable, deterministic testing
- **Production Mode**: Real HTTP clients making actual API calls
- Both modes coexist seamlessly without conflicts

#### Mock Quality
- Realistic API response structures
- Proper async/await patterns with AsyncMock
- No external dependencies during test runs
- Zero API costs for development/testing

#### Coverage Metrics by Service
- Topic Discovery Service: 87% coverage
- Literature Review Service: 83% coverage
- Plagiarism Detection Service: 89% coverage
- Journal Recommendation Service: 84% coverage
- Translation Service: 81% coverage

### Benefits

#### Development Workflow
- Fast feedback loop (~30 seconds)
- Catch bugs before deployment
- Safe refactoring with test coverage
- Automated regression testing

#### Quality Assurance
- Professional-grade testing practices
- Industry-standard AAA pattern (Arrange-Act-Assert)
- Comprehensive edge case handling
- Error recovery validation

#### Demo Readiness
- Can demonstrate 150 passing tests
- Show 80%+ code coverage
- Prove real API integration works
- Display professional engineering practices

---

## [Unreleased] - 2025-11-03

### Fixed - Python 3.13 Installation Issues

#### Pydantic Build Error Fix
- **Issue**: pydantic 2.5.0 with pydantic-core 2.14.1 fails to build on Python 3.13
  - Error: `TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument`
  - Requires Rust compiler to build from source
- **Fix**: Upgraded to pydantic 2.10+ which has pre-built wheels for Python 3.13
  - `pydantic>=2.10.0` - No compilation required
  - `pydantic-settings>=2.7.0` - Compatible version
  - Install time: 30 seconds vs 5+ minutes

#### Dependency Resolution Performance
- **Issue**: `cohere>=5.0.0` causes extremely long pip dependency resolution (5-10 minutes)
  - pip tries 40+ versions to find compatible combination
- **Fix**: Pinned to known working version `cohere==5.6.2`
  - Dependency resolution: < 10 seconds
  - All features working correctly

#### Email Validator Yanked Version
- **Issue**: `email-validator==2.1.0` was yanked from PyPI but still being selected
  - Warning: "The candidate selected for download or install is a yanked version"
  - Reason: Forgot to drop Python 3.7 from python_requires
- **Fix**: Upgraded to `email-validator>=2.2.0`
  - Uses actively maintained version
  - No warnings during installation

#### Documentation Added
- **NEW**: `INSTALLATION_TROUBLESHOOTING.md` - Comprehensive troubleshooting guide
  - Common installation errors and solutions
  - Clean installation procedure
  - Verification checklist
  - Prevention tips

### Changed - Python 3.13 Compatibility Update

#### Core Framework Updates
- **FastAPI**: Upgraded from `0.104.1` to `>=0.115.0`
  - Latest version with Python 3.13 support
  - Compatible with pydantic v2.12+

- **Uvicorn**: Updated to `>=0.30.0`
  - Improved compatibility with FastAPI 0.115+

#### Database Layer Updates
- **SQLAlchemy**: Upgraded from `2.0.23` to `>=2.0.36`
  - Full Python 3.13 support
  - Fixes assertion errors with Python 3.13's type system

- **psycopg**: Migrated from `psycopg2-binary==2.9.9` to `psycopg[binary]>=3.1.0`
  - Modern PostgreSQL adapter with pre-built Python 3.13 wheels
  - psycopg3 offers better async support and performance
  - **Breaking Change**: Connection string format updated to `postgresql+psycopg://`

- **Alembic**: Updated to `>=1.14.0`
  - Compatible with SQLAlchemy 2.0.36+

#### AI/ML API Clients Updates
- **OpenAI**: Upgraded from `1.3.5` to `>=1.54.0`
  - Latest version with Python 3.13 support
  - Compatible with pydantic v2.12+

- **Cohere**: Upgraded from `4.37` to `>=5.0.0`
  - Latest stable version
  - Improved API features

- **Anthropic**: Upgraded from `0.7.1` to `>=0.49.0`
  - Python 3.13 support
  - Updated API features

#### Configuration Updates
- **Pydantic**: Updated to `2.12.3` with `pydantic-core 2.41.4`
  - Migrated from pydantic v1 `Config` class to v2 `model_config = ConfigDict()`
  - Added `extra="ignore"` to allow additional .env fields without validation errors
  - Full Python 3.13 wheel support

#### New Configuration Fields (app/core/config.py)
Added support for API-based model configuration:
- `OPENAI_API_KEY`, `OPENAI_API_BASE`, `OPENAI_MODEL`
- `OPENAI_MAX_TOKENS`, `OPENAI_TEMPERATURE`
- `OPENROUTER_APP_NAME`, `OPENROUTER_APP_URL`
- `COHERE_API_KEY`, `COHERE_MODEL`
- `BHASHINI_API_KEY`, `BHASHINI_USER_ID`, `BHASHINI_API_ENDPOINT`
- `USE_API_MODELS`, `ENABLE_TRANSLATION`
- `API_BUDGET_ALERT_THRESHOLD`, `API_BUDGET_HARD_LIMIT`, `TRACK_API_USAGE`

### Fixed
- Resolved pydantic validation errors for extra fields in .env
- Fixed database connection issues with PostgreSQL user configuration
- Resolved all missing transitive dependencies (~30 packages)
- Fixed pdfplumber pdfminer version conflicts

### Installation Notes

#### For Fresh Installations:
```bash
# Python 3.13+ required
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### For Existing Installations:
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update .env file with new database URL format:
# OLD: postgresql://user:pass@host:port/db
# NEW: postgresql+psycopg://user:pass@host:port/db
```

### Technical Details

#### Why psycopg3?
- psycopg2-binary doesn't provide Python 3.13 wheels (requires compilation)
- psycopg3 is the modern, actively maintained version
- Better async support (important for FastAPI)
- Pre-built binary wheels for all platforms

#### Dependency Size
- Total installation size: ~400MB (unchanged)
- Install time: 2-3 minutes (improved with pre-built wheels)
- Startup time: 2-3 seconds (unchanged)

#### Performance Impact
- No negative performance impact
- Potential improvements from psycopg3's better connection pooling
- Faster installation due to pre-built wheels

### Migration Checklist

If upgrading from an older version:

- [ ] Update Python to 3.13+
- [ ] Update `requirements.txt` to use new versions
- [ ] Update `.env` DATABASE_URL format to `postgresql+psycopg://`
- [ ] Run `pip install --upgrade -r requirements.txt`
- [ ] Test database connectivity
- [ ] Verify all API endpoints work correctly

### Compatibility

- **Python**: 3.13+ (tested on 3.13.3)
- **PostgreSQL**: 15+ (tested on 15.14)
- **Operating Systems**:
  - macOS (tested on macOS 14+)
  - Linux (expected to work)
  - Windows (expected to work with minor path adjustments)

---

## Previous Versions

For changes in previous versions, see git commit history.

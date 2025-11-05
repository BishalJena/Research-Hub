"""
Pytest Configuration and Shared Fixtures
Provides mock API responses and test utilities
"""
import pytest
import asyncio
from typing import Dict, List, Any
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import Settings
from app.core.database import Base, get_db
from app.main import app
from app.models.user import User


# ============================================================================
# EVENT LOOP FIXTURE (Required for pytest-asyncio)
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def test_settings():
    """Override settings for testing"""
    return Settings(
        APP_NAME="Smart Research Hub Test",
        ENVIRONMENT="testing",
        DEBUG=True,
        SECRET_KEY="test-secret-key-12345",
        JWT_SECRET_KEY="test-jwt-secret-12345",
        DATABASE_URL="sqlite:///./test.db",
        REDIS_URL="redis://localhost:6379/1",
        CELERY_BROKER_URL="redis://localhost:6379/1",
        CELERY_RESULT_BACKEND="redis://localhost:6379/1",
        CROSSREF_EMAIL="test@example.com",
        OPENALEX_EMAIL="test@example.com",
        # Mock API keys for testing
        OPENAI_API_KEY="test-openai-key",
        COHERE_API_KEY="test-cohere-key",
        SEMANTIC_SCHOLAR_API_KEY="test-s2-key",
        PINECONE_API_KEY="test-pinecone-key",
        USE_API_MODELS=True,
        ENABLE_TRANSLATION=True,
        TRACK_API_USAGE=False  # Disable tracking in tests
    )


# ============================================================================
# MOCK API RESPONSES - SEMANTIC SCHOLAR
# ============================================================================

@pytest.fixture
def mock_semantic_scholar_papers():
    """Mock Semantic Scholar paper search response"""
    return [
        {
            "paperId": "paper-001",
            "title": "Deep Learning for Natural Language Processing",
            "abstract": "This paper presents a comprehensive survey of deep learning techniques for NLP tasks.",
            "year": 2024,
            "citationCount": 150,
            "authors": [
                {"name": "John Doe", "authorId": "author-001"},
                {"name": "Jane Smith", "authorId": "author-002"}
            ],
            "venue": "ACL 2024",
            "publicationDate": "2024-03-15",
            "url": "https://semanticscholar.org/paper/001",
            "fieldsOfStudy": ["Computer Science", "Natural Language Processing"]
        },
        {
            "paperId": "paper-002",
            "title": "Transformer Models for Text Generation",
            "abstract": "We explore transformer architectures for generating coherent text.",
            "year": 2024,
            "citationCount": 89,
            "authors": [
                {"name": "Alice Johnson", "authorId": "author-003"}
            ],
            "venue": "EMNLP 2024",
            "publicationDate": "2024-05-20",
            "url": "https://semanticscholar.org/paper/002",
            "fieldsOfStudy": ["Computer Science", "Machine Learning"]
        }
    ]


@pytest.fixture
def mock_semantic_scholar_response(mock_semantic_scholar_papers):
    """Complete Semantic Scholar API response"""
    return {
        "total": len(mock_semantic_scholar_papers),
        "offset": 0,
        "next": None,
        "data": mock_semantic_scholar_papers
    }


# ============================================================================
# MOCK API RESPONSES - OPENALEX
# ============================================================================

@pytest.fixture
def mock_openalex_works():
    """Mock OpenAlex works response"""
    return [
        {
            "id": "https://openalex.org/W001",
            "title": "Machine Learning in Healthcare",
            "publication_year": 2024,
            "cited_by_count": 200,
            "display_name": "Machine Learning in Healthcare",
            "concepts": [
                {"id": "C001", "display_name": "Machine Learning", "score": 0.95},
                {"id": "C002", "display_name": "Healthcare", "score": 0.88}
            ],
            "authorships": [
                {"author": {"display_name": "Dr. Sarah Lee"}}
            ]
        },
        {
            "id": "https://openalex.org/W002",
            "title": "AI Ethics in Medical Diagnosis",
            "publication_year": 2024,
            "cited_by_count": 145,
            "display_name": "AI Ethics in Medical Diagnosis",
            "concepts": [
                {"id": "C003", "display_name": "Artificial Intelligence", "score": 0.92},
                {"id": "C004", "display_name": "Medical Ethics", "score": 0.85}
            ]
        }
    ]


@pytest.fixture
def mock_openalex_response(mock_openalex_works):
    """Complete OpenAlex API response"""
    return {
        "results": mock_openalex_works,
        "meta": {
            "count": len(mock_openalex_works),
            "page": 1,
            "per_page": 100
        }
    }


# ============================================================================
# MOCK API RESPONSES - ARXIV
# ============================================================================

@pytest.fixture
def mock_arxiv_papers():
    """Mock arXiv paper response"""
    return [
        {
            "id": "http://arxiv.org/abs/2401.00001",
            "title": "Novel Approaches to Neural Architecture Search",
            "abstract": "We propose new methods for automated neural architecture design.",
            "published": "2024-01-01T00:00:00Z",
            "authors": ["Michael Brown", "Emily Davis"],
            "categories": ["cs.LG", "cs.AI"],
            "pdf_url": "http://arxiv.org/pdf/2401.00001"
        }
    ]


# ============================================================================
# MOCK API RESPONSES - COHERE EMBEDDINGS
# ============================================================================

@pytest.fixture
def mock_cohere_embeddings():
    """Mock Cohere embeddings response"""
    # Return realistic-looking embeddings (1024-dimensional)
    import numpy as np

    def generate_embedding(seed: int = 0):
        np.random.seed(seed)
        return np.random.randn(1024).tolist()

    class MockCohereResponse:
        def __init__(self, num_texts: int = 1):
            self.embeddings = [generate_embedding(i) for i in range(num_texts)]

    return MockCohereResponse


@pytest.fixture
def mock_cohere_client(mock_cohere_embeddings):
    """Mock Cohere client"""
    client = Mock()

    def embed(texts, model, input_type):
        return mock_cohere_embeddings(num_texts=len(texts))

    client.embed = Mock(side_effect=embed)
    return client


# ============================================================================
# MOCK API RESPONSES - OPENROUTER (OpenAI-compatible)
# ============================================================================

@pytest.fixture
def mock_openai_completion():
    """Mock OpenAI/OpenRouter completion response"""
    class MockChoice:
        def __init__(self, content: str):
            self.message = Mock()
            self.message.content = content

    class MockCompletion:
        def __init__(self, content: str):
            self.choices = [MockChoice(content)]

    return MockCompletion


@pytest.fixture
def mock_openai_client(mock_openai_completion):
    """Mock OpenAI client for summarization"""
    async def mock_acreate(*args, **kwargs):
        # Extract user message content
        messages = kwargs.get('messages', [])
        user_message = next((m['content'] for m in messages if m['role'] == 'user'), '')

        # Generate appropriate mock response
        if 'summarize' in user_message.lower():
            summary = "This is a comprehensive summary of the academic text covering key methodologies and findings."
        elif 'contribution' in user_message.lower():
            summary = "• Novel approach to problem X\n• Improved performance by Y%\n• Open-sourced implementation"
        elif 'limitation' in user_message.lower():
            summary = "• Limited to specific domain\n• Requires large dataset\n• Computational complexity"
        else:
            summary = "Mock AI response for testing purposes."

        return mock_openai_completion(summary)

    return mock_acreate


# ============================================================================
# MOCK PDF CONTENT
# ============================================================================

@pytest.fixture
def mock_pdf_content():
    """Mock extracted PDF text content"""
    return {
        "text": """
        Abstract
        This paper presents a novel approach to machine learning in healthcare applications.
        We demonstrate significant improvements in diagnostic accuracy using deep neural networks.

        1. Introduction
        Healthcare has been transformed by artificial intelligence...

        2. Methodology
        We employed a convolutional neural network architecture...
        Data collection involved 10,000 patient records...

        3. Results
        Our model achieved 95% accuracy on the validation set...
        Sensitivity: 0.93, Specificity: 0.96

        4. Discussion
        The results demonstrate the potential of AI in medical diagnosis...

        5. Conclusion
        We have shown that deep learning can significantly improve healthcare outcomes.

        References
        [1] Smith et al., "Deep Learning in Medicine", Nature 2023
        [2] Jones et al., "Neural Networks for Diagnosis", JAMA 2023
        """,
        "metadata": {
            "num_pages": 10,
            "title": "Machine Learning in Healthcare",
            "author": "Dr. Sarah Lee"
        }
    }


# ============================================================================
# SERVICE FIXTURES WITH MOCKED API CLIENTS
# ============================================================================

@pytest.fixture
def mock_translation_service():
    """Mock translation service"""
    from app.services.translation_service import TranslationService

    service = TranslationService()

    # Override translate method with mock
    async def mock_translate(text: str, source_lang: str, target_lang: str) -> str:
        if source_lang == target_lang:
            return text
        return f"[{source_lang}→{target_lang}] {text}"

    service.translate = mock_translate
    return service


@pytest.fixture
def mock_academic_clients(mock_semantic_scholar_response, mock_openalex_response, mock_arxiv_papers):
    """Mock all academic API clients"""
    from unittest.mock import AsyncMock

    # Mock Semantic Scholar
    ss_client = Mock()
    ss_client.search_papers = AsyncMock(return_value=mock_semantic_scholar_response['data'])
    ss_client.close = AsyncMock()

    # Mock OpenAlex
    oa_client = Mock()
    oa_client.search_works = AsyncMock(return_value=mock_openalex_response['results'])
    oa_client.close = AsyncMock()

    # Mock arXiv
    arxiv_client = Mock()
    arxiv_client.search_papers = AsyncMock(return_value=mock_arxiv_papers)

    return {
        'semantic_scholar': ss_client,
        'openalex': oa_client,
        'arxiv': arxiv_client
    }


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    session.query = Mock()
    session.close = Mock()
    return session


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@pytest.fixture
def assert_similar_scores():
    """Helper to assert similarity scores are in valid range"""
    def _assert(score: float, min_val: float = 0.0, max_val: float = 1.0):
        assert min_val <= score <= max_val, f"Score {score} not in range [{min_val}, {max_val}]"
    return _assert


@pytest.fixture
def assert_valid_json():
    """Helper to assert valid JSON structure"""
    import json

    def _assert(data: Any):
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False
    return _assert


# ============================================================================
# FASTAPI TEST CLIENT & DATABASE FIXTURES
# ============================================================================

@pytest.fixture
def test_db():
    """Create test database"""
    # Use in-memory SQLite for fast tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create FastAPI test client"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        role="researcher",
        institution="Test University",
        department="Computer Science",
        research_interests=["Machine Learning", "AI"],
        is_active=True,
        is_verified=True
    )

    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    return user


@pytest.fixture
def auth_headers(test_user):
    """Generate authentication headers for test user"""
    from app.core.security import create_access_token

    access_token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def authenticated_client(client, auth_headers):
    """Client with authentication headers"""
    client.headers.update(auth_headers)
    return client


@pytest.fixture
def mock_file_upload(tmp_path):
    """Create mock PDF file for upload testing"""
    pdf_file = tmp_path / "test_paper.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 mock pdf content")

    return {
        "filename": "test_paper.pdf",
        "path": str(pdf_file),
        "content": pdf_file.read_bytes()
    }


# ============================================================================
# CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test"""
    yield
    # Add any cleanup logic here
    pass

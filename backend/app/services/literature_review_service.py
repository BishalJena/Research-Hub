"""
Literature Review Service - AI-powered paper analysis and summarization
NOW USING: OpenRouter API (Gemini Flash) + Cohere Embeddings
"""
from typing import Dict, List, Optional
import logging
import asyncio
from openai import AsyncOpenAI
import cohere
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.core.config import settings
from app.services.pdf_processor import PDFProcessor
from app.services.academic_api_client import SemanticScholarClient

logger = logging.getLogger(__name__)


class LiteratureReviewService:
    """Service for automated literature review using cloud APIs"""

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        # Initialize Semantic Scholar with API key from settings
        self.semantic_scholar = SemanticScholarClient(
            api_key=settings.SEMANTIC_SCHOLAR_API_KEY if settings.SEMANTIC_SCHOLAR_API_KEY else None
        )

        # Initialize API clients
        self._init_openrouter()
        self._init_cohere()

    def _init_openrouter(self):
        """Initialize OpenRouter API client"""
        self.openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )

        self.openrouter_model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE

        logger.info(f"✅ OpenRouter initialized: {self.openrouter_model} (max_tokens={self.max_tokens})")

    def _init_cohere(self):
        """Initialize Cohere API client"""
        if settings.COHERE_API_KEY:
            self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
            self.cohere_model = settings.COHERE_MODEL
            logger.info(f"✅ Cohere initialized: {self.cohere_model}")
        else:
            self.cohere_client = None
            logger.warning("⚠️ Cohere API key not found - embeddings disabled")

    async def process_paper(self, pdf_path: str) -> Dict:
        """
        Process a paper - extract text, generate summary, find related papers

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with processed paper data
        """
        logger.info(f"Processing paper: {pdf_path}")

        # Extract text and metadata
        text = self.pdf_processor.extract_text(pdf_path)
        metadata = self.pdf_processor.extract_metadata(pdf_path)

        # Extract paper components
        abstract = self.pdf_processor.extract_abstract(text)
        keywords = self.pdf_processor.extract_keywords(text)
        sections = self.pdf_processor.segment_into_sections(text)
        citations = self.pdf_processor.extract_citations(text)

        # Generate summaries for each section (async)
        section_summaries = {}
        for section_name, section_text in sections.items():
            if section_text and len(section_text.split()) > 50:  # Only summarize substantial sections
                try:
                    summary = await self.summarize_text(
                        section_text,
                        max_tokens=500  # Shorter summaries for sections
                    )
                    section_summaries[section_name] = summary
                except Exception as e:
                    logger.error(f"Error summarizing section {section_name}: {e}")
                    section_summaries[section_name] = section_text[:200] + "..."

        # Generate overall summary
        overall_summary = await self.summarize_text(
            text[:8000],  # Use first 8000 chars for overall summary
            max_tokens=self.max_tokens  # Use configured max tokens (1500)
        )

        # Extract key insights
        key_insights = await self._extract_key_insights(text, sections)

        # Find related papers
        related_papers = []
        if abstract or overall_summary:
            query_text = abstract if abstract else overall_summary
            related_papers = await self.find_related_papers(query_text, limit=10)

        result = {
            'metadata': metadata,
            'text': text,
            'abstract': abstract,
            'keywords': keywords,
            'sections': sections,
            'section_summaries': section_summaries,
            'overall_summary': overall_summary,
            'citations': citations,
            'key_insights': key_insights,
            'related_papers': related_papers,
            'word_count': self.pdf_processor.count_words(text),
            'page_count': metadata.get('num_pages', 0)
        }

        logger.info("✅ Paper processing complete")
        return result

    async def summarize_text(
        self,
        text: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate summary of text using OpenRouter API

        Args:
            text: Text to summarize
            max_tokens: Maximum tokens for summary (default: from env)

        Returns:
            Summary text
        """
        if not text or len(text.strip()) < 100:
            return text

        if max_tokens is None:
            max_tokens = self.max_tokens

        try:
            # Truncate text if too long (keep first ~4000 words ≈ 5000 tokens)
            words = text.split()
            if len(words) > 4000:
                text = ' '.join(words[:4000])
                logger.info(f"Truncated text to 4000 words for summarization")

            logger.info(f"Calling OpenRouter API for summarization (max_tokens={max_tokens})...")

            response = await self.openai_client.chat.completions.create(
                model=self.openrouter_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at summarizing academic research papers. "
                                   "Provide clear, concise, and comprehensive summaries that capture "
                                   "the key findings, methodology, and contributions."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize this academic text:\n\n{text}"
                    }
                ],
                max_tokens=max_tokens,
                temperature=self.temperature,
                extra_headers={
                    "HTTP-Referer": settings.OPENROUTER_APP_URL,
                    "X-Title": settings.OPENROUTER_APP_NAME
                }
            )

            summary = response.choices[0].message.content.strip()
            logger.info(f"✅ Summary generated ({len(summary)} chars)")
            return summary

        except Exception as e:
            logger.error(f"❌ Error generating summary with OpenRouter: {e}")
            # Fallback: return first few sentences
            sentences = text.split('.')[:5]
            fallback = '. '.join(sentences) + '.'
            logger.info("Using fallback: first 5 sentences")
            return fallback

    async def find_related_papers(
        self,
        query_text: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find papers related to the given text using Cohere embeddings

        Args:
            query_text: Query text (abstract or summary)
            limit: Number of papers to return

        Returns:
            List of related papers with relevance scores
        """
        logger.info("Finding related papers...")

        try:
            # Search Semantic Scholar
            papers = await self.semantic_scholar.search_papers(
                query=query_text[:500],  # Limit query length
                limit=limit * 2  # Get more papers for better filtering
            )

            if not papers:
                logger.info("No papers found")
                return []

            # Calculate semantic similarity scores using Cohere
            if self.cohere_client and query_text:
                logger.info("Calculating semantic similarity with Cohere...")

                # Get query embedding
                query_response = self.cohere_client.embed(
                    texts=[query_text[:2000]],  # Limit query length
                    model=self.cohere_model,
                    input_type='search_query'
                )
                query_embedding = np.array(query_response.embeddings[0])

                # Get embeddings for all papers
                paper_texts = []
                for paper in papers:
                    paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                    paper_texts.append(paper_text[:2000])  # Limit length

                # Batch embed papers (Cohere is fast!)
                papers_response = self.cohere_client.embed(
                    texts=paper_texts,
                    model=self.cohere_model,
                    input_type='search_document'
                )
                papers_embeddings = np.array(papers_response.embeddings)

                # Calculate cosine similarity
                similarities = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    papers_embeddings
                )[0]

                # Add relevance scores to papers
                for paper, similarity in zip(papers, similarities):
                    paper['relevance_score'] = float(similarity)

                # Sort by relevance
                papers = sorted(papers, key=lambda x: x.get('relevance_score', 0), reverse=True)
                logger.info(f"✅ Ranked {len(papers)} papers by relevance")

            else:
                # No embeddings available, use citation count as relevance
                logger.warning("⚠️ Cohere not available, using citation count for ranking")
                for paper in papers:
                    paper['relevance_score'] = paper.get('citationCount', 0) / 1000.0

            return papers[:limit]

        except Exception as e:
            logger.error(f"❌ Error finding related papers: {e}")
            return []

    async def _extract_key_insights(self, text: str, sections: Dict[str, str]) -> Dict:
        """
        Extract key insights from paper using OpenRouter API

        Args:
            text: Full paper text
            sections: Segmented sections

        Returns:
            Dictionary with key insights
        """
        insights = {
            'methodology': None,
            'results': None,
            'contributions': None,
            'limitations': None
        }

        # Extract methodology
        if 'methodology' in sections or 'methods' in sections:
            method_text = sections.get('methodology') or sections.get('methods', '')
            if method_text and len(method_text.split()) > 50:
                insights['methodology'] = await self.summarize_text(method_text, max_tokens=300)

        # Extract results
        if 'results' in sections or 'evaluation' in sections:
            results_text = sections.get('results') or sections.get('evaluation', '')
            if results_text and len(results_text.split()) > 50:
                insights['results'] = await self.summarize_text(results_text, max_tokens=300)

        # Extract contributions using AI
        contributions = await self._find_contributions_ai(text)
        if contributions:
            insights['contributions'] = contributions

        # Extract limitations using AI
        limitations = await self._find_limitations_ai(text)
        if limitations:
            insights['limitations'] = limitations

        return insights

    async def _find_contributions_ai(self, text: str) -> Optional[str]:
        """Find contributions using OpenRouter API"""
        try:
            # Look for contributions section or introduction
            text_snippet = text[:3000]  # First 3000 chars likely have intro/contributions

            response = await self.openai_client.chat.completions.create(
                model=self.openrouter_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract the main contributions of this research paper in 2-3 bullet points."
                    },
                    {
                        "role": "user",
                        "content": text_snippet
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )

            contributions = response.choices[0].message.content.strip()
            return contributions if len(contributions) > 20 else None

        except Exception as e:
            logger.error(f"Error extracting contributions: {e}")
            return self._find_contributions(text)  # Fallback to regex

    async def _find_limitations_ai(self, text: str) -> Optional[str]:
        """Find limitations using OpenRouter API"""
        try:
            # Look for limitations section (usually near the end)
            text_snippet = text[-3000:]  # Last 3000 chars

            response = await self.openai_client.chat.completions.create(
                model=self.openrouter_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract the main limitations mentioned in this research paper in 2-3 bullet points."
                    },
                    {
                        "role": "user",
                        "content": text_snippet
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )

            limitations = response.choices[0].message.content.strip()
            return limitations if len(limitations) > 20 else None

        except Exception as e:
            logger.error(f"Error extracting limitations: {e}")
            return self._find_limitations(text)  # Fallback to regex

    def _find_contributions(self, text: str) -> Optional[str]:
        """Find contributions mentioned in paper (regex fallback)"""
        import re
        patterns = [
            r'(?:our|main|key)\s+contribution[s]?\s+(?:is|are|include)[s]?:?\s*(.{100,500})',
            r'we\s+(?:propose|introduce|present)\s+(.{100,500})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _find_limitations(self, text: str) -> Optional[str]:
        """Find limitations mentioned in paper (regex fallback)"""
        import re
        pattern = r'limitations?:?\s*(.{100,500})'
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

        return None

    async def compare_papers(self, paper_paths: List[str]) -> Dict:
        """
        Compare multiple papers

        Args:
            paper_paths: List of PDF paths

        Returns:
            Comparison analysis
        """
        logger.info(f"Comparing {len(paper_paths)} papers...")

        # Process all papers
        papers_data = []
        for path in paper_paths:
            try:
                data = await self.process_paper(path)
                papers_data.append(data)
            except Exception as e:
                logger.error(f"Error processing {path}: {e}")

        # Build comparison
        comparison = {
            'paper_count': len(papers_data),
            'common_keywords': self._find_common_keywords(papers_data),
            'methodologies': [p['key_insights'].get('methodology') for p in papers_data],
            'total_citations': sum(len(p.get('citations', [])) for p in papers_data),
        }

        return comparison

    def _find_common_keywords(self, papers_data: List[Dict]) -> List[str]:
        """Find keywords common across papers"""
        from collections import Counter

        all_keywords = []
        for paper in papers_data:
            all_keywords.extend(paper.get('keywords', []))

        keyword_counts = Counter(all_keywords)
        # Return keywords that appear in at least 2 papers
        common = [k for k, count in keyword_counts.items() if count >= 2]

        return common

    async def close(self):
        """Close API clients"""
        await self.semantic_scholar.close()
        if hasattr(self, 'openai_client'):
            await self.openai_client.close()

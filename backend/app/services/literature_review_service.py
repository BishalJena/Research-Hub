"""
Literature Review Service - AI-powered paper analysis and summarization
"""
from typing import Dict, List, Optional
import logging
import asyncio
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sentence_transformers import SentenceTransformer, util

from app.services.pdf_processor import PDFProcessor
from app.services.academic_api_client import SemanticScholarClient

logger = logging.getLogger(__name__)


class LiteratureReviewService:
    """Service for automated literature review"""

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.semantic_scholar = SemanticScholarClient()

        # Initialize models (lazy loading)
        self._summarizer = None
        self._embedding_model = None

    @property
    def summarizer(self):
        """Lazy load summarization model"""
        if self._summarizer is None:
            logger.info("Loading summarization model...")
            try:
                # Use BART for summarization (good for scientific text)
                self._summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("Summarization model loaded")
            except Exception as e:
                logger.error(f"Error loading summarization model: {e}")
                raise
        return self._summarizer

    @property
    def embedding_model(self):
        """Lazy load embedding model for semantic search"""
        if self._embedding_model is None:
            logger.info("Loading embedding model...")
            try:
                # Use SPECTER for scientific paper embeddings
                self._embedding_model = SentenceTransformer('allenai/specter')
                logger.info("Embedding model loaded")
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                # Fallback to general model
                self._embedding_model = SentenceTransformer('all-mpnet-base-v2')
        return self._embedding_model

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

        # Generate summaries for each section
        section_summaries = {}
        for section_name, section_text in sections.items():
            if section_text and len(section_text.split()) > 50:  # Only summarize substantial sections
                summary = self.summarize_text(section_text, max_length=150, min_length=50)
                section_summaries[section_name] = summary

        # Generate overall summary
        overall_summary = self.summarize_text(
            text[:4000],  # Use first 4000 chars for overall summary
            max_length=200,
            min_length=100
        )

        # Extract key insights
        key_insights = self._extract_key_insights(text, sections)

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

        logger.info("Paper processing complete")
        return result

    def summarize_text(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 50
    ) -> str:
        """
        Generate summary of text using AI

        Args:
            text: Text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length

        Returns:
            Summary text
        """
        if not text or len(text.split()) < min_length:
            return text

        try:
            # Truncate text if too long (BART max is 1024 tokens)
            words = text.split()
            if len(words) > 800:
                text = ' '.join(words[:800])

            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )

            return summary[0]['summary_text']

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback: return first few sentences
            sentences = text.split('.')[:3]
            return '. '.join(sentences) + '.'

    async def find_related_papers(
        self,
        query_text: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find papers related to the given text

        Args:
            query_text: Query text (abstract or summary)
            limit: Number of papers to return

        Returns:
            List of related papers
        """
        logger.info("Finding related papers...")

        try:
            # Search Semantic Scholar
            papers = await self.semantic_scholar.search_papers(
                query=query_text[:500],  # Limit query length
                limit=limit
            )

            # Calculate semantic similarity scores
            if papers and query_text:
                query_embedding = self.embedding_model.encode(query_text, convert_to_tensor=True)

                for paper in papers:
                    paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                    if paper_text.strip():
                        paper_embedding = self.embedding_model.encode(paper_text, convert_to_tensor=True)
                        similarity = util.pytorch_cos_sim(query_embedding, paper_embedding).item()
                        paper['relevance_score'] = similarity
                    else:
                        paper['relevance_score'] = 0.0

                # Sort by relevance
                papers = sorted(papers, key=lambda x: x.get('relevance_score', 0), reverse=True)

            return papers[:limit]

        except Exception as e:
            logger.error(f"Error finding related papers: {e}")
            return []

    def _extract_key_insights(self, text: str, sections: Dict[str, str]) -> Dict:
        """
        Extract key insights from paper

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
            if method_text:
                insights['methodology'] = self.summarize_text(method_text, max_length=100)

        # Extract results
        if 'results' in sections or 'evaluation' in sections:
            results_text = sections.get('results') or sections.get('evaluation', '')
            if results_text:
                insights['results'] = self.summarize_text(results_text, max_length=100)

        # Look for contributions in introduction or abstract
        contributions = self._find_contributions(text)
        if contributions:
            insights['contributions'] = contributions

        # Look for limitations
        limitations = self._find_limitations(text)
        if limitations:
            insights['limitations'] = limitations

        return insights

    def _find_contributions(self, text: str) -> Optional[str]:
        """Find contributions mentioned in paper"""
        # Look for phrases like "our contribution", "we propose", "we introduce"
        patterns = [
            r'(?:our|main|key)\s+contribution[s]?\s+(?:is|are|include)[s]?:?\s*(.{100,500})',
            r'we\s+(?:propose|introduce|present)\s+(.{100,500})',
        ]

        for pattern in patterns:
            import re
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _find_limitations(self, text: str) -> Optional[str]:
        """Find limitations mentioned in paper"""
        # Look for "limitations" section or mentions
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

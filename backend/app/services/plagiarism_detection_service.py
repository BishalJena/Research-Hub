"""
Plagiarism Detection Service - Multi-layered similarity detection
NOW USING: Cohere Embeddings API
"""
from typing import List, Dict, Tuple, Optional
import re
import hashlib
from collections import defaultdict
import logging
import cohere
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings
from app.services.academic_api_client import SemanticScholarClient

logger = logging.getLogger(__name__)


class PlagiarismDetectionService:
    """Service for detecting plagiarism using multiple techniques and Cohere API"""

    def __init__(self):
        # Initialize Semantic Scholar with API key from settings
        self.semantic_scholar = SemanticScholarClient(
            api_key=settings.SEMANTIC_SCHOLAR_API_KEY if settings.SEMANTIC_SCHOLAR_API_KEY else None
        )

        # Initialize Cohere API
        self._init_cohere()

    def _init_cohere(self):
        """Initialize Cohere API client"""
        if settings.COHERE_API_KEY:
            self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
            self.cohere_model = settings.COHERE_MODEL
            logger.info(f"✅ Cohere initialized: {self.cohere_model}")
        else:
            self.cohere_client = None
            logger.warning("⚠️ Cohere API key not found - semantic detection disabled")

    async def check_plagiarism(
        self,
        text: str,
        language: str = "en",
        check_online: bool = True
    ) -> Dict:
        """
        Check text for plagiarism using multiple techniques

        Args:
            text: Text to check
            language: Language of the text
            check_online: Whether to check against online sources

        Returns:
            Dictionary with plagiarism check results
        """
        logger.info(f"Starting plagiarism check ({len(text)} chars)")

        # Split text into chunks (paragraphs)
        chunks = self._chunk_text(text)
        logger.info(f"Split into {len(chunks)} chunks")

        all_matches = []

        # Layer 1: Fingerprint-based detection (fast, exact matches)
        fingerprint_matches = self._fingerprint_detection(chunks)
        all_matches.extend(fingerprint_matches)

        # Layer 2: N-gram overlap (near-duplicate detection)
        ngram_matches = self._ngram_detection(chunks)
        all_matches.extend(ngram_matches)

        # Layer 3: Semantic similarity (paraphrase detection) - Using Cohere!
        if self.cohere_client:
            semantic_matches = await self._semantic_detection(chunks, check_online)
            all_matches.extend(semantic_matches)
        else:
            logger.warning("⚠️ Skipping semantic detection - Cohere not available")

        # Remove duplicate matches
        unique_matches = self._deduplicate_matches(all_matches)

        # Calculate originality score
        originality_score = self._calculate_originality_score(text, unique_matches)

        # Generate statistics
        stats = self._calculate_statistics(text, unique_matches)

        result = {
            'originality_score': originality_score,
            'total_matches': len(unique_matches),
            'matches': unique_matches,
            'statistics': stats,
            'text_length': len(text),
            'word_count': len(text.split()),
            'language': language
        }

        logger.info(f"✅ Plagiarism check complete. Originality Score: {originality_score}%")
        return result

    def _chunk_text(self, text: str, min_chunk_size: int = 100) -> List[str]:
        """Split text into chunks (paragraphs or sentences)"""
        # Split by double newline (paragraphs)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        chunks = []
        for para in paragraphs:
            if len(para.split()) >= min_chunk_size:
                chunks.append(para)
            else:
                # Split long paragraphs into sentences
                sentences = re.split(r'[.!?]+', para)
                current_chunk = []
                current_length = 0

                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue

                    word_count = len(sent.split())
                    if current_length + word_count >= min_chunk_size:
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))
                        current_chunk = [sent]
                        current_length = word_count
                    else:
                        current_chunk.append(sent)
                        current_length += word_count

                if current_chunk:
                    chunks.append(' '.join(current_chunk))

        return chunks

    def _fingerprint_detection(self, chunks: List[str]) -> List[Dict]:
        """Layer 1: Fast fingerprint-based exact match detection"""
        logger.info("Running fingerprint detection...")

        matches = []
        # In a real implementation, you'd check against a database of fingerprints
        # For now, we'll create fingerprints for potential internal checking

        for i, chunk in enumerate(chunks):
            fingerprint = hashlib.md5(chunk.encode()).hexdigest()
            # Store fingerprint for future checks
            # In production, check against database of known fingerprints

        return matches  # Would return actual matches from database

    def _ngram_detection(
        self,
        chunks: List[str],
        n: int = 5,
        threshold: float = 0.6
    ) -> List[Dict]:
        """Layer 2: N-gram overlap detection for near-duplicates"""
        logger.info("Running n-gram detection...")

        matches = []

        def get_ngrams(text: str, n: int) -> set:
            """Extract n-grams from text"""
            words = text.lower().split()
            return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))

        # Compare each chunk pair
        for i in range(len(chunks)):
            for j in range(i+1, len(chunks)):
                ngrams_i = get_ngrams(chunks[i], n)
                ngrams_j = get_ngrams(chunks[j], n)

                if not ngrams_i or not ngrams_j:
                    continue

                # Jaccard similarity
                intersection = len(ngrams_i & ngrams_j)
                union = len(ngrams_i | ngrams_j)
                similarity = intersection / union if union > 0 else 0

                if similarity >= threshold:
                    matches.append({
                        'text': chunks[i][:200],
                        'source': f"Internal chunk {j}",
                        'similarity': similarity,
                        'start_pos': i * 500,  # Approximate
                        'end_pos': i * 500 + len(chunks[i]),
                        'type': 'near_duplicate'
                    })

        logger.info(f"Found {len(matches)} n-gram matches")
        return matches

    async def _semantic_detection(
        self,
        chunks: List[str],
        check_online: bool = True,
        threshold: float = 0.75
    ) -> List[Dict]:
        """
        Layer 3: Semantic similarity detection using Cohere Embeddings

        Detects paraphrased plagiarism by comparing semantic similarity
        """
        logger.info("Running semantic detection with Cohere...")

        matches = []

        if not check_online or not self.cohere_client:
            return matches

        try:
            # Encode all chunks using Cohere (batch processing!)
            logger.info(f"Embedding {len(chunks)} chunks with Cohere...")

            # Limit chunks for API efficiency (first 10 chunks)
            chunks_to_check = chunks[:10]

            chunk_response = self.cohere_client.embed(
                texts=[chunk[:2000] for chunk in chunks_to_check],  # Limit length
                model=self.cohere_model,
                input_type='search_document'
            )
            chunk_embeddings = np.array(chunk_response.embeddings)
            logger.info(f"✅ Generated {len(chunk_embeddings)} chunk embeddings")

            # Search for similar papers online for each chunk
            for i, chunk in enumerate(chunks_to_check):
                try:
                    # Search Semantic Scholar
                    logger.info(f"Searching Semantic Scholar for chunk {i+1}/{len(chunks_to_check)}...")
                    papers = await self.semantic_scholar.search_papers(
                        query=chunk[:500],  # Limit query length
                        limit=5  # Fewer papers for speed
                    )

                    if not papers:
                        logger.warning(f"No papers found on Semantic Scholar for chunk {i+1}")
                        continue

                    logger.info(f"Found {len(papers)} papers on Semantic Scholar for chunk {i+1}")

                    # Get paper texts
                    paper_texts = []
                    valid_papers = []
                    for paper in papers:
                        paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                        if paper_text.strip():
                            paper_texts.append(paper_text[:2000])
                            valid_papers.append(paper)

                    if not paper_texts:
                        continue

                    # Embed papers using Cohere (batch!)
                    papers_response = self.cohere_client.embed(
                        texts=paper_texts,
                        model=self.cohere_model,
                        input_type='search_query'
                    )
                    papers_embeddings = np.array(papers_response.embeddings)

                    # Calculate cosine similarity
                    similarities = cosine_similarity(
                        chunk_embeddings[i].reshape(1, -1),
                        papers_embeddings
                    )[0]

                    # Find matches above threshold
                    for paper, similarity in zip(valid_papers, similarities):
                        if similarity >= threshold:
                            matches.append({
                                'text': chunk[:200],
                                'source': paper.get('title', 'Unknown'),
                                'source_url': paper.get('url'),
                                'similarity': float(similarity),
                                'start_pos': i * 500,
                                'end_pos': i * 500 + len(chunk),
                                'type': 'paraphrase' if similarity < 0.9 else 'high_similarity',
                                'source_year': paper.get('year'),
                                'source_authors': [a.get('name') for a in paper.get('authors', [])][:3]
                            })

                except Exception as e:
                    logger.error(f"Error in semantic detection for chunk {i}: {e}")

            logger.info(f"✅ Found {len(matches)} semantic matches")
            return matches

        except Exception as e:
            logger.error(f"❌ Error in semantic detection: {e}")
            return []

    def _deduplicate_matches(self, matches: List[Dict]) -> List[Dict]:
        """Remove duplicate matches"""
        seen = set()
        unique = []

        for match in matches:
            key = (match.get('text', '')[:50], match.get('source', ''))
            if key not in seen:
                seen.add(key)
                unique.append(match)

        return unique

    def _calculate_originality_score(
        self,
        text: str,
        matches: List[Dict]
    ) -> float:
        """Calculate originality score (0-100)"""
        if not text:
            return 0.0

        total_words = len(text.split())
        if total_words == 0:
            return 0.0

        # Calculate matched words
        matched_words = 0
        for match in matches:
            match_text = match.get('text', '')
            matched_words += len(match_text.split())

        # Base score
        base_score = 100 - (matched_words / total_words * 100)
        base_score = max(0, min(100, base_score))

        # Apply penalties for high similarity matches
        penalty = 0
        for match in matches:
            similarity = match.get('similarity', 0)
            if similarity >= 0.9:
                penalty += 10
            elif similarity >= 0.8:
                penalty += 5
            elif similarity >= 0.7:
                penalty += 2

        final_score = max(0, base_score - penalty)
        return round(final_score, 2)

    def _calculate_statistics(
        self,
        text: str,
        matches: List[Dict]
    ) -> Dict:
        """Calculate statistics about matches"""
        total_words = len(text.split())

        matched_words = sum(
            len(m.get('text', '').split())
            for m in matches
        )

        # Count by type
        type_counts = defaultdict(int)
        for match in matches:
            match_type = match.get('type', 'unknown')
            type_counts[match_type] += 1

        # Unique sources
        sources = set(m.get('source', '') for m in matches)

        return {
            'total_words': total_words,
            'matched_words': matched_words,
            'match_percentage': (matched_words / total_words * 100) if total_words > 0 else 0,
            'unique_sources': len(sources),
            'matches_by_type': dict(type_counts),
            'highest_similarity': max((m.get('similarity', 0) for m in matches), default=0),
            'average_similarity': sum(m.get('similarity', 0) for m in matches) / len(matches) if matches else 0
        }

    async def suggest_citations(
        self,
        text: str,
        context: Optional[str] = None
    ) -> List[Dict]:
        """
        Suggest citations for claims in text

        Args:
            text: Text that may need citations
            context: Additional context

        Returns:
            List of suggested citations
        """
        logger.info("Suggesting citations...")

        suggestions = []

        # Identify claims that need citations
        claims = self._identify_claims(text)

        for claim in claims[:5]:  # Limit to 5 claims
            # Search for relevant papers
            papers = await self.semantic_scholar.search_papers(
                query=claim,
                limit=3  # Limit papers per claim
            )

            for paper in papers:
                suggestions.append({
                    'claim': claim,
                    'paper_title': paper.get('title'),
                    'authors': [a.get('name') for a in paper.get('authors', [])][:3],
                    'year': paper.get('year'),
                    'venue': paper.get('venue'),
                    'url': paper.get('url'),
                    'citation_count': paper.get('citationCount'),
                    'relevance': 0.8  # Could calculate actual relevance with Cohere
                })

        logger.info(f"✅ Generated {len(suggestions)} citation suggestions")
        return suggestions

    def _identify_claims(self, text: str) -> List[str]:
        """Identify claims/statements that might need citations"""
        claims = []

        # Simple heuristic: sentences with specific patterns
        sentences = re.split(r'[.!?]+', text)

        claim_patterns = [
            r'research shows?',
            r'studies? (?:have )?(?:shown|demonstrated|found|revealed)',
            r'evidence suggests?',
            r'according to',
            r'it (?:is|has been) (?:shown|demonstrated|proven)',
            r'experiments? (?:show|demonstrate)',
        ]

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) < 5:
                continue

            for pattern in claim_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(sentence)
                    break

        return claims[:10]  # Limit to 10 claims

    async def close(self):
        """Close API clients"""
        await self.semantic_scholar.close()

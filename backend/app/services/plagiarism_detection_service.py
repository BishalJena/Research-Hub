"""
Plagiarism Detection Service - Multi-layered similarity detection
"""
from typing import List, Dict, Tuple, Optional
import re
import hashlib
from collections import defaultdict
import logging

from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np

from app.services.academic_api_client import SemanticScholarClient

logger = logging.getLogger(__name__)


class PlagiarismDetectionService:
    """Service for detecting plagiarism using multiple techniques"""

    def __init__(self):
        self.semantic_scholar = SemanticScholarClient()

        # Initialize models (lazy loading)
        self._embedding_model = None
        self._cross_encoder = None

    @property
    def embedding_model(self):
        """Lazy load sentence embedding model"""
        if self._embedding_model is None:
            logger.info("Loading embedding model for plagiarism detection...")
            try:
                # Use all-mpnet for general text
                self._embedding_model = SentenceTransformer('all-mpnet-base-v2')
                logger.info("Embedding model loaded")
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                raise
        return self._embedding_model

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

        # Layer 3: Semantic similarity (paraphrase detection)
        semantic_matches = await self._semantic_detection(chunks, check_online)
        all_matches.extend(semantic_matches)

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

        logger.info(f"Plagiarism check complete. Score: {originality_score}")
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
        """Layer 3: Semantic similarity detection for paraphrases"""
        logger.info("Running semantic detection...")

        matches = []

        if not check_online:
            return matches

        # Encode all chunks
        chunk_embeddings = self.embedding_model.encode(
            chunks,
            convert_to_tensor=True,
            show_progress_bar=False
        )

        # Search for similar papers online for each chunk
        for i, chunk in enumerate(chunks[:5]):  # Limit to first 5 chunks for speed
            try:
                # Search Semantic Scholar
                papers = await self.semantic_scholar.search_papers(
                    query=chunk[:500],  # Limit query length
                    limit=10
                )

                for paper in papers:
                    paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                    if not paper_text.strip():
                        continue

                    # Calculate semantic similarity
                    paper_embedding = self.embedding_model.encode(
                        paper_text,
                        convert_to_tensor=True
                    )

                    similarity = util.pytorch_cos_sim(
                        chunk_embeddings[i],
                        paper_embedding
                    ).item()

                    if similarity >= threshold:
                        matches.append({
                            'text': chunk[:200],
                            'source': paper.get('title', 'Unknown'),
                            'source_url': paper.get('url'),
                            'similarity': similarity,
                            'start_pos': i * 500,
                            'end_pos': i * 500 + len(chunk),
                            'type': 'paraphrase' if similarity < 0.9 else 'high_similarity',
                            'source_year': paper.get('year'),
                            'source_authors': [a.get('name') for a in paper.get('authors', [])][:3]
                        })

            except Exception as e:
                logger.error(f"Error in semantic detection for chunk {i}: {e}")

        logger.info(f"Found {len(matches)} semantic matches")
        return matches

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

        for claim in claims:
            # Search for relevant papers
            papers = await self.semantic_scholar.search_papers(
                query=claim,
                limit=5
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
                    'relevance': 0.8  # Could calculate actual relevance
                })

        logger.info(f"Generated {len(suggestions)} citation suggestions")
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

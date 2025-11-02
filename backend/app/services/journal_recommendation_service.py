"""
Journal Recommendation Service - AI-powered journal matching
"""
from typing import List, Dict, Optional
from collections import defaultdict
import logging

from sentence_transformers import SentenceTransformer, util
import torch

logger = logging.getLogger(__name__)


class JournalRecommendationService:
    """Service for recommending suitable journals for papers"""

    def __init__(self):
        # Initialize models (lazy loading)
        self._embedding_model = None

        # In production, this would load from database
        # For now, we'll use a sample journal database
        self.journal_database = self._load_sample_journals()

    @property
    def embedding_model(self):
        """Lazy load embedding model"""
        if self._embedding_model is None:
            logger.info("Loading embedding model for journal matching...")
            try:
                # Use SPECTER for scientific papers
                self._embedding_model = SentenceTransformer('allenai/specter')
                logger.info("Embedding model loaded")
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                # Fallback to general model
                self._embedding_model = SentenceTransformer('all-mpnet-base-v2')
        return self._embedding_model

    async def recommend_journals(
        self,
        paper_abstract: str,
        paper_keywords: List[str] = None,
        preferences: Dict = None
    ) -> List[Dict]:
        """
        Recommend journals for a paper

        Args:
            paper_abstract: Paper abstract
            paper_keywords: Paper keywords
            preferences: User preferences (open_access, max_apc, min_impact_factor, etc.)

        Returns:
            List of recommended journals with scores
        """
        logger.info("Recommending journals...")

        if not paper_abstract or len(paper_abstract.split()) < 10:
            raise ValueError("Paper abstract too short for meaningful recommendations")

        # Set default preferences
        if preferences is None:
            preferences = {}

        # Step 1: Semantic matching
        semantic_scores = self._calculate_semantic_similarity(paper_abstract)

        # Step 2: Keyword matching
        keyword_scores = self._calculate_keyword_overlap(
            paper_keywords or [],
            semantic_scores
        )

        # Step 3: Apply user preferences (filtering)
        filtered_journals = self._apply_filters(self.journal_database, preferences)

        # Step 4: Calculate composite scores
        scored_journals = []
        for journal in filtered_journals:
            journal_id = journal['id']

            # Get individual scores
            semantic_score = semantic_scores.get(journal_id, 0.0)
            keyword_score = keyword_scores.get(journal_id, 0.0)

            # Calculate composite score
            composite_score = self._calculate_composite_score(
                semantic_score=semantic_score,
                keyword_score=keyword_score,
                impact_factor=journal.get('impact_factor', 0),
                time_to_publish=journal.get('avg_time_to_publish_days', 180),
                open_access=journal.get('open_access', False),
                acceptance_rate=journal.get('acceptance_rate', 50)
            )

            # Calculate fit score
            fit_score = self._calculate_fit_score(
                semantic_score, keyword_score, journal
            )

            # Estimate acceptance probability (mock for now)
            acceptance_probability = self._estimate_acceptance_probability(
                fit_score, journal
            )

            journal_result = {
                **journal,
                'semantic_score': semantic_score,
                'keyword_score': keyword_score,
                'composite_score': composite_score,
                'fit_score': fit_score,
                'acceptance_probability': acceptance_probability
            }

            scored_journals.append(journal_result)

        # Sort by composite score
        scored_journals.sort(key=lambda x: x['composite_score'], reverse=True)

        logger.info(f"Recommended {len(scored_journals)} journals")
        return scored_journals[:20]  # Top 20

    def _calculate_semantic_similarity(
        self,
        paper_abstract: str
    ) -> Dict[str, float]:
        """Calculate semantic similarity between paper and journals"""
        logger.info("Calculating semantic similarities...")

        # Encode paper abstract
        paper_embedding = self.embedding_model.encode(
            paper_abstract,
            convert_to_tensor=True
        )

        scores = {}

        for journal in self.journal_database:
            # Create journal profile text
            journal_profile = f"{journal['title']} {journal.get('description', '')} {' '.join(journal.get('keywords', []))}"

            # Encode journal profile
            journal_embedding = self.embedding_model.encode(
                journal_profile,
                convert_to_tensor=True
            )

            # Calculate cosine similarity
            similarity = util.pytorch_cos_sim(
                paper_embedding,
                journal_embedding
            ).item()

            scores[journal['id']] = similarity

        return scores

    def _calculate_keyword_overlap(
        self,
        paper_keywords: List[str],
        semantic_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate keyword overlap scores"""
        if not paper_keywords:
            # Return equal scores if no keywords
            return {j_id: 0.5 for j_id in semantic_scores}

        paper_keywords_lower = [k.lower() for k in paper_keywords]
        scores = {}

        for journal in self.journal_database:
            journal_keywords = [k.lower() for k in journal.get('keywords', [])]
            journal_subjects = [s.lower() for s in journal.get('subjects', [])]

            all_journal_terms = journal_keywords + journal_subjects

            if not all_journal_terms:
                scores[journal['id']] = 0.0
                continue

            # Calculate Jaccard similarity
            paper_set = set(paper_keywords_lower)
            journal_set = set(all_journal_terms)

            intersection = len(paper_set & journal_set)
            union = len(paper_set | journal_set)

            score = intersection / union if union > 0 else 0.0
            scores[journal['id']] = score

        return scores

    def _apply_filters(
        self,
        journals: List[Dict],
        preferences: Dict
    ) -> List[Dict]:
        """Filter journals based on user preferences"""
        filtered = journals

        # Filter by open access
        if preferences.get('open_access_only', False):
            filtered = [j for j in filtered if j.get('open_access', False)]

        # Filter by maximum APC
        if 'max_apc' in preferences:
            max_apc = preferences['max_apc']
            filtered = [
                j for j in filtered
                if j.get('apc_amount', 0) <= max_apc or not j.get('open_access')
            ]

        # Filter by minimum impact factor
        if 'min_impact_factor' in preferences:
            min_if = preferences['min_impact_factor']
            filtered = [
                j for j in filtered
                if j.get('impact_factor', 0) >= min_if
            ]

        # Filter by maximum time to publish
        if 'max_time_to_publish' in preferences:
            max_days = preferences['max_time_to_publish']
            filtered = [
                j for j in filtered
                if j.get('avg_time_to_publish_days', 365) <= max_days
            ]

        # Filter by required indexing
        if 'required_indexing' in preferences:
            required = preferences['required_indexing']
            if 'Scopus' in required:
                filtered = [j for j in filtered if j.get('scopus_indexed', False)]
            if 'Web of Science' in required:
                filtered = [j for j in filtered if j.get('web_of_science_indexed', False)]

        # Exclude predatory journals
        if preferences.get('exclude_predatory', True):
            filtered = [j for j in filtered if not j.get('is_predatory', False)]

        return filtered

    def _calculate_composite_score(
        self,
        semantic_score: float,
        keyword_score: float,
        impact_factor: float,
        time_to_publish: int,
        open_access: bool,
        acceptance_rate: float
    ) -> float:
        """Calculate composite score for journal"""
        # Normalize metrics
        norm_semantic = semantic_score  # Already 0-1
        norm_keyword = keyword_score  # Already 0-1
        norm_impact = min(impact_factor / 10.0, 1.0)  # Normalize by 10
        norm_time = 1.0 - min(time_to_publish / 365.0, 1.0)  # Lower is better
        norm_oa = 1.0 if open_access else 0.5
        norm_acceptance = acceptance_rate / 100.0  # 0-1

        # Weighted combination
        weights = {
            'semantic': 0.35,
            'keyword': 0.20,
            'impact': 0.15,
            'time': 0.10,
            'open_access': 0.10,
            'acceptance': 0.10
        }

        composite = (
            norm_semantic * weights['semantic'] +
            norm_keyword * weights['keyword'] +
            norm_impact * weights['impact'] +
            norm_time * weights['time'] +
            norm_oa * weights['open_access'] +
            norm_acceptance * weights['acceptance']
        )

        return composite

    def _calculate_fit_score(
        self,
        semantic_score: float,
        keyword_score: float,
        journal: Dict
    ) -> float:
        """Calculate how well the paper fits the journal"""
        # Simple combination of semantic and keyword scores
        fit = (semantic_score * 0.6 + keyword_score * 0.4)

        # Boost for highly cited journals (proxy for quality match)
        if journal.get('h_index', 0) > 50:
            fit *= 1.1

        return min(fit, 1.0)

    def _estimate_acceptance_probability(
        self,
        fit_score: float,
        journal: Dict
    ) -> float:
        """Estimate probability of acceptance"""
        # Base probability from journal acceptance rate
        base_prob = journal.get('acceptance_rate', 50) / 100.0

        # Adjust based on fit score
        adjustment = (fit_score - 0.5) * 0.3  # ±15%

        probability = base_prob + adjustment
        probability = max(0.05, min(0.95, probability))  # Clamp between 5-95%

        return round(probability, 2)

    def _load_sample_journals(self) -> List[Dict]:
        """
        Load sample journal database
        In production, this would load from database or external API
        """
        return [
            {
                'id': 'nature',
                'title': 'Nature',
                'publisher': 'Nature Publishing Group',
                'issn': '0028-0836',
                'website_url': 'https://www.nature.com',
                'scopus_indexed': True,
                'web_of_science_indexed': True,
                'impact_factor': 49.96,
                'h_index': 1089,
                'sjr_score': 20.0,
                'open_access': False,
                'apc_amount': 0,
                'avg_time_to_publish_days': 180,
                'acceptance_rate': 7.0,
                'subjects': ['Multidisciplinary', 'Science'],
                'keywords': ['research', 'science', 'nature', 'multidisciplinary'],
                'description': 'Premier international weekly journal of science',
                'country': 'UK',
                'is_predatory': False
            },
            {
                'id': 'plos-one',
                'title': 'PLOS ONE',
                'publisher': 'Public Library of Science',
                'issn': '1932-6203',
                'website_url': 'https://journals.plos.org/plosone/',
                'scopus_indexed': True,
                'web_of_science_indexed': True,
                'impact_factor': 3.24,
                'h_index': 436,
                'sjr_score': 0.99,
                'open_access': True,
                'apc_amount': 1825,
                'apc_currency': 'USD',
                'avg_time_to_publish_days': 90,
                'acceptance_rate': 50.0,
                'subjects': ['Multidisciplinary', 'Science'],
                'keywords': ['open access', 'research', 'science', 'multidisciplinary'],
                'description': 'Inclusive, peer-reviewed, open-access resource',
                'country': 'USA',
                'is_predatory': False
            },
            {
                'id': 'ieee-access',
                'title': 'IEEE Access',
                'publisher': 'IEEE',
                'issn': '2169-3536',
                'website_url': 'https://ieeeaccess.ieee.org',
                'scopus_indexed': True,
                'web_of_science_indexed': True,
                'impact_factor': 3.47,
                'h_index': 127,
                'sjr_score': 0.587,
                'open_access': True,
                'apc_amount': 1850,
                'apc_currency': 'USD',
                'avg_time_to_publish_days': 60,
                'acceptance_rate': 30.0,
                'subjects': ['Engineering', 'Computer Science', 'Technology'],
                'keywords': ['engineering', 'computer science', 'technology', 'open access'],
                'description': 'Multidisciplinary open access journal',
                'country': 'USA',
                'is_predatory': False
            },
            {
                'id': 'scientific-reports',
                'title': 'Scientific Reports',
                'publisher': 'Nature Publishing Group',
                'issn': '2045-2322',
                'website_url': 'https://www.nature.com/srep/',
                'scopus_indexed': True,
                'web_of_science_indexed': True,
                'impact_factor': 4.38,
                'h_index': 253,
                'sjr_score': 0.973,
                'open_access': True,
                'apc_amount': 2190,
                'apc_currency': 'USD',
                'avg_time_to_publish_days': 120,
                'acceptance_rate': 60.0,
                'subjects': ['Multidisciplinary', 'Science'],
                'keywords': ['research', 'open access', 'science'],
                'description': 'Open access journal from Nature',
                'country': 'UK',
                'is_predatory': False
            },
            {
                'id': 'arxiv',
                'title': 'arXiv (Preprint)',
                'publisher': 'Cornell University',
                'issn': None,
                'website_url': 'https://arxiv.org',
                'scopus_indexed': False,
                'web_of_science_indexed': False,
                'impact_factor': None,
                'h_index': None,
                'sjr_score': None,
                'open_access': True,
                'apc_amount': 0,
                'avg_time_to_publish_days': 1,
                'acceptance_rate': 100.0,
                'subjects': ['Physics', 'Mathematics', 'Computer Science'],
                'keywords': ['preprint', 'research', 'open access'],
                'description': 'Open-access archive for preprints',
                'country': 'USA',
                'is_predatory': False
            }
        ]

    async def get_journal_details(self, journal_id: str) -> Optional[Dict]:
        """Get detailed information about a specific journal"""
        for journal in self.journal_database:
            if journal['id'] == journal_id:
                return journal
        return None

    async def search_journals(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """Search for journals by name or keyword"""
        query_lower = query.lower()

        results = []
        for journal in self.journal_database:
            # Search in title, keywords, and subjects
            searchable_text = (
                journal['title'].lower() + ' ' +
                ' '.join(journal.get('keywords', [])).lower() + ' ' +
                ' '.join(journal.get('subjects', [])).lower()
            )

            if query_lower in searchable_text:
                results.append(journal)

        return results[:limit]

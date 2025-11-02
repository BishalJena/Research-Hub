"""
Academic API Clients - Interfaces to external academic databases
"""
import aiohttp
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SemanticScholarClient:
    """Client for Semantic Scholar API"""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = None

    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def search_papers(
        self,
        query: str,
        fields: List[str] = None,
        limit: int = 100,
        year: str = None
    ) -> List[Dict]:
        """
        Search for papers on Semantic Scholar

        Args:
            query: Search query
            fields: Fields to return (title, abstract, authors, citations, etc.)
            limit: Maximum number of results
            year: Year filter (e.g., "2023-2024")

        Returns:
            List of paper dictionaries
        """
        if fields is None:
            fields = ["paperId", "title", "abstract", "year", "citationCount",
                     "authors", "venue", "publicationDate", "url", "fieldsOfStudy"]

        session = await self._get_session()

        params = {
            "query": query,
            "fields": ",".join(fields),
            "limit": limit
        }

        if year:
            params["year"] = year

        try:
            async with session.get(f"{self.BASE_URL}/paper/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Semantic Scholar API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error calling Semantic Scholar API: {e}")
            return []

    async def get_paper_details(self, paper_id: str) -> Optional[Dict]:
        """Get detailed information about a specific paper"""
        session = await self._get_session()

        fields = ["paperId", "title", "abstract", "year", "citationCount",
                 "authors", "venue", "publicationDate", "url", "fieldsOfStudy",
                 "citations", "references"]

        try:
            async with session.get(
                f"{self.BASE_URL}/paper/{paper_id}",
                params={"fields": ",".join(fields)}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting paper details: {e}")
            return None

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()


class OpenAlexClient:
    """Client for OpenAlex API"""

    BASE_URL = "https://api.openalex.org"

    def __init__(self, email: str):
        """
        Initialize OpenAlex client

        Args:
            email: Your email for polite pool (faster, more reliable)
        """
        self.email = email
        self.session = None

    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def search_works(
        self,
        query: str = None,
        filter_params: Dict = None,
        per_page: int = 100
    ) -> List[Dict]:
        """
        Search for works (papers) on OpenAlex

        Args:
            query: Search query
            filter_params: Filter parameters (e.g., {"publication_year": "2023"})
            per_page: Results per page

        Returns:
            List of work dictionaries
        """
        session = await self._get_session()

        params = {
            "mailto": self.email,
            "per-page": per_page
        }

        if query:
            params["search"] = query

        if filter_params:
            filter_str = ",".join([f"{k}:{v}" for k, v in filter_params.items()])
            params["filter"] = filter_str

        try:
            async with session.get(f"{self.BASE_URL}/works", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    logger.error(f"OpenAlex API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error calling OpenAlex API: {e}")
            return []

    async def get_trending_concepts(self, per_page: int = 50) -> List[Dict]:
        """Get trending concepts/topics"""
        session = await self._get_session()

        params = {
            "mailto": self.email,
            "per-page": per_page,
            "sort": "cited_by_count:desc"
        }

        try:
            async with session.get(f"{self.BASE_URL}/concepts", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                return []
        except Exception as e:
            logger.error(f"Error getting trending concepts: {e}")
            return []

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()


class ArXivClient:
    """Client for arXiv API"""

    BASE_URL = "http://export.arxiv.org/api/query"

    async def search_papers(
        self,
        query: str,
        max_results: int = 100,
        sort_by: str = "submittedDate",
        sort_order: str = "descending"
    ) -> List[Dict]:
        """
        Search for papers on arXiv

        Args:
            query: Search query
            max_results: Maximum number of results
            sort_by: Sort by (relevance, lastUpdatedDate, submittedDate)
            sort_order: Sort order (ascending, descending)

        Returns:
            List of paper dictionaries
        """
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params) as response:
                    if response.status == 200:
                        text = await response.text()
                        return self._parse_arxiv_response(text)
                    else:
                        logger.error(f"arXiv API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error calling arXiv API: {e}")
            return []

    def _parse_arxiv_response(self, xml_text: str) -> List[Dict]:
        """Parse arXiv XML response to list of dictionaries"""
        import xml.etree.ElementTree as ET

        papers = []
        try:
            root = ET.fromstring(xml_text)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}

            for entry in root.findall('atom:entry', namespace):
                paper = {
                    'id': entry.find('atom:id', namespace).text if entry.find('atom:id', namespace) is not None else None,
                    'title': entry.find('atom:title', namespace).text.strip() if entry.find('atom:title', namespace) is not None else None,
                    'abstract': entry.find('atom:summary', namespace).text.strip() if entry.find('atom:summary', namespace) is not None else None,
                    'published': entry.find('atom:published', namespace).text if entry.find('atom:published', namespace) is not None else None,
                    'authors': [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)],
                    'categories': [cat.get('term') for cat in entry.findall('atom:category', namespace)],
                    'pdf_url': None
                }

                # Get PDF link
                for link in entry.findall('atom:link', namespace):
                    if link.get('title') == 'pdf':
                        paper['pdf_url'] = link.get('href')
                        break

                papers.append(paper)

        except Exception as e:
            logger.error(f"Error parsing arXiv response: {e}")

        return papers


class CrossRefClient:
    """Client for CrossRef API"""

    BASE_URL = "https://api.crossref.org"

    def __init__(self, email: str):
        """
        Initialize CrossRef client

        Args:
            email: Your email for polite pool
        """
        self.email = email
        self.session = None

    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            headers = {"User-Agent": f"SmartResearchHub/1.0 (mailto:{self.email})"}
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def search_works(
        self,
        query: str,
        rows: int = 100,
        sort: str = "score",
        order: str = "desc"
    ) -> List[Dict]:
        """
        Search for works on CrossRef

        Args:
            query: Search query
            rows: Number of results
            sort: Sort field
            order: Sort order

        Returns:
            List of work dictionaries
        """
        session = await self._get_session()

        params = {
            "query": query,
            "rows": rows,
            "sort": sort,
            "order": order
        }

        try:
            async with session.get(f"{self.BASE_URL}/works", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("message", {}).get("items", [])
                else:
                    logger.error(f"CrossRef API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error calling CrossRef API: {e}")
            return []

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

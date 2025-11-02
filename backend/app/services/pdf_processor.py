"""
PDF Processing Service - Extract text and metadata from PDFs
"""
import PyPDF2
import pdfplumber
from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF files to extract text and metadata"""

    def __init__(self):
        self.section_headers = [
            "abstract", "introduction", "literature review", "related work",
            "methodology", "methods", "approach", "implementation",
            "results", "evaluation", "discussion", "conclusion",
            "future work", "references", "acknowledgments"
        ]

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text as string
        """
        logger.info(f"Extracting text from PDF: {pdf_path}")

        text = ""

        try:
            # Try pdfplumber first (better for complex PDFs)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"

            if not text.strip():
                # Fallback to PyPDF2
                logger.info("pdfplumber failed, trying PyPDF2...")
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"

            logger.info(f"Extracted {len(text)} characters from PDF")
            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def extract_metadata(self, pdf_path: str) -> Dict:
        """
        Extract metadata from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with metadata
        """
        metadata = {
            'title': None,
            'author': None,
            'subject': None,
            'creator': None,
            'producer': None,
            'creation_date': None,
            'num_pages': 0
        }

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Get document info
                if pdf_reader.metadata:
                    metadata.update({
                        'title': pdf_reader.metadata.get('/Title', None),
                        'author': pdf_reader.metadata.get('/Author', None),
                        'subject': pdf_reader.metadata.get('/Subject', None),
                        'creator': pdf_reader.metadata.get('/Creator', None),
                        'producer': pdf_reader.metadata.get('/Producer', None),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', None),
                    })

                metadata['num_pages'] = len(pdf_reader.pages)

            logger.info(f"Extracted metadata: {metadata}")
            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return metadata

    def segment_into_sections(self, text: str) -> Dict[str, str]:
        """
        Segment paper text into sections

        Args:
            text: Full paper text

        Returns:
            Dictionary mapping section names to text
        """
        logger.info("Segmenting text into sections...")

        sections = {}
        lines = text.split('\n')

        current_section = "introduction"
        current_text = []

        for line in lines:
            line_lower = line.strip().lower()

            # Check if this line is a section header
            is_header = False
            for header in self.section_headers:
                # Match "1. Introduction" or "Introduction" or "1 Introduction"
                pattern = r'^\d*\.?\s*' + re.escape(header) + r'\s*$'
                if re.match(pattern, line_lower, re.IGNORECASE):
                    # Save previous section
                    if current_text:
                        sections[current_section] = '\n'.join(current_text).strip()

                    # Start new section
                    current_section = header
                    current_text = []
                    is_header = True
                    break

            if not is_header and line.strip():
                current_text.append(line)

        # Save last section
        if current_text:
            sections[current_section] = '\n'.join(current_text).strip()

        logger.info(f"Found {len(sections)} sections")
        return sections

    def extract_citations(self, text: str) -> List[str]:
        """
        Extract citations from text

        Args:
            text: Paper text

        Returns:
            List of citation strings
        """
        citations = []

        # Pattern for [1], [2,3], etc.
        numeric_citations = re.findall(r'\[(\d+(?:,\s*\d+)*)\]', text)
        citations.extend([f"[{c}]" for c in numeric_citations])

        # Pattern for (Author, Year)
        author_year = re.findall(r'\(([A-Z][a-z]+(?:\s+et\s+al\.?)?,\s*\d{4})\)', text)
        citations.extend([f"({c})" for c in author_year])

        # Deduplicate
        citations = list(set(citations))

        logger.info(f"Extracted {len(citations)} citations")
        return citations

    def extract_abstract(self, text: str) -> Optional[str]:
        """
        Extract abstract from paper text

        Args:
            text: Full paper text

        Returns:
            Abstract text or None
        """
        # Look for "Abstract" section
        pattern = r'abstract\s*[:\-]?\s*\n(.*?)(?=\n\s*(?:introduction|keywords|1\.|i\.))'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            abstract = match.group(1).strip()
            logger.info(f"Extracted abstract ({len(abstract)} chars)")
            return abstract

        return None

    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from paper

        Args:
            text: Paper text

        Returns:
            List of keywords
        """
        # Look for "Keywords:" section
        pattern = r'keywords?\s*[:\-]\s*(.*?)(?=\n\s*\n|introduction|1\.)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            keywords_text = match.group(1).strip()
            # Split by comma or semicolon
            keywords = [k.strip() for k in re.split(r'[,;]', keywords_text)]
            keywords = [k for k in keywords if k and len(k) < 50]  # Filter out invalid entries

            logger.info(f"Extracted {len(keywords)} keywords")
            return keywords

        return []

    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())

    def get_page_count(self, pdf_path: str) -> int:
        """Get number of pages in PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            logger.error(f"Error counting pages: {e}")
            return 0

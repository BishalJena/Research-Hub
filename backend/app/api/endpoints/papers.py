from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from app.core.database import get_db
from app.models.user import User
from app.models.paper import Paper, PaperStatus
from app.api.dependencies.auth import get_current_user
from app.schemas.paper import (
    PaperUploadResponse,
    PaperResponse,
    PaperDetailResponse,
    PaperSummaryResponse,
    RelatedPaper
)
from app.services.literature_review_service import LiteratureReviewService
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def list_papers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all papers for current user"""
    papers = db.query(Paper).filter(Paper.user_id == current_user.id).all()
    
    # Format for frontend
    formatted_papers = []
    for paper in papers:
        formatted_papers.append({
            "id": paper.id,
            "title": paper.title,
            "filename": paper.title + ".pdf",
            "uploaded_at": paper.created_at.isoformat() if paper.created_at else None,
            "created_at": paper.created_at.isoformat() if paper.created_at else None,
            "processed": paper.status == PaperStatus.COMPLETED,
            "status": paper.status.value if paper.status else "draft",
            "summary": paper.summary,
            "methodology": paper.key_insights.get("methodology") if paper.key_insights else None,
            "key_findings": paper.key_insights.get("key_findings") if paper.key_insights else None,
            "processing_progress": paper.processing_progress or 0,
            "file_size": paper.file_size,
            "abstract": paper.abstract,
            "keywords": paper.keywords
        })
    
    return {"papers": formatted_papers}


@router.post("/upload", response_model=PaperUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a research paper (PDF)

    - **file**: PDF file to upload
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE} bytes"
        )

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.pdf")

    with open(file_path, 'wb') as f:
        f.write(contents)

    # Create paper record
    paper = Paper(
        user_id=current_user.id,
        title=file.filename.replace('.pdf', ''),
        file_path=file_path,
        file_size=len(contents),
        status=PaperStatus.DRAFT,
        language="en"
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return PaperUploadResponse(
        paper_id=paper.id,
        filename=file.filename,
        status="uploaded",
        message="Paper uploaded successfully. Use /papers/{paper_id}/process to analyze it."
    )


@router.get("/{paper_id}", response_model=PaperDetailResponse)
async def get_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paper details"""
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.user_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )

    return paper


@router.post("/{paper_id}/process", response_model=PaperSummaryResponse)
async def process_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Process paper - extract text, generate summary, find related papers

    This may take a few minutes for large papers.
    """
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.user_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )

    if not paper.file_path or not os.path.exists(paper.file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paper file not found"
        )

    # Update status
    paper.status = PaperStatus.PROCESSING
    db.commit()

    try:
        # Process paper
        service = LiteratureReviewService()
        result = await service.process_paper(paper.file_path)

        # Update paper with results
        paper.abstract = result.get('abstract')
        paper.keywords = result.get('keywords')
        paper.full_text = result.get('text')
        paper.summary = result.get('overall_summary')
        paper.key_insights = result.get('key_insights')
        paper.extracted_citations = result.get('citations')
        paper.related_papers = [
            {
                'title': p.get('title'),
                'authors': [a.get('name') for a in p.get('authors', [])],
                'year': p.get('year'),
                'url': p.get('url')
            }
            for p in result.get('related_papers', [])[:10]
        ]
        paper.status = PaperStatus.COMPLETED
        paper.processing_progress = 100

        db.commit()
        db.refresh(paper)

        # Cleanup in background
        if background_tasks:
            background_tasks.add_task(service.close)
        else:
            await service.close()

        return PaperSummaryResponse(
            paper_id=paper.id,
            overall_summary=result.get('overall_summary'),
            section_summaries=result.get('section_summaries', {}),
            key_insights=result.get('key_insights', {}),
            word_count=result.get('word_count', 0),
            page_count=result.get('page_count', 0)
        )

    except Exception as e:
        paper.status = PaperStatus.DRAFT
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing paper: {str(e)}"
        )


@router.get("/{paper_id}/related", response_model=List[RelatedPaper])
async def get_related_papers(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get papers related to this paper"""
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.user_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )

    # Return cached related papers if available
    if paper.related_papers:
        return [
            RelatedPaper(
                title=p.get('title', ''),
                authors=p.get('authors', []),
                year=p.get('year'),
                url=p.get('url'),
                relevance_score=0.8  # Placeholder
            )
            for p in paper.related_papers
        ]

    # Otherwise, find related papers
    if paper.abstract or paper.summary:
        service = LiteratureReviewService()
        try:
            query_text = paper.abstract if paper.abstract else paper.summary
            related = await service.find_related_papers(query_text, limit=10)

            return [
                RelatedPaper(
                    paper_id=p.get('paperId'),
                    title=p.get('title', ''),
                    authors=[a.get('name') for a in p.get('authors', [])],
                    year=p.get('year'),
                    abstract=p.get('abstract'),
                    citation_count=p.get('citationCount'),
                    url=p.get('url'),
                    relevance_score=p.get('relevance_score', 0.0)
                )
                for p in related
            ]
        finally:
            await service.close()

    return []


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a paper"""
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.user_id == current_user.id
    ).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )

    # Delete file if exists
    if paper.file_path and os.path.exists(paper.file_path):
        os.remove(paper.file_path)

    # Delete from database
    db.delete(paper)
    db.commit()

    return None

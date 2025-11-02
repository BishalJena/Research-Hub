from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.plagiarism_check import PlagiarismCheck
from app.api.dependencies.auth import get_current_user
from app.schemas.plagiarism import (
    PlagiarismCheckRequest,
    PlagiarismCheckResponse,
    PlagiarismReportResponse,
    CitationSuggestionRequest,
    CitationSuggestionResponse,
    PlagiarismMatch,
    PlagiarismStatistics
)
from app.services.plagiarism_detection_service import PlagiarismDetectionService

router = APIRouter()


@router.post("/check", response_model=PlagiarismCheckResponse)
async def check_plagiarism(
    request: PlagiarismCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Check text for plagiarism using multi-layered detection

    - **text**: Text to check (minimum 100 characters)
    - **language**: Language of the text (default: en)
    - **check_online**: Whether to check against online sources

    Returns plagiarism report with:
    - Originality score (0-100)
    - Matched segments
    - Source information
    - Statistics
    """
    service = PlagiarismDetectionService()

    try:
        # Run plagiarism check
        result = await service.check_plagiarism(
            text=request.text,
            language=request.language,
            check_online=request.check_online
        )

        # Save check to database
        check_record = PlagiarismCheck(
            user_id=current_user.id,
            text=request.text,
            language=request.language,
            originality_score=result['originality_score'],
            total_matches=result['total_matches'],
            matches=result['matches'],
            total_words=result['statistics']['total_words'],
            matched_words=result['statistics']['matched_words'],
            unique_sources=result['statistics']['unique_sources'],
            status="completed",
            completed_at=datetime.utcnow()
        )

        db.add(check_record)
        db.commit()
        db.refresh(check_record)

        # Cleanup in background
        if background_tasks:
            background_tasks.add_task(service.close)
        else:
            await service.close()

        # Convert to response model
        return PlagiarismCheckResponse(
            originality_score=result['originality_score'],
            total_matches=result['total_matches'],
            matches=[PlagiarismMatch(**m) for m in result['matches']],
            statistics=PlagiarismStatistics(**result['statistics']),
            text_length=result['text_length'],
            word_count=result['word_count'],
            language=result['language']
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking plagiarism: {str(e)}"
        )


@router.get("/report/{check_id}", response_model=PlagiarismReportResponse)
async def get_plagiarism_report(
    check_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a plagiarism check report by ID

    Returns the saved plagiarism check results.
    """
    check = db.query(PlagiarismCheck).filter(
        PlagiarismCheck.id == check_id,
        PlagiarismCheck.user_id == current_user.id
    ).first()

    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plagiarism check not found"
        )

    return check


@router.get("/history", response_model=list[PlagiarismReportResponse])
async def get_plagiarism_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Get plagiarism check history for current user

    - **limit**: Maximum number of results to return
    """
    checks = db.query(PlagiarismCheck).filter(
        PlagiarismCheck.user_id == current_user.id
    ).order_by(
        PlagiarismCheck.created_at.desc()
    ).limit(limit).all()

    return checks


@router.post("/citations/suggest", response_model=CitationSuggestionResponse)
async def suggest_citations(
    request: CitationSuggestionRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Suggest citations for claims in text

    Identifies statements that need citations and suggests
    relevant academic papers.

    - **text**: Text containing claims
    - **context**: Optional additional context
    """
    service = PlagiarismDetectionService()

    try:
        suggestions = await service.suggest_citations(
            text=request.text,
            context=request.context
        )

        # Cleanup in background
        if background_tasks:
            background_tasks.add_task(service.close)
        else:
            await service.close()

        return CitationSuggestionResponse(
            suggestions=suggestions,
            total_suggestions=len(suggestions)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suggesting citations: {str(e)}"
        )


@router.delete("/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plagiarism_check(
    check_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a plagiarism check record"""
    check = db.query(PlagiarismCheck).filter(
        PlagiarismCheck.id == check_id,
        PlagiarismCheck.user_id == current_user.id
    ).first()

    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plagiarism check not found"
        )

    db.delete(check)
    db.commit()

    return None

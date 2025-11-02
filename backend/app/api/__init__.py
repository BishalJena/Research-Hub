from fastapi import APIRouter
from app.api.endpoints import auth, users, papers, plagiarism, journals, topics, government

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(plagiarism.router, prefix="/plagiarism", tags=["plagiarism"])
api_router.include_router(journals.router, prefix="/journals", tags=["journals"])
api_router.include_router(topics.router, prefix="/topics", tags=["topics"])
api_router.include_router(government.router, prefix="/government", tags=["government", "innovation"])

from app.models.user import User
from app.models.paper import Paper, PaperStatus
from app.models.plagiarism_check import PlagiarismCheck
from app.models.journal import Journal

__all__ = ["User", "Paper", "PaperStatus", "PlagiarismCheck", "Journal"]

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    institution: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    preferred_language: str = "en"


class UserResponse(UserBase):
    id: int
    apcce_id: Optional[str] = None
    research_interests: Optional[List[str]] = None
    orcid: Optional[str] = None
    google_scholar_id: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    institution: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    research_interests: Optional[List[str]] = None
    orcid: Optional[str] = None
    google_scholar_id: Optional[str] = None
    preferred_language: Optional[str] = None

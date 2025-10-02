from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator

import hashlib

class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(..., description="Must be true to accept")
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)

    user_agent: Optional[str] = None
    submission_id: Optional[str] = None

  
    def to_safe_dict(self) -> dict:
        d = self.dict()
        d["submission_id"] = self.compute_submission_id()
        d["email"] = hashlib.sha256(self.email.encode()).hexdigest()
        d["age"] = hashlib.sha256(str(self.age).encode()).hexdigest()
        return d

    def compute_submission_id(self) -> str:
        """Return given submission_id or compute one from email+datehour."""
        if self.submission_id:
            return self.submission_id
        key = f"{self.email}{datetime.utcnow().strftime('%Y%m%d%H')}"
        return hashlib.sha256(key.encode()).hexdigest()

    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("consent")
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v

        
class StoredSurveyRecord(BaseModel):
    name: str
    email: str   # already hashed
    age: str     # already hashed
    consent: bool
    rating: int
    comments: Optional[str]
    source: str = "other"
    user_agent: Optional[str]
    submission_id: Optional[str] = None
    received_at: datetime
    ip: str

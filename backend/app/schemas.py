from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class CredentialsInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisterInput(CredentialsInput):
    full_name: str = Field(min_length=1, max_length=160)


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=160)


class CourseInput(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=200, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str = ""
    thumbnail_url: HttpUrl | None = None
    instructor_name: str = "Shahil Academy"
    level: str = "All levels"
    duration_minutes: int = Field(default=0, ge=0)
    price: float | None = Field(default=None, ge=0)
    status: Literal["draft", "published", "archived"] = "draft"
    is_public: bool = True


class ModuleInput(BaseModel):
    course_id: str
    title: str = Field(min_length=1, max_length=180)
    description: str = ""
    position: int = Field(default=0, ge=0)
    status: Literal["draft", "published"] = "draft"


class TopicInput(BaseModel):
    module_id: str
    title: str = Field(min_length=1, max_length=180)
    description: str = ""
    video_url: str | None = None
    position: int = Field(default=0, ge=0)
    duration_minutes: int = Field(default=0, ge=0)
    status: Literal["draft", "published"] = "draft"
    doubts_enabled: bool = True
    attempt_limit: int | None = Field(default=None, ge=1)
    passing_percentage: float = Field(default=0, ge=0, le=100)
    results_visible: bool = True
    answers_visible: bool = False
    explanations_visible: bool = False


class ResourceInput(BaseModel):
    topic_id: str
    title: str = Field(min_length=1, max_length=180)
    description: str = ""
    resource_type: Literal["link", "pdf", "document", "archive"] = "link"
    external_url: HttpUrl
    position: int = Field(default=0, ge=0)
    is_published: bool = True


class QuestionInput(BaseModel):
    topic_id: str
    prompt: str = Field(min_length=1, max_length=4000)
    question_type: Literal["multiple_choice", "true_false", "short_answer"] = "multiple_choice"
    options: list[str] = Field(default_factory=list, max_length=20)
    correct_answer: str = Field(min_length=1, max_length=1000)
    explanation: str = ""
    marks: float = Field(default=1, gt=0)
    position: int = Field(default=0, ge=0)
    is_published: bool = True


class EnrollmentInput(BaseModel):
    student_id: str
    course_id: str
    status: Literal["active", "revoked"] = "active"
    expires_at: datetime | None = None


class DoubtInput(BaseModel):
    topic_id: str
    message: str = Field(min_length=1, max_length=10000)


class ReplyInput(BaseModel):
    message: str = Field(min_length=1, max_length=10000)


class AnnouncementInput(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    message: str = Field(min_length=1, max_length=10000)
    course_id: str | None = None
    status: Literal["draft", "published", "archived"] = "draft"


class QuizSubmission(BaseModel):
    answers: dict[str, str] = Field(max_length=200)


class ModelSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

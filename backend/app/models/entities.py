import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def new_id() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class Profile(TimestampMixin, Base):
    __tablename__ = "profiles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="student", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Course(TimestampMixin, Base):
    __tablename__ = "courses"
    __table_args__ = (UniqueConstraint("slug"), Index("ix_courses_publication_status", "status", "is_public"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048))
    instructor_name: Mapped[str] = mapped_column(String(160), default="Shahil Academy", nullable=False)
    level: Mapped[str] = mapped_column(String(40), default="All levels", nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    price: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Module(TimestampMixin, Base):
    __tablename__ = "modules"
    __table_args__ = (Index("ix_modules_course_order", "course_id", "position"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)


class Topic(TimestampMixin, Base):
    __tablename__ = "topics"
    __table_args__ = (Index("ix_topics_module_order", "module_id", "position"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    module_id: Mapped[str] = mapped_column(ForeignKey("modules.id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    video_provider: Mapped[str | None] = mapped_column(String(30))
    video_ref: Mapped[str | None] = mapped_column(String(32))
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    doubts_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    attempt_limit: Mapped[int | None] = mapped_column(Integer)
    passing_percentage: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    results_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    answers_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    explanations_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class TopicResource(TimestampMixin, Base):
    __tablename__ = "topic_resources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    resource_type: Mapped[str] = mapped_column(String(30), default="link", nullable=False)
    external_url: Mapped[str | None] = mapped_column(String(2048))
    storage_key: Mapped[str | None] = mapped_column(String(512))
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Enrollment(TimestampMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "course_id"), Index("ix_enrollments_student_status", "student_id", "status"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    student_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="RESTRICT"), nullable=False)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TopicProgress(TimestampMixin, Base):
    __tablename__ = "topic_progress"
    __table_args__ = (UniqueConstraint("student_id", "topic_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    student_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="RESTRICT"), nullable=False, index=True)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_visited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Bookmark(TimestampMixin, Base):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("student_id", "topic_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    student_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False)


class Question(TimestampMixin, Base):
    __tablename__ = "questions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(20), default="multiple_choice", nullable=False)
    options: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    marks: Mapped[float] = mapped_column(Float, default=1, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class QuizAttempt(TimestampMixin, Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = (Index("ix_attempt_student_topic", "student_id", "topic_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    student_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="RESTRICT"), nullable=False)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    attempt_id: Mapped[str] = mapped_column(ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    awarded_marks: Mapped[float] = mapped_column(Float, nullable=False)


class Doubt(TimestampMixin, Base):
    __tablename__ = "doubts"
    __table_args__ = (Index("ix_doubts_status_created", "status", "created_at"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    student_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="RESTRICT"), nullable=False, index=True)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)


class DoubtReply(TimestampMixin, Base):
    __tablename__ = "doubt_replies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    doubt_id: Mapped[str] = mapped_column(ForeignKey("doubts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="RESTRICT"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)


class Announcement(TimestampMixin, Base):
    __tablename__ = "announcements"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    author_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    course_id: Mapped[str | None] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_actor_created", "actor_id", "created_at"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    actor_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="RESTRICT"), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

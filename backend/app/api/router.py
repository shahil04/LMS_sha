import json
import base64
import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.config import settings
from app.db.session import get_db
from app.models import (
    Announcement, AuditLog, Bookmark, Course, CourseIdSequence, Doubt, DoubtReply, Enrollment,
    Module, Profile, Question, QuizAnswer, QuizAttempt, Topic, TopicProgress,
    TopicResource,
)
from app.schemas import (
    AnnouncementInput, CourseInput, CredentialsInput, DoubtInput, EnrollmentInput, ModuleInput,
    ProfileUpdate, QuestionInput, QuizSubmission, ReplyInput, ResourceInput,
    RegisterInput, TopicInput,
)

router = APIRouter(prefix="/api/v1")

_PASSWORD_HASH_ITERATIONS = 600_000
_PASSWORD_SALT_BYTES = 16


def _password_hash(password: str) -> str:
    salt = secrets.token_bytes(_PASSWORD_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PASSWORD_HASH_ITERATIONS)
    return "$".join((
        "pbkdf2_sha256", str(_PASSWORD_HASH_ITERATIONS),
        base64.b64encode(salt).decode(), base64.b64encode(digest).decode(),
    ))


def _verify_password(password: str, encoded: str | None) -> bool:
    if not encoded:
        return False
    try:
        scheme, iterations, salt, expected = encoded.split("$")
        if scheme != "pbkdf2_sha256" or int(iterations) != _PASSWORD_HASH_ITERATIONS:
            return False
        salt_bytes = base64.b64decode(salt)
        expected_bytes = base64.b64decode(expected)
        if len(salt_bytes) != _PASSWORD_SALT_BYTES or len(expected_bytes) != 32:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt_bytes, _PASSWORD_HASH_ITERATIONS,
        )
        return hmac.compare_digest(digest, expected_bytes)
    except (ValueError, TypeError):
        return False


def _auth_response(profile: Profile) -> dict:
    if not settings.jwt_secret_key:
        raise HTTPException(status_code=503, detail="JWT_SECRET_KEY is not configured")
    if settings.jwt_algorithm not in {"HS256", "HS384", "HS512"}:
        raise HTTPException(status_code=503, detail="JWT_ALGORITHM must be an HMAC algorithm")
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": profile.id,
            "email": profile.email,
            "aud": "authenticated",
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return {"access_token": token, "token_type": "bearer", "profile": _profile_dict(profile)}


def _ensure_jwt_configured() -> None:
    if not settings.jwt_secret_key:
        raise HTTPException(status_code=503, detail="JWT_SECRET_KEY is not configured")
    if settings.jwt_algorithm not in {"HS256", "HS384", "HS512"}:
        raise HTTPException(status_code=503, detail="JWT_ALGORITHM must be an HMAC algorithm")


def _course_dict(course: Course) -> dict:
    return {
        "id": course.id, "title": course.title, "slug": course.slug,
        "description": course.description, "thumbnail_url": course.thumbnail_url,
        "instructor_name": course.instructor_name, "level": course.level,
        "duration_minutes": course.duration_minutes, "price": course.price,
        "status": course.status, "created_at": course.created_at,
    }


def _profile_dict(profile: Profile) -> dict:
    return {
        "id": profile.id, "email": profile.email, "full_name": profile.full_name,
        "role": profile.role, "is_active": profile.is_active,
        "created_at": profile.created_at,
    }


def _module_dict(module: Module) -> dict:
    return {
        "id": module.id, "course_id": module.course_id, "title": module.title,
        "description": module.description, "position": module.position, "status": module.status,
    }


def _topic_dict(topic: Topic, progress: TopicProgress | None = None) -> dict:
    return {
        "id": topic.id, "module_id": topic.module_id, "title": topic.title,
        "description": topic.description, "position": topic.position,
        "duration_minutes": topic.duration_minutes, "status": topic.status,
        "video_provider": topic.video_provider, "video_ref": topic.video_ref,
        "is_complete": bool(progress and progress.is_complete),
        "doubts_enabled": topic.doubts_enabled,
    }


def _admin_topic_dict(topic: Topic) -> dict:
    return {
        **_topic_dict(topic),
        "attempt_limit": topic.attempt_limit,
        "passing_percentage": topic.passing_percentage,
        "results_visible": topic.results_visible,
        "answers_visible": topic.answers_visible,
        "explanations_visible": topic.explanations_visible,
    }


def _public_topic_dict(topic: Topic) -> dict:
    return {
        "id": topic.id, "title": topic.title, "description": topic.description,
        "position": topic.position, "duration_minutes": topic.duration_minutes,
    }


def _resource_dict(resource: TopicResource) -> dict:
    return {
        "id": resource.id, "topic_id": resource.topic_id, "title": resource.title,
        "description": resource.description, "resource_type": resource.resource_type,
        "external_url": resource.external_url, "position": resource.position,
        "is_published": resource.is_published,
    }


def _doubt_dict(db: Session, doubt: Doubt) -> dict:
    topic = db.get(Topic, doubt.topic_id)
    student = db.get(Profile, doubt.student_id)
    replies = db.scalars(
        select(DoubtReply).where(DoubtReply.doubt_id == doubt.id).order_by(DoubtReply.created_at)
    ).all()
    return {
        "id": doubt.id, "topic_id": doubt.topic_id,
        "topic_title": topic.title if topic else "", "student_id": doubt.student_id,
        "student_name": student.full_name if student else "",
        "message": doubt.message, "status": doubt.status, "created_at": doubt.created_at,
        "updated_at": doubt.updated_at,
        "replies": [{
            "id": reply.id, "author_id": reply.author_id,
            "author_name": (db.get(Profile, reply.author_id) or Profile(
                id="", email="", full_name="Shahil Academy"
            )).full_name,
            "message": reply.message, "created_at": reply.created_at,
        } for reply in replies],
    }


def _audit(db: Session, actor: Profile, action: str, resource_type: str, resource_id: str) -> None:
    db.add(AuditLog(
        actor_id=actor.id, action=action, resource_type=resource_type, resource_id=resource_id
    ))


def _course_for_topic(db: Session, topic_id: str) -> tuple[Topic, Module, Course]:
    topic = db.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    module = db.get(Module, topic.module_id)
    course = db.get(Course, module.course_id) if module else None
    if module is None or course is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic, module, course


def _ensure_enrollment(db: Session, profile: Profile, course: Course) -> None:
    enrollment = db.scalar(select(Enrollment).where(
        Enrollment.student_id == profile.id,
        Enrollment.course_id == course.id,
        Enrollment.status == "active",
    ))
    now = datetime.now(timezone.utc)
    expiry = enrollment.expires_at if enrollment else None
    if expiry is not None and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if enrollment is None or (expiry and expiry <= now):
        raise HTTPException(status_code=403, detail="An active course enrollment is required")
    if course.status != "published" or course.archived_at is not None:
        raise HTTPException(status_code=404, detail="Course not found")


def _youtube_ref(url: str | None) -> tuple[str | None, str | None]:
    if url is None or not url.strip():
        return None, None
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    video_ref = None
    if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            video_ref = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith("/embed/"):
            video_ref = parsed.path.split("/embed/", 1)[1]
    elif host in {"youtu.be", "www.youtu.be"}:
        video_ref = parsed.path.strip("/").split("/", 1)[0]
    if parsed.scheme != "https" or not video_ref or len(video_ref) != 11:
        raise HTTPException(status_code=422, detail="Provide a valid YouTube watch, share, or embed URL")
    if not all(char.isalnum() or char in "_-" for char in video_ref):
        raise HTTPException(status_code=422, detail="Invalid YouTube video reference")
    return "youtube", video_ref


@router.get("/auth/me")
def read_me(user: Profile = Depends(get_current_user)):
    return _profile_dict(user)


@router.post("/auth/register", status_code=201)
def register(payload: RegisterInput, db: Session = Depends(get_db)):
    _ensure_jwt_configured()
    email = str(payload.email).strip().lower()
    full_name = payload.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=422, detail="Full name cannot be blank")
    if db.scalar(select(Profile).where(func.lower(Profile.email) == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    profile = Profile(
        id=str(uuid.uuid4()),
        email=email,
        full_name=full_name,
        password_hash=_password_hash(payload.password),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _auth_response(profile)


@router.post("/auth/login")
def login(payload: CredentialsInput, db: Session = Depends(get_db)):
    _ensure_jwt_configured()
    email = str(payload.email).strip().lower()
    profile = db.scalar(select(Profile).where(func.lower(Profile.email) == email))
    if profile is None or not _verify_password(payload.password, profile.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not profile.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    return _auth_response(profile)


@router.patch("/auth/me")
def update_me(payload: ProfileUpdate, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()
    db.commit()
    db.refresh(user)
    return _profile_dict(user)


@router.get("/courses")
def public_courses(
    q: str | None = None, limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0), db: Session = Depends(get_db),
):
    query = select(Course).where(Course.status == "published", Course.is_public.is_(True), Course.archived_at.is_(None))
    if q:
        query = query.where(Course.title.ilike(f"%{q.strip()}%"))
    courses = db.scalars(query.order_by(Course.created_at.desc()).offset(offset).limit(limit)).all()
    return [_course_dict(course) for course in courses]


@router.get("/courses/{course_id}")
def public_course(course_id: str, db: Session = Depends(get_db)):
    course = db.scalar(select(Course).where(
        (Course.id == course_id) | (Course.slug == course_id),
        Course.status == "published",
        Course.is_public.is_(True),
        Course.archived_at.is_(None),
    ))
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    result = _course_dict(course)
    modules = db.scalars(select(Module).where(
        Module.course_id == course.id, Module.status == "published"
    ).order_by(Module.position)).all()
    result["modules"] = [{
        **_module_dict(module),
        "topics": [_public_topic_dict(topic) for topic in db.scalars(select(Topic).where(
            Topic.module_id == module.id, Topic.status == "published"
        ).order_by(Topic.position)).all()],
    } for module in modules]
    return result


@router.get("/student/dashboard")
def student_dashboard(db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    enrollments = db.scalars(select(Enrollment).where(
        Enrollment.student_id == user.id, Enrollment.status == "active",
        (Enrollment.expires_at.is_(None)) | (Enrollment.expires_at > now),
    )).all()
    enrolled_ids = {entry.course_id for entry in enrollments}
    courses = db.scalars(select(Course).where(
        Course.id.in_(enrolled_ids) if enrolled_ids else False,
        Course.status == "published", Course.archived_at.is_(None),
    )).all()
    course_items = []
    for course in courses:
        topics = db.scalars(select(Topic).join(Module).where(
            Module.course_id == course.id, Module.status == "published", Topic.status == "published"
        )).all()
        topic_ids = [topic.id for topic in topics]
        completed = db.scalar(select(func.count(TopicProgress.id)).where(
            TopicProgress.student_id == user.id, TopicProgress.topic_id.in_(topic_ids),
            TopicProgress.is_complete.is_(True),
        )) if topic_ids else 0
        course_items.append({**_course_dict(course), "topic_count": len(topic_ids),
                             "completed_topics": completed or 0,
                             "progress_percent": round((completed or 0) * 100 / len(topic_ids)) if topic_ids else 0})
    doubts = db.scalars(select(Doubt).where(Doubt.student_id == user.id).order_by(Doubt.updated_at.desc()).limit(5)).all()
    announcements = db.scalars(select(Announcement).where(
        Announcement.status == "published",
        (Announcement.course_id.is_(None)) | (Announcement.course_id.in_(enrolled_ids) if enrolled_ids else False),
    ).order_by(Announcement.published_at.desc()).limit(5)).all()
    recent = db.scalars(select(TopicProgress).where(
        TopicProgress.student_id == user.id
    ).order_by(TopicProgress.last_visited_at.desc()).limit(5)).all()
    return {
        "profile": _profile_dict(user), "courses": course_items,
        "open_doubts": sum(doubt.status == "open" for doubt in doubts),
        "doubts": [_doubt_dict(db, doubt) for doubt in doubts],
        "announcements": [{
            "id": announcement.id, "title": announcement.title, "message": announcement.message,
            "published_at": announcement.published_at,
        } for announcement in announcements],
        "recent_topics": [{
            **_topic_dict(db.get(Topic, progress.topic_id), progress),
            "last_visited_at": progress.last_visited_at,
        } for progress in recent if db.get(Topic, progress.topic_id) is not None],
    }


@router.get("/student/courses")
def student_courses(db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    ids = db.scalars(select(Enrollment.course_id).where(
        Enrollment.student_id == user.id, Enrollment.status == "active",
        (Enrollment.expires_at.is_(None)) | (Enrollment.expires_at > now),
    )).all()
    courses = db.scalars(select(Course).where(
        Course.id.in_(ids) if ids else False, Course.status == "published", Course.archived_at.is_(None)
    )).all()
    result = []
    for course in courses:
        topics = db.scalars(select(Topic).join(Module).where(
            Module.course_id == course.id, Module.status == "published", Topic.status == "published"
        )).all()
        topic_ids = [topic.id for topic in topics]
        completed = db.scalar(select(func.count(TopicProgress.id)).where(
            TopicProgress.student_id == user.id, TopicProgress.topic_id.in_(topic_ids),
            TopicProgress.is_complete.is_(True),
        )) if topic_ids else 0
        result.append({**_course_dict(course), "topic_count": len(topic_ids),
                       "completed_topics": completed or 0,
                       "progress_percent": round((completed or 0) * 100 / len(topic_ids)) if topic_ids else 0})
    return result


@router.get("/student/courses/{course_id}")
def student_course(course_id: str, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    _ensure_enrollment(db, user, course)
    modules = db.scalars(select(Module).where(
        Module.course_id == course.id, Module.status == "published"
    ).order_by(Module.position)).all()
    return {
        **_course_dict(course),
        "modules": [{
            **_module_dict(module),
            "topics": [_topic_dict(
                topic, db.scalar(select(TopicProgress).where(
                    TopicProgress.student_id == user.id, TopicProgress.topic_id == topic.id
                ))
            ) for topic in db.scalars(select(Topic).where(
                Topic.module_id == module.id, Topic.status == "published"
            ).order_by(Topic.position)).all()],
        } for module in modules],
    }


@router.get("/student/topics/{topic_id}")
def student_topic(topic_id: str, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    topic, module, course = _course_for_topic(db, topic_id)
    _ensure_enrollment(db, user, course)
    if topic.status != "published" or module.status != "published":
        raise HTTPException(status_code=404, detail="Topic not found")
    progress = db.scalar(select(TopicProgress).where(
        TopicProgress.student_id == user.id, TopicProgress.topic_id == topic.id
    ))
    now = datetime.now(timezone.utc)
    if progress is None:
        progress = TopicProgress(student_id=user.id, topic_id=topic.id, last_visited_at=now)
        db.add(progress)
    else:
        progress.last_visited_at = now
    db.commit()
    return {
        **_topic_dict(topic, progress), "course": _course_dict(course),
        "module": _module_dict(module),
        "resources": [_resource_dict(resource) for resource in db.scalars(select(TopicResource).where(
            TopicResource.topic_id == topic.id, TopicResource.is_published.is_(True)
        ).order_by(TopicResource.position)).all()],
    }


@router.get("/student/topics/{topic_id}/resources")
def student_topic_resources(topic_id: str, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    topic, module, course = _course_for_topic(db, topic_id)
    _ensure_enrollment(db, user, course)
    if topic.status != "published" or module.status != "published":
        raise HTTPException(status_code=404, detail="Topic not found")
    return [_resource_dict(resource) for resource in db.scalars(select(TopicResource).where(
        TopicResource.topic_id == topic.id, TopicResource.is_published.is_(True)
    ).order_by(TopicResource.position)).all()]


@router.post("/student/topics/{topic_id}/complete")
def complete_topic(topic_id: str, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    topic, module, course = _course_for_topic(db, topic_id)
    _ensure_enrollment(db, user, course)
    if topic.status != "published" or module.status != "published":
        raise HTTPException(status_code=404, detail="Topic not found")
    progress = db.scalar(select(TopicProgress).where(
        TopicProgress.student_id == user.id, TopicProgress.topic_id == topic.id
    ))
    now = datetime.now(timezone.utc)
    if progress is None:
        progress = TopicProgress(student_id=user.id, topic_id=topic.id)
        db.add(progress)
    progress.is_complete = True
    progress.completed_at = now
    progress.last_visited_at = now
    db.commit()
    return {"topic_id": topic.id, "is_complete": True, "completed_at": now}


@router.get("/student/topics/{topic_id}/questions")
def student_questions(topic_id: str, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    topic, module, course = _course_for_topic(db, topic_id)
    _ensure_enrollment(db, user, course)
    if topic.status != "published" or module.status != "published":
        raise HTTPException(status_code=404, detail="Topic not found")
    attempts = db.scalar(select(func.count(QuizAttempt.id)).where(
        QuizAttempt.student_id == user.id, QuizAttempt.topic_id == topic.id
    )) or 0
    if topic.attempt_limit is not None and attempts >= topic.attempt_limit:
        raise HTTPException(status_code=403, detail="Quiz attempt limit reached")
    questions = db.scalars(select(Question).where(
        Question.topic_id == topic.id, Question.is_published.is_(True)
    ).order_by(Question.position)).all()
    return [{
        "id": question.id, "prompt": question.prompt, "question_type": question.question_type,
        "options": json.loads(question.options), "marks": question.marks,
    } for question in questions]


@router.post("/student/topics/{topic_id}/attempts")
def submit_quiz(topic_id: str, payload: QuizSubmission, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    topic, module, course = _course_for_topic(db, topic_id)
    _ensure_enrollment(db, user, course)
    if topic.status != "published" or module.status != "published":
        raise HTTPException(status_code=404, detail="Topic not found")
    prior_attempts = db.scalar(select(func.count(QuizAttempt.id)).where(
        QuizAttempt.student_id == user.id, QuizAttempt.topic_id == topic.id
    )) or 0
    if topic.attempt_limit is not None and prior_attempts >= topic.attempt_limit:
        raise HTTPException(status_code=403, detail="Quiz attempt limit reached")
    questions = db.scalars(select(Question).where(
        Question.topic_id == topic.id, Question.is_published.is_(True)
    )).all()
    question_by_id = {question.id: question for question in questions}
    if not questions or not payload.answers or not set(payload.answers).issubset(question_by_id):
        raise HTTPException(status_code=422, detail="Answers must reference published questions for this topic")
    attempt = QuizAttempt(student_id=user.id, topic_id=topic.id)
    db.add(attempt)
    db.flush()
    score = 0.0
    max_score = sum(question.marks for question in questions)
    for question_id, submitted_answer in payload.answers.items():
        question = question_by_id[question_id]
        is_correct = submitted_answer.strip().casefold() == question.correct_answer.strip().casefold()
        awarded = question.marks if is_correct else 0.0
        score += awarded
        db.add(QuizAnswer(
            attempt_id=attempt.id, question_id=question.id, answer=submitted_answer,
            is_correct=is_correct, awarded_marks=awarded,
        ))
    attempt.score = score
    attempt.max_score = max_score
    db.commit()
    result = {"id": attempt.id, "score": score, "max_score": max_score,
              "percentage": round(score * 100 / max_score, 2) if max_score else 0,
              "passed": bool(max_score and score * 100 / max_score >= topic.passing_percentage)}
    if not topic.results_visible:
        return {"id": attempt.id, "submitted": True}
    result["answers"] = [{
            "question_id": answer.question_id, "is_correct": answer.is_correct,
            "awarded_marks": answer.awarded_marks,
            **({"correct_answer": question_by_id[answer.question_id].correct_answer}
               if topic.answers_visible else {}),
            **({"explanation": question_by_id[answer.question_id].explanation}
               if topic.explanations_visible else {}),
        } for answer in db.scalars(select(QuizAnswer).where(QuizAnswer.attempt_id == attempt.id)).all()]
    return result


@router.get("/student/attempts")
def own_attempts(db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    attempts = db.scalars(select(QuizAttempt).where(
        QuizAttempt.student_id == user.id
    ).order_by(QuizAttempt.submitted_at.desc())).all()
    return [{
        "id": attempt.id, "topic_id": attempt.topic_id, "score": attempt.score,
        "max_score": attempt.max_score, "submitted_at": attempt.submitted_at,
    } for attempt in attempts]


@router.get("/student/doubts")
def own_doubts(db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    doubts = db.scalars(select(Doubt).where(
        Doubt.student_id == user.id
    ).order_by(Doubt.updated_at.desc())).all()
    return [_doubt_dict(db, doubt) for doubt in doubts]


@router.post("/student/doubts", status_code=201)
def create_doubt(payload: DoubtInput, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    topic, module, course = _course_for_topic(db, payload.topic_id)
    _ensure_enrollment(db, user, course)
    if topic.status != "published" or module.status != "published" or not topic.doubts_enabled:
        raise HTTPException(status_code=403, detail="Doubts are not enabled for this topic")
    doubt = Doubt(student_id=user.id, topic_id=topic.id, message=payload.message.strip())
    db.add(doubt)
    db.commit()
    db.refresh(doubt)
    return _doubt_dict(db, doubt)


@router.get("/student/bookmarks")
def own_bookmarks(db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    entries = db.scalars(select(Bookmark).where(Bookmark.student_id == user.id)).all()
    visible = []
    for entry in entries:
        topic = db.get(Topic, entry.topic_id)
        if topic is None or topic.status != "published":
            continue
        _, module, course = _course_for_topic(db, topic.id)
        try:
            _ensure_enrollment(db, user, course)
        except HTTPException as error:
            if error.status_code == 403:
                continue
            raise
        if module.status == "published":
            visible.append(_topic_dict(topic))
    return visible


@router.post("/student/bookmarks/{topic_id}", status_code=201)
def add_bookmark(topic_id: str, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    topic, module, course = _course_for_topic(db, topic_id)
    _ensure_enrollment(db, user, course)
    if topic.status != "published" or module.status != "published":
        raise HTTPException(status_code=404, detail="Topic not found")
    if db.scalar(select(Bookmark).where(Bookmark.student_id == user.id, Bookmark.topic_id == topic.id)) is None:
        db.add(Bookmark(student_id=user.id, topic_id=topic.id))
        db.commit()
    return {"topic_id": topic.id, "bookmarked": True}


@router.delete("/student/bookmarks/{topic_id}", status_code=204)
def remove_bookmark(topic_id: str, db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    bookmark = db.scalar(select(Bookmark).where(
        Bookmark.student_id == user.id, Bookmark.topic_id == topic_id
    ))
    if bookmark:
        db.delete(bookmark)
        db.commit()


@router.get("/student/announcements")
def student_announcements(db: Session = Depends(get_db), user: Profile = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    course_ids = db.scalars(select(Enrollment.course_id).where(
        Enrollment.student_id == user.id, Enrollment.status == "active",
        (Enrollment.expires_at.is_(None)) | (Enrollment.expires_at > now),
    )).all()
    entries = db.scalars(select(Announcement).where(
        Announcement.status == "published",
        (Announcement.course_id.is_(None)) | (Announcement.course_id.in_(course_ids) if course_ids else False),
    ).order_by(Announcement.published_at.desc())).all()
    return [{"id": entry.id, "title": entry.title, "message": entry.message,
             "course_id": entry.course_id, "published_at": entry.published_at} for entry in entries]


@router.get("/admin/dashboard")
def admin_dashboard(db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    return {
        "students": db.scalar(select(func.count(Profile.id)).where(Profile.role == "student")) or 0,
        "published_courses": db.scalar(select(func.count(Course.id)).where(Course.status == "published")) or 0,
        "enrollments": db.scalar(select(func.count(Enrollment.id)).where(Enrollment.status == "active")) or 0,
        "modules": db.scalar(select(func.count(Module.id))) or 0,
        "topics": db.scalar(select(func.count(Topic.id))) or 0,
        "pending_doubts": db.scalar(select(func.count(Doubt.id)).where(Doubt.status == "open")) or 0,
    }


@router.get("/admin/reports")
def admin_reports(db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    courses = db.scalars(select(Course).where(Course.archived_at.is_(None))).all()
    reports = []
    for course in courses:
        topic_ids = db.scalars(select(Topic.id).join(Module).where(
            Module.course_id == course.id, Module.status == "published", Topic.status == "published"
        )).all()
        enrollments = db.scalar(select(func.count(Enrollment.id)).where(
            Enrollment.course_id == course.id, Enrollment.status == "active",
            (Enrollment.expires_at.is_(None)) | (Enrollment.expires_at > now),
        )) or 0
        completed = db.scalar(select(func.count(TopicProgress.id)).join(
            Enrollment, Enrollment.student_id == TopicProgress.student_id
        ).where(
            Enrollment.course_id == course.id, Enrollment.status == "active",
            (Enrollment.expires_at.is_(None)) | (Enrollment.expires_at > now),
            TopicProgress.topic_id.in_(topic_ids) if topic_ids else False,
            TopicProgress.is_complete.is_(True),
        )) or 0
        possible = enrollments * len(topic_ids)
        reports.append({
            "course_id": course.id,
            "course_title": course.title,
            "topic_count": len(topic_ids),
            "active_enrollments": enrollments,
            "completion_percent": round(completed * 100 / possible, 1) if possible else 0,
        })
    return reports


@router.get("/admin/courses")
def admin_courses(db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    return [_course_dict(item) for item in db.scalars(select(Course).order_by(Course.created_at.desc())).all()]


@router.post("/admin/courses", status_code=201)
def create_course(payload: CourseInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    if db.scalar(select(Course).where(Course.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="Course slug already exists")
    next_id = db.execute(
        update(CourseIdSequence)
        .where(CourseIdSequence.id == 1)
        .values(next_value=CourseIdSequence.next_value + 1)
        .returning(CourseIdSequence.next_value)
    ).scalar_one()
    values = payload.model_dump()
    values["thumbnail_url"] = str(values["thumbnail_url"]) if values["thumbnail_url"] else None
    if values["status"] == "published":
        values["published_at"] = datetime.now(timezone.utc)
    course = Course(id=f"c{next_id}", **values)
    db.add(course)
    db.flush()
    _audit(db, admin, "course.created", "course", course.id)
    db.commit()
    db.refresh(course)
    return _course_dict(course)


@router.patch("/admin/courses/{course_id}")
def update_course(course_id: str, payload: CourseInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    duplicate = db.scalar(select(Course).where(Course.slug == payload.slug, Course.id != course_id))
    if duplicate:
        raise HTTPException(status_code=409, detail="Course slug already exists")
    values = payload.model_dump()
    values["thumbnail_url"] = str(values["thumbnail_url"]) if values["thumbnail_url"] else None
    for key, value in values.items():
        setattr(course, key, value)
    if course.status == "published" and course.published_at is None:
        course.published_at = datetime.now(timezone.utc)
    if course.status == "archived":
        course.archived_at = datetime.now(timezone.utc)
    elif course.status == "published":
        course.archived_at = None
    _audit(db, admin, "course.updated", "course", course.id)
    db.commit()
    db.refresh(course)
    return _course_dict(course)


@router.get("/admin/modules")
def admin_modules(course_id: str | None = None, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    query = select(Module)
    if course_id:
        query = query.where(Module.course_id == course_id)
    return [_module_dict(item) for item in db.scalars(query.order_by(Module.course_id, Module.position)).all()]


@router.post("/admin/modules", status_code=201)
def create_module(payload: ModuleInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    if db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=404, detail="Course not found")
    module = Module(**payload.model_dump())
    db.add(module)
    db.flush()
    _audit(db, admin, "module.created", "module", module.id)
    db.commit()
    db.refresh(module)
    return _module_dict(module)


@router.patch("/admin/modules/{module_id}")
def update_module(module_id: str, payload: ModuleInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    module = db.get(Module, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")
    if db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in payload.model_dump().items():
        setattr(module, key, value)
    _audit(db, admin, "module.updated", "module", module.id)
    db.commit()
    db.refresh(module)
    return _module_dict(module)


@router.get("/admin/topics")
def admin_topics(module_id: str | None = None, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    query = select(Topic)
    if module_id:
        query = query.where(Topic.module_id == module_id)
    return [_admin_topic_dict(item) for item in db.scalars(query.order_by(Topic.module_id, Topic.position)).all()]


@router.post("/admin/topics", status_code=201)
def create_topic(payload: TopicInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    if db.get(Module, payload.module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found")
    provider, video_ref = _youtube_ref(payload.video_url)
    values = payload.model_dump(exclude={"video_url"})
    topic = Topic(**values, video_provider=provider, video_ref=video_ref)
    db.add(topic)
    db.flush()
    _audit(db, admin, "topic.created", "topic", topic.id)
    db.commit()
    db.refresh(topic)
    return _topic_dict(topic)


@router.patch("/admin/topics/{topic_id}")
def update_topic(topic_id: str, payload: TopicInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    topic = db.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    if db.get(Module, payload.module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found")
    provider, video_ref = _youtube_ref(payload.video_url)
    for key, value in payload.model_dump(exclude={"video_url"}).items():
        setattr(topic, key, value)
    topic.video_provider = provider
    topic.video_ref = video_ref
    _audit(db, admin, "topic.updated", "topic", topic.id)
    db.commit()
    db.refresh(topic)
    return _topic_dict(topic)


@router.post("/admin/resources", status_code=201)
def create_resource(payload: ResourceInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    if db.get(Topic, payload.topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    resource = TopicResource(**{
        **payload.model_dump(exclude={"external_url"}),
        "external_url": str(payload.external_url),
    })
    db.add(resource)
    db.flush()
    _audit(db, admin, "resource.created", "topic_resource", resource.id)
    db.commit()
    db.refresh(resource)
    return _resource_dict(resource)


@router.patch("/admin/resources/{resource_id}")
def update_resource(resource_id: str, payload: ResourceInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    resource = db.get(TopicResource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    if db.get(Topic, payload.topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    for key, value in payload.model_dump(exclude={"external_url"}).items():
        setattr(resource, key, value)
    resource.external_url = str(payload.external_url)
    _audit(db, admin, "resource.updated", "topic_resource", resource.id)
    db.commit()
    db.refresh(resource)
    return _resource_dict(resource)


@router.get("/admin/resources")
def admin_resources(db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    return [_resource_dict(item) for item in db.scalars(select(TopicResource).order_by(TopicResource.created_at.desc())).all()]


@router.post("/admin/questions", status_code=201)
def create_question(payload: QuestionInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    if db.get(Topic, payload.topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    question = Question(**{
        **payload.model_dump(exclude={"options"}),
        "options": json.dumps(payload.options),
    })
    db.add(question)
    db.flush()
    _audit(db, admin, "question.created", "question", question.id)
    db.commit()
    db.refresh(question)
    return {"id": question.id, "topic_id": question.topic_id, "prompt": question.prompt}


@router.patch("/admin/questions/{question_id}")
def update_question(question_id: str, payload: QuestionInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    if db.get(Topic, payload.topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    for key, value in payload.model_dump(exclude={"options"}).items():
        setattr(question, key, value)
    question.options = json.dumps(payload.options)
    _audit(db, admin, "question.updated", "question", question.id)
    db.commit()
    return {"id": question.id, "topic_id": question.topic_id, "prompt": question.prompt}


@router.get("/admin/questions")
def admin_questions(db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    questions = db.scalars(select(Question).order_by(Question.topic_id, Question.position)).all()
    return [{
        "id": q.id, "topic_id": q.topic_id, "prompt": q.prompt,
        "question_type": q.question_type, "options": json.loads(q.options),
        "correct_answer": q.correct_answer, "explanation": q.explanation,
        "marks": q.marks, "position": q.position, "is_published": q.is_published,
    } for q in questions]


@router.get("/admin/students")
def admin_students(q: str | None = None, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    query = select(Profile).where(Profile.role == "student")
    if q:
        like = f"%{q.strip()}%"
        query = query.where((Profile.email.ilike(like)) | (Profile.full_name.ilike(like)))
    return [_profile_dict(item) for item in db.scalars(query.order_by(Profile.created_at.desc()).limit(200)).all()]


@router.patch("/admin/students/{student_id}/status")
def update_student_status(student_id: str, is_active: bool, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    student = db.get(Profile, student_id)
    if student is None or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")
    student.is_active = is_active
    _audit(db, admin, "student.status_changed", "profile", student.id)
    db.commit()
    return _profile_dict(student)


@router.get("/admin/enrollments")
def admin_enrollments(db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    rows = db.scalars(select(Enrollment).order_by(Enrollment.created_at.desc()).limit(500)).all()
    return [{
        "id": row.id, "student_id": row.student_id, "student_email": (db.get(Profile, row.student_id) or Profile(
            id="", email="", full_name=""
        )).email,
        "course_id": row.course_id, "course_title": (db.get(Course, row.course_id) or Course(
            id="", title="", slug="", description="", instructor_name="", level=""
        )).title,
        "status": row.status, "expires_at": row.expires_at, "created_at": row.created_at,
    } for row in rows]


@router.post("/admin/enrollments", status_code=201)
def create_enrollment(payload: EnrollmentInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    student = db.get(Profile, payload.student_id)
    if student is None or student.role != "student" or db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=404, detail="Student or course not found")
    enrollment = db.scalar(select(Enrollment).where(
        Enrollment.student_id == payload.student_id, Enrollment.course_id == payload.course_id
    ))
    if enrollment:
        enrollment.status = payload.status
        enrollment.expires_at = payload.expires_at
    else:
        enrollment = Enrollment(**payload.model_dump())
        db.add(enrollment)
    db.flush()
    _audit(db, admin, "enrollment.granted", "enrollment", enrollment.id)
    db.commit()
    db.refresh(enrollment)
    return {"id": enrollment.id, "student_id": enrollment.student_id, "course_id": enrollment.course_id,
            "status": enrollment.status, "expires_at": enrollment.expires_at}


@router.patch("/admin/enrollments/{enrollment_id}")
def update_enrollment(enrollment_id: str, status: str = Query(pattern="^(active|revoked|expired)$"),
                      db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    enrollment.status = status
    _audit(db, admin, "enrollment.status_changed", "enrollment", enrollment.id)
    db.commit()
    return {"id": enrollment.id, "status": enrollment.status}


@router.get("/admin/doubts")
def admin_doubts(status: str | None = None, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    query = select(Doubt)
    if status in {"open", "answered", "resolved"}:
        query = query.where(Doubt.status == status)
    return [_doubt_dict(db, doubt) for doubt in db.scalars(query.order_by(Doubt.created_at.desc())).all()]


@router.post("/admin/doubts/{doubt_id}/replies", status_code=201)
def reply_to_doubt(doubt_id: str, payload: ReplyInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    doubt = db.get(Doubt, doubt_id)
    if doubt is None:
        raise HTTPException(status_code=404, detail="Doubt not found")
    reply = DoubtReply(doubt_id=doubt.id, author_id=admin.id, message=payload.message.strip())
    doubt.status = "answered"
    db.add(reply)
    _audit(db, admin, "doubt.replied", "doubt", doubt.id)
    db.commit()
    return _doubt_dict(db, doubt)


@router.patch("/admin/doubts/{doubt_id}/status")
def change_doubt_status(doubt_id: str, status: str = Query(pattern="^(open|answered|resolved)$"),
                        db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    doubt = db.get(Doubt, doubt_id)
    if doubt is None:
        raise HTTPException(status_code=404, detail="Doubt not found")
    doubt.status = status
    _audit(db, admin, "doubt.status_changed", "doubt", doubt.id)
    db.commit()
    return _doubt_dict(db, doubt)


@router.get("/admin/announcements")
def admin_announcements(db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    entries = db.scalars(select(Announcement).order_by(Announcement.created_at.desc())).all()
    return [{
        "id": entry.id, "title": entry.title, "message": entry.message,
        "course_id": entry.course_id, "status": entry.status, "published_at": entry.published_at,
    } for entry in entries]


@router.post("/admin/announcements", status_code=201)
def create_announcement(payload: AnnouncementInput, db: Session = Depends(get_db), admin: Profile = Depends(require_admin)):
    if payload.course_id and db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=404, detail="Course not found")
    entry = Announcement(**payload.model_dump(), author_id=admin.id)
    if entry.status == "published":
        entry.published_at = datetime.now(timezone.utc)
    db.add(entry)
    db.flush()
    _audit(db, admin, "announcement.created", "announcement", entry.id)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "title": entry.title, "status": entry.status, "published_at": entry.published_at}


@router.patch("/admin/announcements/{announcement_id}")
def update_announcement(
    announcement_id: str,
    payload: AnnouncementInput,
    db: Session = Depends(get_db),
    admin: Profile = Depends(require_admin),
):
    entry = db.get(Announcement, announcement_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    if payload.course_id and db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in payload.model_dump().items():
        setattr(entry, key, value)
    if entry.status == "published" and entry.published_at is None:
        entry.published_at = datetime.now(timezone.utc)
    if entry.status != "published":
        entry.published_at = None
    _audit(db, admin, "announcement.updated", "announcement", entry.id)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "title": entry.title, "status": entry.status, "published_at": entry.published_at}

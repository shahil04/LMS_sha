from fastapi.testclient import TestClient
from fastapi import Depends
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Course, CourseIdSequence, Enrollment, Module, Profile, Question, Topic, TopicResource

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base.metadata.create_all(engine)

student = Profile(id="student-1", email="student@example.test", full_name="Student")
admin = Profile(id="admin-1", email="admin@example.test", full_name="Admin", role="admin")
course = Course(
    id="course-1", title="Published Course", slug="published-course",
    description="Course description", instructor_name="Instructor",
    level="Beginner", status="published", is_public=True,
)
module = Module(id="module-1", course_id="course-1", title="Module", status="published")
topic = Topic(
    id="topic-1", module_id="module-1", title="Lesson", status="published",
    video_provider="youtube", video_ref="abcdefghijk",
)
question = Question(
    id="question-1", topic_id="topic-1", prompt="2 + 2?",
    options='["3", "4"]', correct_answer="4", marks=2,
)
published_resource = TopicResource(
    id="resource-1", topic_id="topic-1", title="Lesson notes",
    external_url="https://example.test/notes.pdf", is_published=True,
)
draft_resource = TopicResource(
    id="resource-2", topic_id="topic-1", title="Draft notes",
    external_url="https://example.test/draft.pdf", is_published=False,
)


def override_db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def authenticated_student(db: Session = Depends(get_db)) -> Profile:
    return db.get(Profile, student.id)


def setup_module():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestingSession() as session:
        session.add_all([
            student, admin, course, module, topic, question, published_resource, draft_resource,
            CourseIdSequence(id=1, next_value=0),
        ])
        session.commit()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def test_public_catalog_hides_draft_courses():
    with TestingSession() as session:
        session.add(Course(
            id="draft-course", title="Draft", slug="draft", description="",
            instructor_name="Instructor", level="Beginner", status="draft",
        ))
        session.commit()
    response = client.get("/api/v1/courses")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["course-1"]


def test_public_course_outline_does_not_expose_video_reference():
    response = client.get("/api/v1/courses/published-course")
    assert response.status_code == 200
    public_topic = response.json()["modules"][0]["topics"][0]
    assert "video_ref" not in public_topic
    assert "video_provider" not in public_topic


def test_admin_course_creation_assigns_sequential_ids():
    app.dependency_overrides[get_current_user] = lambda: admin
    first = client.post("/api/v1/admin/courses", json={
        "title": "Python One", "slug": "python-one", "status": "draft",
    })
    second = client.post("/api/v1/admin/courses", json={
        "title": "Python Two", "slug": "python-two", "status": "draft",
    })
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == "c1"
    assert second.json()["id"] == "c2"
    app.dependency_overrides.pop(get_current_user, None)


def test_student_cannot_use_admin_endpoint():
    app.dependency_overrides[get_current_user] = lambda: student
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 403
    app.dependency_overrides.pop(get_current_user, None)


def test_admin_report_uses_course_and_completion_data():
    app.dependency_overrides[get_current_user] = lambda: admin
    response = client.get("/api/v1/admin/reports")
    assert response.status_code == 200
    report = next(item for item in response.json() if item["course_id"] == course.id)
    assert report["topic_count"] == 1
    assert "completion_percent" in report
    app.dependency_overrides.pop(get_current_user, None)


def test_profile_update_cannot_escalate_role():
    app.dependency_overrides[get_current_user] = authenticated_student
    response = client.patch(
        "/api/v1/auth/me",
        json={"full_name": "Updated Student", "role": "admin"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "student"
    app.dependency_overrides.pop(get_current_user, None)


def test_enrollment_is_required_to_open_lesson():
    app.dependency_overrides[get_current_user] = lambda: student
    response = client.get("/api/v1/student/topics/topic-1")
    assert response.status_code == 403
    with TestingSession() as session:
        session.add(Enrollment(student_id=student.id, course_id=course.id, status="active"))
        session.commit()
    response = client.get("/api/v1/student/topics/topic-1")
    assert response.status_code == 200
    app.dependency_overrides.pop(get_current_user, None)


def test_resources_require_enrollment_and_hide_unpublished_records():
    app.dependency_overrides[get_current_user] = lambda: student
    with TestingSession() as session:
        enrollment = session.scalar(select(Enrollment).where(Enrollment.student_id == student.id))
        if enrollment:
            session.delete(enrollment)
            session.commit()
    denied = client.get("/api/v1/student/topics/topic-1/resources")
    assert denied.status_code == 403
    with TestingSession() as session:
        if session.scalar(select(Enrollment).where(Enrollment.student_id == student.id)) is None:
            session.add(Enrollment(student_id=student.id, course_id=course.id, status="active"))
            session.commit()
    response = client.get("/api/v1/student/topics/topic-1/resources")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["resource-1"]
    app.dependency_overrides.pop(get_current_user, None)


def test_quiz_grades_on_server_and_rejects_unrelated_question():
    app.dependency_overrides[get_current_user] = lambda: student
    with TestingSession() as session:
        if session.scalar(
            select(Enrollment).where(Enrollment.student_id == student.id)
        ) is None:
            session.add(Enrollment(student_id=student.id, course_id=course.id, status="active"))
            session.commit()
    question_response = client.get("/api/v1/student/topics/topic-1/questions")
    assert question_response.status_code == 200
    assert "correct_answer" not in question_response.json()[0]
    good = client.post(
        "/api/v1/student/topics/topic-1/attempts",
        json={"answers": {"question-1": "4"}},
    )
    assert good.status_code == 200
    assert good.json()["score"] == 2
    assert "correct_answer" not in good.json()["answers"][0]
    bad = client.post(
        "/api/v1/student/topics/topic-1/attempts",
        json={"answers": {"another-student-question": "4"}},
    )
    assert bad.status_code == 422
    app.dependency_overrides.pop(get_current_user, None)


def test_quiz_results_can_be_hidden_by_topic_policy():
    app.dependency_overrides[get_current_user] = lambda: student
    with TestingSession() as session:
        if session.scalar(select(Enrollment).where(Enrollment.student_id == student.id)) is None:
            session.add(Enrollment(student_id=student.id, course_id=course.id, status="active"))
        session.get(Topic, topic.id).results_visible = False
        session.commit()
    response = client.post(
        "/api/v1/student/topics/topic-1/attempts",
        json={"answers": {"question-1": "4"}},
    )
    assert response.status_code == 200
    assert response.json() == {"id": response.json()["id"], "submitted": True}
    app.dependency_overrides.pop(get_current_user, None)


def test_youtube_input_is_host_and_id_validated():
    from app.api.router import _youtube_ref
    from fastapi import HTTPException

    assert _youtube_ref("https://youtu.be/abcdefghijk") == ("youtube", "abcdefghijk")
    try:
        _youtube_ref("https://youtube.com.evil.test/watch?v=abcdefghijk")
    except HTTPException as error:
        assert error.status_code == 422
    else:
        raise AssertionError("Untrusted video host was accepted")


def test_registration_returns_token_without_email_verification(monkeypatch):
    import uuid

    monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-key-with-at-least-32-bytes")
    monkeypatch.setattr(settings, "jwt_algorithm", "HS256")
    email = f"{uuid.uuid4()}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "New Student", "email": email, "password": "password123"},
    )

    assert response.status_code == 201
    auth = response.json()
    assert auth["token_type"] == "bearer"
    assert auth["profile"]["email"] == email
    assert "password_hash" not in auth["profile"]
    current_user = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {auth['access_token']}"},
    )
    assert current_user.status_code == 200
    assert current_user.json()["email"] == email


def test_login_checks_password_and_duplicate_registration(monkeypatch):
    import uuid

    monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-key-with-at-least-32-bytes")
    monkeypatch.setattr(settings, "jwt_algorithm", "HS256")
    email = f"{uuid.uuid4()}@example.com"
    registration = client.post(
        "/api/v1/auth/register",
        json={"full_name": "New Student", "email": email, "password": "password123"},
    )
    assert registration.status_code == 201

    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "wrong-password"},
    )
    assert bad_login.status_code == 401
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200
    duplicate = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Another Student", "email": email, "password": "password123"},
    )
    assert duplicate.status_code == 409

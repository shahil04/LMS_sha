# API specification

The interactive OpenAPI contract is served at `/docs`; the versioned root is `/api/v1`.

| Area | Endpoints |
|---|---|
| Health | `GET /health` |
| Identity/profile | `GET /api/v1/auth/me`, `PATCH /api/v1/auth/me` |
| Public catalog | `GET /api/v1/courses?q=&limit=&offset=`, `GET /api/v1/courses/{course_id_or_slug}` |
| Student learning | `GET /api/v1/student/dashboard`, `GET /api/v1/student/courses`, `GET /api/v1/student/courses/{course_id}`, `GET /api/v1/student/topics/{topic_id}`, `POST /api/v1/student/topics/{topic_id}/complete`, `GET /api/v1/student/topics/{topic_id}/resources` |
| Student quizzes | `GET /api/v1/student/topics/{topic_id}/questions`, `POST /api/v1/student/topics/{topic_id}/attempts`, `GET /api/v1/student/attempts` |
| Student support | `GET/POST /api/v1/student/doubts`, `GET /api/v1/student/announcements`, `GET /api/v1/student/bookmarks`, `POST/DELETE /api/v1/student/bookmarks/{topic_id}` |
| Admin overview | `GET /api/v1/admin/dashboard`, `GET /api/v1/admin/reports` |
| Admin content | `GET/POST /api/v1/admin/courses`, `PATCH /api/v1/admin/courses/{id}`, `GET/POST /api/v1/admin/modules`, `PATCH /api/v1/admin/modules/{id}`, `GET/POST /api/v1/admin/topics`, `PATCH /api/v1/admin/topics/{id}`, `GET/POST /api/v1/admin/resources`, `PATCH /api/v1/admin/resources/{id}`, `GET/POST /api/v1/admin/questions`, `PATCH /api/v1/admin/questions/{id}` |
| Admin operations | `GET /api/v1/admin/students`, `PATCH /api/v1/admin/students/{id}/status`, `GET/POST /api/v1/admin/enrollments`, `PATCH /api/v1/admin/enrollments/{id}`, `GET /api/v1/admin/doubts`, `POST /api/v1/admin/doubts/{id}/replies`, `PATCH /api/v1/admin/doubts/{id}/status`, `GET/POST /api/v1/admin/announcements`, `PATCH /api/v1/admin/announcements/{id}` |

Protected API requests require `Authorization: Bearer <Supabase access token>`. Roles are looked up from `profiles`, not trusted from client data. Errors use standard HTTP status codes with safe FastAPI detail messages.

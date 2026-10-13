# Shahil Academy — Complete Full-Stack LMS Website Master Prompt

## Project objective

Act as a senior full-stack engineering team consisting of a UI/UX designer, React frontend engineer, FastAPI backend engineer, PostgreSQL database architect, authentication/security engineer, LMS product engineer, DevOps engineer, and QA automation engineer.

Build **Shahil Academy**, a complete, modern, responsive Learning Management System (LMS). This must be a working full-stack application, not merely a landing page, static mockup, or disconnected UI prototype.

The platform has two primary roles:

1. **Student** — accesses courses in which they are enrolled, studies topic by topic, watches lessons, accesses notes, answers practice questions and quizzes, tracks progress, and submits doubts.
2. **Admin** — manages courses, modules, topics, videos, study resources, questions, students, enrollments, doubts, announcements, and reports.

Build in small, verifiable phases. Inspect the existing repository before making changes. Do not overwrite existing work without understanding it.

---

## 1. Required technology stack

### Frontend
- React
- Vite
- TypeScript
- Tailwind CSS
- React Router
- TanStack Query for server state and caching
- Axios or a similarly well-structured typed API client
- React Hook Form
- Zod for client-side form validation
- Lucide icons
- Accessible, reusable UI components

### Backend
- uv 
- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic database migrations
- pytest
- Modular routers, services, repositories, schemas, and dependencies
- OpenAPI/Swagger documentation


### Database, identity, and storage
- Supabase PostgreSQL
- Supabase Auth for identity and authentication
- Supabase Storage for controlled file uploads when configured
- Google Drive URLs as an initial option for study materials
- A storage-provider interface that can support Amazon S3 and CloudFront later

### Initial deployment targets
- Frontend: Vercel or another suitable static frontend host
- Backend: Render or another suitable Python application host
- Database and authentication: Supabase

Verify current free-tier restrictions before deployment. Do not assume that free tiers have unlimited usage, persistent local disks, or permanent availability.

---

## 2. Brand and design system

Brand name: **Shahil Academy**

Create a polished education brand with:
- Navy blue, white, and pale blue as the main palette
- Clean typography and a consistent spacing scale
- Clear hierarchy and readable line lengths
- Reusable buttons, inputs, cards, dialogs, tables, tabs, badges, and alerts
- Subtle borders and shadows rather than excessive decoration
- Accessible color contrast and visible keyboard focus
- Responsive navigation and mobile drawers
- Loading indicators, skeletons, empty states, error states, and success notifications
- Responsive data tables that remain usable on mobile
- Consistent design across public, student, and admin pages

The visual quality should feel like a professional education platform. Avoid clutter, unnecessary animation, fake statistics, and fabricated testimonials.

Use realistic demo content only when clearly identified as demo content. Never present invented student counts, placements, reviews, or outcomes as real.

---

## 3. Public website pages

Create these pages:
- Home / landing page
- Course catalog
- Course details
- About Shahil Academy
- Contact/support
- Student login
- Student registration
- Forgot password
- Password reset
- Privacy policy
- Terms and conditions
- Not found page

### Homepage sections
- Header and responsive navigation
- Hero section with a clear value proposition
- Featured courses
- How learning works
- Benefits and learning features
- Frequently asked questions
- Contact or call-to-action section
- Footer with policy links

### Course catalog
Each course card may show:
- Thumbnail
- Title
- Short description
- Instructor
- Level
- Estimated duration
- Price, when configured
- Course details link
- Enrollment or purchase call to action

Only show published courses intended for public visibility. Do not expose draft topics, private resources, or protected URLs in public API responses.

---

## 4. Authentication and authorization

Use **Supabase Auth** as the single identity system unless a documented technical constraint requires another design.

Implement:
- Student registration
- Login and logout
- Email verification where configured
- Forgot-password and reset-password flow
- Current-user/profile endpoint
- Secure account and profile handling
- Admin login through the same identity system but with separately controlled authorization
- Token verification in FastAPI

### Admin provisioning
- Never allow public registration to create an admin.
- Admin access must be provisioned through a secure, authorized process.
- Store roles or permissions in trusted server-side data.
- Do not trust a role, user ID, enrollment status, or permission sent by the browser.
- Derive identity from verified access-token claims.
- Explain any Supabase configuration needed to support the selected authorization approach.

### Security boundary
Frontend route guards are for user experience only. FastAPI must independently verify identity, role, resource ownership, publication status, enrollment, and other permissions for every protected operation.

Never expose the Supabase service-role key or any privileged secret to frontend code.

---

## 5. Student portal

Create a dedicated student layout and these routes:
- `/student/dashboard`
- `/student/courses`
- `/student/courses/:courseId`
- `/student/learn/:topicId`
- `/student/doubts`
- `/student/announcements`
- `/student/profile`

### Student dashboard
Display real data from the backend:
- Welcome message
- Enrolled courses
- Course completion progress
- Continue Learning action
- Recently visited topics
- Completed topics
- Open or pending doubts
- Relevant announcements

### Student course experience
- Show only valid enrolled courses.
- Display the course's modules and topics.
- Provide expandable/collapsible module navigation.
- Show topic completion status.
- Provide previous-topic and next-topic navigation.
- Allow students to mark a topic complete when permitted.
- Resume from the last visited topic.
- Provide search and optional bookmarks.
- Support mobile lesson navigation.
- Display helpful empty states when the student has no courses.

The backend must prevent students from accessing unenrolled courses by changing URL parameters or sending direct API requests.

---

## 6. Course, module, and topic hierarchy

Use this structure:

```text
Course
└── Module
    └── Topic
        ├── Video lesson
        ├── Study resources
        ├── Questions and quizzes
        ├── Doubt section
        └── Progress and completion
```

Example course:

```text
Course: Data Science
├── Module 1: Python Programming
│   ├── Introduction to Python
│   ├── Variables and Data Types
│   ├── Conditional Statements
│   └── Loops
└── Module 2: SQL
    ├── Introduction to SQL
    ├── SELECT Queries
    └── Filtering Data
```

Each course should support:
- Title, slug, description, thumbnail
- Instructor name
- Level and estimated duration
- Optional price
- Draft, published, unpublished, or archived state
- Created/updated/published timestamps

Each module should support:
- Parent course
- Title and description
- Ordering
- Publication status

Each topic should support:
- Parent module
- Title and description
- Video provider and video reference
- Resources
- Questions or quiz
- Doubt section enabled/disabled
- Ordering
- Draft/published status
- Estimated duration, if useful

Content edits must not accidentally delete student progress. Prefer archival or safe deletion rules where historical records exist.

---

## 7. Video lessons

Initially support:
- YouTube watch URLs
- YouTube share URLs
- Validated YouTube embed references
- Unlisted videos where appropriate

Requirements:
- Validate video URLs on the backend.
- Store provider and provider-specific reference separately.
- Build a safe reusable YouTube player component.
- Do not accept arbitrary iframe HTML from administrators.
- Handle unavailable, private, deleted, or unsupported videos gracefully.
- Do not claim that an unlisted YouTube video is private or protected by LMS enrollment.
- Do not expose private S3 credentials.
- Design a video-provider interface so private S3/CloudFront playback can be added later.

---

## 8. Study resources and file uploads

Every topic may contain multiple resources.

Support:
- Google Drive links
- PDF files
- DOC files
- DOCX files
- ZIP files
- Additional permitted external links

Resource fields:
- Title
- Description
- Resource type
- External URL or storage key
- Display order
- Visibility/publication status
- Created/updated timestamps

### Admin actions
- Add a resource
- Edit title and description
- Paste a Google Drive or other permitted URL
- Upload a file when storage is configured
- Reorder resources
- Enable/disable visibility
- Delete or archive resources safely

### Student actions
- View permitted resources
- Open external links
- Download files when authorized
- See the resource title, type, and description

### Storage and upload security
- Use Supabase Storage or another configured object-storage service.
- Do not store file bytes in PostgreSQL.
- Validate size, permitted type, and file content where practical.
- Do not trust file extension or MIME type alone.
- Use unique storage keys and safe filenames.
- Protect private files using authorization checks and short-lived signed URLs where suitable.
- Do not make a private bucket publicly accessible just to make downloads work.
- Explain Google Drive sharing settings and test the intended access.
- Keep storage logic behind a service interface so S3 can be added later.
- If storage credentials or buckets are not configured, show clear setup instructions and do not claim uploads are functional.

---

## 9. Questions, practice, and quizzes

Each topic may include:
- Multiple-choice questions
- True/false questions
- Short-answer questions
- Ungraded practice questions
- Graded quizzes
- Marks and passing percentage
- Difficulty level
- Question order
- Optional explanations
- Attempt limits
- Retake configuration
- Configurable answer visibility

### Student functionality
- Open questions
- Submit answers
- View results when allowed
- Review explanations when allowed
- Retake quizzes if permitted
- View their own attempt history

### Admin functionality
- Create, edit, reorder, and delete questions
- Configure marks and passing percentage
- Configure attempt limits
- Control when results, correct answers, and explanations become visible

### Quiz security
- Grade answers on the backend.
- Do not send correct answers to the browser before the student is allowed to see them.
- Validate question IDs and submitted choices.
- Store quiz attempts and answers separately.
- Prevent students from reading another student's attempt records.
- Test grading rules and repeated submissions.

---

## 10. Topic-wise doubt management

Every topic may have a text-based doubt section.

### Student functionality
- Submit a text doubt linked to a topic
- View their own doubts and instructor replies
- See Open, Answered, or Resolved status
- View timestamps
- Edit or delete their own doubt only under defined rules
- Receive in-app notifications when a reply is added, if notifications are implemented

### Admin functionality
- View doubts by course, module, topic, student, and status
- Search and filter doubts
- Reply to a doubt
- Change status
- Reopen a doubt if needed
- Review conversation history

### Data and permissions
Store:
- Doubt author
- Topic reference
- Message text
- Replies and reply authors
- Status
- Created/updated timestamps

Students must not edit or delete other students' doubts. Every operation must be authorized on the backend.

Prepare for future instructor roles, threaded replies, and email notifications without making those future capabilities a prerequisite for the first working release.

---

## 11. Admin portal

Create a separate protected admin experience:
- `/admin/dashboard`
- `/admin/courses`
- `/admin/modules`
- `/admin/topics`
- `/admin/resources`
- `/admin/questions`
- `/admin/students`
- `/admin/enrollments`
- `/admin/doubts`
- `/admin/announcements`
- `/admin/reports`
- `/admin/settings`

### Admin dashboard
Show database-backed metrics:
- Total students
- Published courses
- Enrollments
- Modules and topics
- Pending doubts
- Course completion statistics

Do not hardcode dashboard metrics as if they were live data.

### Course management
- Create and edit courses
- Upload course thumbnails when configured
- Edit descriptions, level, instructor, duration, and optional price
- Create and reorder modules
- Create and reorder topics
- Add video links and resources
- Add questions and quizzes
- Enable/disable doubts
- Save drafts
- Publish and unpublish content
- Archive courses without destroying historical progress

### Student management
- Search and filter student accounts
- View profile and enrollment details
- Review learning progress
- Suspend access when authorized
- Never display passwords or sensitive authentication credentials

### Enrollment management
- Enroll students manually
- Revoke or expire access
- View enrollment history
- Prevent duplicate active enrollment records
- Log important administrative changes

All admin actions must be protected by backend authorization, not merely hidden buttons.

---

## 12. Enrollment, course access, and future payments

For the first release:
- Use admin-managed enrollments.
- Admins can grant or revoke access.
- Students can view only courses with valid enrollment.
- Enforce enrollment checks in FastAPI for every protected lesson, resource, quiz, and progress operation.

Prepare the data model for future paid enrollment and Razorpay integration.

Future payment requirements:
- Create payment orders on the backend.
- Verify provider signatures on the backend.
- Verify actual payment status.
- Create enrollments only after confirmed successful payment.
- Make webhook processing idempotent.
- Handle duplicate callbacks and retries safely.
- Never trust a frontend payment-success message.
- Never store payment-card details.

Do not implement fake payment success or imply that a payment has been processed when it has not.

---

## 13. Progress, bookmarks, and announcements

### Topic progress
Track:
- Student
- Topic
- Completion state
- Last visited timestamp
- Completion timestamp where applicable

Define and document how course progress is calculated. Avoid counting archived or irrelevant topics inconsistently. Preserve progress when content is edited.

### Bookmarks
Allow students to bookmark useful topics if included in the release. Restrict bookmark records to their owner.

### Announcements
Admins can create, publish, edit, and archive announcements. Support all-student or selected-course targeting. Students should only see announcements relevant to them.

---

## 14. Database architecture

Use PostgreSQL with UUIDs where appropriate, foreign keys, indexes, constraints, timestamps, and explicit deletion policies.

Recommended entities:
- `profiles`
- `courses`
- `modules`
- `topics`
- `topic_resources`
- `enrollments`
- `topic_progress`
- `bookmarks`
- `questions`
- `question_options`
- `quiz_attempts`
- `quiz_answers`
- `doubts`
- `doubt_replies`
- `announcements`
- `audit_logs`

### Database rules
- Link profile records to Supabase Auth user IDs.
- Keep identity credentials managed by Supabase Auth.
- Add uniqueness constraints for slugs and relevant enrollment relationships.
- Add indexes for common course, topic, enrollment, status, and timestamp queries.
- Use appropriate cascading or restrictive deletion behavior.
- Preserve historical records where necessary.
- Add database migrations using Alembic.
- Document the entity relationship diagram.
- Do not treat `Base.metadata.create_all()` as a replacement for versioned production migrations.

If Supabase Row Level Security (RLS) is enabled, implement and test policies consistent with the selected backend access model. Never expose the service-role key in frontend code.

---

## 15. FastAPI REST API

Use the versioned prefix `/api/v1`.

### Authentication and profile
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login` if required by the chosen auth flow
- `POST /api/v1/auth/logout` if required by the chosen auth flow
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`
- Profile read/update endpoints

Avoid duplicating Supabase Auth functionality unnecessarily. Document which operations are handled by Supabase and which are handled by FastAPI.

### Public course catalog
- `GET /api/v1/courses`
- `GET /api/v1/courses/{course_id}`

Return only information safe for public display.

### Student endpoints
- `GET /api/v1/student/dashboard`
- `GET /api/v1/student/courses`
- `GET /api/v1/student/courses/{course_id}`
- `GET /api/v1/student/topics/{topic_id}`
- `POST /api/v1/student/topics/{topic_id}/complete`
- `GET /api/v1/student/topics/{topic_id}/resources`
- `GET /api/v1/student/topics/{topic_id}/questions`
- Quiz attempt submission and result endpoints
- Doubt list, creation, and permitted update endpoints
- Bookmark endpoints
- Announcement endpoints

### Admin endpoints
Create authorized CRUD and management endpoints for:
- Courses
- Modules
- Topics
- Resources
- Questions and quizzes
- Students
- Enrollments
- Doubts and replies
- Announcements
- Reports and dashboard metrics
- Settings where appropriate

### API quality
- Pydantic validation
- Pagination, search, and filtering
- Appropriate HTTP status codes
- Consistent error response format
- Safe error messages
- Database transaction handling
- Generated OpenAPI documentation
- Authorization tests for every protected resource type

Keep route handlers thin and put business logic in services where practical.

---

## 16. Suggested project structure

```text
shahil-academy/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── pages/
│   │   │   ├── public/
│   │   │   ├── auth/
│   │   │   ├── student/
│   │   │   └── admin/
│   │   ├── hooks/
│   │   ├── routes/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── middleware/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
├── docs/
│   ├── database-schema.md
│   ├── api-specification.md
│   ├── deployment-guide.md
│   └── security-model.md
├── .gitignore
└── README.md
```

Adjust the structure when justified by the repository and implementation, but maintain clear separation of concerns.

---

## 17. Security requirements

Implement and test:
- Correct access-token verification
- Server-side role authorization
- Object-level authorization
- Enrollment and publication checks
- Safe file upload validation
- Safe external URL and embed handling
- CORS restricted to configured frontend origins
- Rate limiting for login and sensitive endpoints
- Secure handling of secrets and environment variables
- Appropriate logging without tokens, passwords, or sensitive personal data
- Safe error handling without stack-trace leakage
- Admin audit logs
- Database constraints
- Protected quiz answers
- Protection against unauthorized file downloads
- Prevention of role escalation and insecure direct object references

Do not commit credentials to Git. Use `.env.example` with placeholder values only. Explain how production secrets are configured through hosting-provider settings.

---

## 18. Testing and quality assurance

Use pytest for backend tests and suitable React testing tools for frontend tests. Add end-to-end tests for critical workflows.

Test at minimum:
1. Student registration/login flow.
2. Admin authentication and authorization.
3. Student cannot perform admin actions.
4. Student cannot access an unenrolled course.
5. Student cannot view unpublished lessons.
6. Student cannot access another student's profile, doubts, progress, or quiz attempts.
7. Correct quiz grading and answer visibility.
8. Invalid or oversized file uploads are rejected.
9. Private resource access is enforced.
10. Progress persists across sessions.
11. Doubt replies and status changes work.
12. Responsive layouts work at mobile and desktop widths.
13. Frontend production build succeeds.
14. Backend tests and lint/type checks pass.

Do not report tests as passed unless they were actually executed. Document failures and fix them before declaring a phase complete.

---

## 19. Deployment and local development

Provide clear instructions for Windows development.

Include:
- Prerequisites
- Git setup
- Frontend dependency installation
- Backend virtual environment and dependency installation
- Supabase project setup
- Database connection configuration
- Supabase Auth configuration
- Storage bucket and permissions setup
- Alembic migration commands
- Local run commands for frontend and backend
- Environment-variable templates
- API health endpoint
- Vercel deployment
- FastAPI host deployment
- Production CORS settings
- Logs and troubleshooting
- Database connection pooling guidance
- HTTPS and secret management
- Free-tier limitations and possible cold starts

Use environment variables for service URLs and secrets. Do not require a local `.env` file to exist during production builds when the hosting provider supplies environment variables. Never rely on local application disk for persistent production uploads unless a persistent volume is explicitly configured.

---

## 20. AI specialist skills

Use these responsibilities throughout the project.

### UI/UX Designer
Design accessible, consistent, mobile-first public, student, and admin experiences. Define tokens, navigation, component states, responsive behavior, and realistic content.

### React Frontend Engineer
Build typed reusable components, routing, API integration, form validation, loading/error states, and responsive dashboards. Never use frontend-only checks as the security boundary.

### FastAPI Backend Engineer
Implement modular endpoints, schemas, services, transactions, error handling, OpenAPI docs, and authorization dependencies. Test protected operations.

### Database Architect
Design normalized tables, migrations, constraints, indexes, relationships, and safe historical-data handling.

### Authentication and Security Engineer
Verify identity, enforce permissions, protect files and answers, prevent privilege escalation, and test negative authorization scenarios.

### LMS Content Engineer
Implement course hierarchy, lesson playback, resources, quizzes, progress, doubts, announcements, and storage adapters.

### DevOps Engineer
Configure Git, environment variables, deployment, migrations, health checks, logs, production origins, and troubleshooting.

### QA Engineer
Run unit, integration, frontend, and end-to-end tests; verify security and responsive behavior; report only real results.

Create optional skill files under `.agents/skills/<skill-name>/SKILL.md` if the selected coding agent supports that convention. Follow the target agent's actual skill-file conventions if they differ.

---

## 21. Required implementation sequence

### Phase 1 — Project foundation and design
- Inspect repository and existing files.
- Establish frontend and backend structure.
- Create the brand design system.
- Build the responsive public website.
- Build login, registration, and password recovery screens.
- Configure environment templates.
- Create initial Supabase integration.
- Provide local run instructions.

### Phase 2 — Identity and authorization
- Implement and test Supabase Auth integration.
- Add profile records and role management.
- Protect student and admin routes.
- Enforce server-side authorization.
- Configure and test migrations.

### Phase 3 — Course management and enrollment
- Create courses, modules, and topics.
- Build admin CRUD screens.
- Build student course catalog and dashboards.
- Implement admin-managed enrollments.
- Enforce course access on the backend.

### Phase 4 — Learning content
- Implement YouTube lessons.
- Implement external resource links.
- Configure and implement secure file storage.
- Implement topic navigation and progress.
- Add bookmarks if included.

### Phase 5 — Quizzes and doubts
- Implement questions and quiz attempts.
- Implement server-side grading.
- Implement doubt submission, replies, and status management.
- Test ownership and privacy rules.

### Phase 6 — Admin features and reports
- Implement student and enrollment management.
- Add announcements.
- Add real database-backed dashboard metrics.
- Add audit logs and useful reports.

### Phase 7 — Testing and deployment
- Run tests, linting, type checks, and production builds.
- Fix discovered failures.
- Deploy frontend, backend, and database configuration.
- Document remaining manual setup and known limitations.

---

## 22. Final delivery requirements

Deliver:
1. Working source code with complete file paths.
2. Public website and responsive student/admin portals.
3. Database schema and versioned migrations.
4. API endpoints and OpenAPI documentation.
5. Authentication and authorization implementation.
6. `.env.example` files with placeholders only.
7. Automated tests and actual test results.
8. README with Windows setup instructions.
9. Deployment guide for the chosen hosting providers.
10. Database ER diagram and architecture documentation.
11. A list of required secrets/configuration that the user must add.
12. A list of limitations or features that remain incomplete.

### Working rules
- Inspect before editing.
- Make small, verifiable changes.
- Build real functionality, not just visual placeholders.
- Wire every implemented button and form to its intended action.
- Do not leave core functionality as TODOs.
- Do not invent credentials, test results, deployment success, or payment outcomes.
- If an external account, secret, or provider configuration is unavailable, clearly state what is required and continue with the work that can be completed.
- After each phase, report files changed, commands executed, tests actually run, results, and outstanding setup.
- Do not stop after building the homepage.
- Do not produce one enormous, untested code dump.

## First action

Begin by inspecting the repository. Then present the architecture, folder structure, database ER diagram, route/page plan, API specification, environment templates, and a working Phase 1 implementation. Continue through the phases until the specified features are implemented and tested, clearly identifying anything that still requires external configuration.

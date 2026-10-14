# Security model

- FastAPI owns registration and login, hashes passwords with PBKDF2-HMAC-SHA256, signs expiring HMAC JWTs, and looks up trusted roles in `profiles`.
- Registration does not verify email ownership. Treat email addresses as unverified identifiers, never as proof of identity or authorization.
- Email-based password recovery is not configured. Lost-account recovery requires a trusted administrator workflow.
- Public sign-up always provisions a student profile; there is no public role assignment operation.
- Admin routes require the database-backed `admin` role. Student routes enforce enrollment, published course/module/topic state, and owner checks independently of frontend guards.
- Quiz grading runs in the backend. Correct answers and explanations are omitted from student question responses.
- Resource links are validated HTTP(S) URLs. Private file upload/download is not advertised until an authenticated object-storage provider is configured.
- Configure CORS to exact deployed frontend origins. Do not put JWT signing keys or database credentials in frontend variables.
- Rate limiting is delegated to a production edge/API gateway until a shared, deployment-appropriate limiter is configured; do not rely on per-process memory for production limits.
- The application accesses the database only through its backend; the frontend must not query privileged tables directly.

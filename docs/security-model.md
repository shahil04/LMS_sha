# Security model

- Supabase Auth is the sole identity provider. FastAPI verifies bearer JWTs against the configured Supabase issuer/JWKS and looks up trusted roles in `profiles`.
- Public sign-up always provisions a student profile; there is no public role assignment operation.
- Admin routes require the database-backed `admin` role. Student routes enforce enrollment, published course/module/topic state, and owner checks independently of frontend guards.
- Quiz grading runs in the backend. Correct answers and explanations are omitted from student question responses.
- Resource links are validated HTTP(S) URLs. Private file upload/download is not advertised until an authenticated object-storage provider is configured.
- Configure CORS to exact deployed frontend origins. Do not put service-role keys or database credentials in frontend variables.
- Rate limiting is delegated to a production edge/API gateway until a shared, deployment-appropriate limiter is configured; do not rely on per-process memory for production limits.
- Supabase RLS must be enabled and tested if clients access tables directly. This application accesses the database only through its backend; the frontend must not query privileged tables directly.

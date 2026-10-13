import { useMemo, useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  ArrowRight, BookOpen, Check, CheckCircle2, Clock3, GraduationCap, Play, Search,
} from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, apiData, errorMessage, type Course, type Doubt, type Module, type Topic } from "./api";
import { supabase, useAuth } from "./auth";
import {
  Button, EmptyState, Field, FormShell, Loading, Notice, PageTitle, TextArea,
} from "./ui";

function QueryError({ error }: { error: unknown }) {
  return <Notice tone="error">{errorMessage(error)}. Make sure the API is running and try again.</Notice>;
}

function CourseCard({ course }: { course: Course }) {
  return <article className="course-card">
    <div className="course-cover"><BookOpen size={32} /></div>
    <span className="badge">{course.level || "All levels"}</span>
    <h3>{course.title}</h3><p>{course.description || "A structured course from Shahil Academy."}</p>
    <div className="course-meta"><span>{course.instructor_name}</span><span>{course.duration_minutes ? `${course.duration_minutes} min` : "Self-paced"}</span></div>
    <Link className="card-link" to={`/courses/${course.slug}`}>Explore course <ArrowRight size={15} /></Link>
  </article>;
}

export function HomePage() {
  const courses = useQuery({ queryKey: ["public-courses", "home"], queryFn: () => apiData<Course[]>(api.get("/courses?limit=3")) });
  return <>
    <section className="hero"><div className="container hero-grid">
      <div><span className="eyebrow">A better way to learn</span>
        <h1>Build knowledge.<br /><em>Grow with confidence.</em></h1>
        <p className="hero-copy">Clear lessons, practical resources, and a learning path that helps you move forward one topic at a time.</p>
        <div className="hero-actions"><Link className="button button-primary" to="/courses">Explore courses <ArrowRight size={16} /></Link><Link className="button button-secondary" to="/about">Meet Shahil Academy</Link></div>
        <p className="hero-note">Learn at your own pace. Revisit lessons whenever you need.</p>
      </div>
      <div className="hero-card">
        <div className="hero-card-head"><span>Your next learning session</span><span className="pill">Self-paced</span></div>
        <div className="learning-preview"><div className="preview-icon"><Play size={20} fill="currentColor" /></div>
          <h3>One topic at a time</h3><p>Lessons, notes, and practice in one place.</p>
          <div className="preview-progress"><span><b>Keep your momentum</b><span>Learn steadily</span></span><div className="progress-track"><div className="progress-fill" style={{ width: "64%" }} /></div></div>
        </div>
      </div>
    </div></section>
    <section className="section"><div className="container">
      <div className="section-heading"><div><span className="eyebrow">Explore</span><h2>Find a course that moves you forward</h2><p>Browse published courses and see what each learning path covers.</p></div><Link className="inline-link" to="/courses">All courses <ArrowRight size={14} /></Link></div>
      {courses.isPending ? <Loading /> : courses.error ? <QueryError error={courses.error} /> :
        courses.data.length ? <div className="course-grid">{courses.data.map((course) => <CourseCard key={course.id} course={course} />)}</div> :
          <EmptyState title="Courses are being prepared" description="Published courses will appear here when they are available." />}
    </div></section>
    <section className="section section-soft"><div className="container">
      <div className="center-heading"><span className="eyebrow">Designed for real learning</span><h2>Everything you need to keep making progress</h2><p>A focused learning environment that brings lessons, practice, and support together.</p></div>
      <div className="feature-grid">
        <Feature icon={<BookOpen size={20} />} title="Structured lessons" text="Learn through clear modules and focused topics, with a path you can follow at your own pace." />
        <Feature icon={<CheckCircle2 size={20} />} title="Visible progress" text="Mark lessons complete and return to your learning with your progress saved." />
        <Feature icon={<GraduationCap size={20} />} title="Ask when you need help" text="Submit topic-specific doubts and follow the conversation with your instructor." />
      </div>
    </div></section>
    <section className="section"><div className="container">
      <div className="center-heading"><span className="eyebrow">How it works</span><h2>A simple path from signup to understanding</h2></div>
      <div className="steps"><Step number="01" title="Choose your course" text="Explore the catalog and find a course that matches your goals." />
        <Step number="02" title="Learn at your pace" text="Work through published lessons, resources, and practice topics." />
        <Step number="03" title="Track and ask" text="Save progress, try quizzes, and send doubts whenever you need support." /></div>
    </div></section>
    <section className="section section-soft"><div className="container">
      <div className="center-heading"><span className="eyebrow">Common questions</span><h2>Good to know</h2></div>
      <div className="faq-list">
        <details><summary>How do I get access to a course?</summary><p>Create a student account and contact the academy or your administrator about enrollment. Course access is granted by the academy.</p></details>
        <details><summary>Can I learn on my own schedule?</summary><p>Courses are designed for self-paced study. Your enrolled courses and topic progress are available from your student space.</p></details>
        <details><summary>Can I ask a question about a lesson?</summary><p>Where the instructor has enabled doubts, submit your question from the lesson or your doubts page and review replies in your account.</p></details>
      </div>
    </div></section>
    <section className="section"><div className="container"><div className="cta"><div><h2>Ready to start learning?</h2><p>Create an account and begin your next learning chapter.</p></div><Link className="button button-secondary" to="/register">Create your account <ArrowRight size={15} /></Link></div></div></section>
  </>;
}

function Feature({ icon, title, text }: { icon: ReactNode; title: string; text: string }) {
  return <article className="feature"><span className="feature-icon">{icon}</span><h3>{title}</h3><p>{text}</p></article>;
}
function Step({ number, title, text }: { number: string; title: string; text: string }) {
  return <article className="step"><span className="step-number">{number}</span><h3>{title}</h3><p>{text}</p></article>;
}

export function CatalogPage() {
  const [search, setSearch] = useState("");
  const query = useQuery({
    queryKey: ["public-courses", search],
    queryFn: () => apiData<Course[]>(api.get("/courses", { params: { q: search || undefined } })),
  });
  return <div className="container text-page" style={{ maxWidth: 1160 }}>
    <PageTitle eyebrow="Course catalog" title="Explore our courses" description="Browse published learning paths from Shahil Academy." />
    <div className="toolbar" style={{ marginBottom: 24 }}><label className="field" style={{ flex: 1, maxWidth: 420 }}>
      <span className="sr-only">Search courses</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search courses…" aria-label="Search courses" />
    </label><Search size={18} color="#778896" /></div>
    {query.isPending ? <Loading /> : query.error ? <QueryError error={query.error} /> :
      query.data.length ? <div className="course-grid">{query.data.map((course) => <CourseCard key={course.id} course={course} />)}</div> :
        <EmptyState title="No published courses found" description={search ? "Try another search term." : "New courses will appear here when they are published."} />}
  </div>;
}

export function PublicCoursePage() {
  const { slug = "" } = useParams();
  const { session } = useAuth();
  const course = useQuery({ queryKey: ["public-course", slug], queryFn: () => apiData<Course>(api.get(`/courses/${slug}`)) });
  if (course.isPending) return <div className="container"><Loading /></div>;
  if (course.error) return <div className="container narrow-page"><QueryError error={course.error} /></div>;
  return <div className="container text-page" style={{ maxWidth: 960 }}>
    <span className="eyebrow">Course overview</span><h1>{course.data.title}</h1>
    <p>{course.data.description}</p>
    <div className="toolbar" style={{ margin: "20px 0" }}><span className="badge">{course.data.level}</span><span className="muted">Instructor: {course.data.instructor_name}</span><span className="muted">{course.data.duration_minutes ? `${course.data.duration_minutes} minutes` : "Self-paced"}</span></div>
    {session ? <Notice>To access full lessons and resources, ask an administrator to enroll your account.</Notice> :
      <Link to="/register" className="button button-primary">Create a student account <ArrowRight size={15} /></Link>}
    <section className="panel" style={{ marginTop: 28 }}><h2>Course outline</h2>
      {course.data.modules?.length ? course.data.modules.map((module) => <div className="content-item" key={module.id}>
        <h3>{module.title}</h3>{module.description && <p>{module.description}</p>}
        <ul>{module.topics?.map((topic) => <li key={topic.id} className="muted">{topic.title}</li>)}</ul>
      </div>) : <EmptyState title="Outline coming soon" description="The course outline will be available once published." />}
    </section>
  </div>;
}

const loginSchema = z.object({ email: z.string().email(), password: z.string().min(8) });
const registerSchema = z.object({ full_name: z.string().min(1, "Enter your name"), email: z.string().email(), password: z.string().min(8, "Use at least 8 characters") });
const emailSchema = z.object({ email: z.string().email() });

export function AuthPage({ mode }: { mode: "login" | "register" | "forgot" }) {
  const navigate = useNavigate();
  const { configured, refreshProfile } = useAuth();
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const schema = mode === "register" ? registerSchema : mode === "forgot" ? emailSchema : loginSchema;
  const form = useForm({ resolver: zodResolver(schema) });
  const submit = form.handleSubmit(async (values) => {
    setError(""); setNotice("");
    if (!supabase) { setError("Add your Supabase URL and anon key to frontend/.env, then restart the app."); return; }
    try {
      const fields = values as { email: string; password?: string; full_name?: string };
      if (mode === "login") {
        const { error: authError } = await supabase.auth.signInWithPassword({ email: fields.email, password: fields.password! });
        if (authError) throw authError;
        const profile = await refreshProfile();
        navigate(profile?.role === "admin" ? "/admin/dashboard" : "/student/dashboard");
      } else if (mode === "register") {
        const { error: authError } = await supabase.auth.signUp({
          email: fields.email, password: fields.password!,
          options: { data: { full_name: fields.full_name }, emailRedirectTo: `${window.location.origin}/student/dashboard` },
        });
        if (authError) throw authError;
        setNotice("Account created. Check your email to verify it, then sign in.");
      } else {
        const { error: authError } = await supabase.auth.resetPasswordForEmail(fields.email, {
          redirectTo: `${window.location.origin}/reset-password`,
        });
        if (authError) throw authError;
        setNotice("If an account exists for that email, a password reset link has been sent.");
      }
    } catch (reason) { setError(errorMessage(reason)); }
  });

  const title = mode === "login" ? "Welcome back" : mode === "register" ? "Create your account" : "Reset your password";
  const description = mode === "login" ? "Sign in to continue learning." : mode === "register" ? "Join Shahil Academy as a student." : "We’ll send a secure reset link to your email.";
  return <FormShell title={title} description={description} onSubmit={(event) => { void submit(event); }}>
    {!configured && <Notice tone="error">Supabase is not configured. Set <code>VITE_SUPABASE_URL</code> and <code>VITE_SUPABASE_ANON_KEY</code>.</Notice>}
    {error && <Notice tone="error">{error}</Notice>}{notice && <Notice tone="success">{notice}</Notice>}
    {mode === "register" && <Field label="Full name" placeholder="Your name" autoComplete="name" {...form.register("full_name")} />}
    <Field label="Email address" type="email" placeholder="you@example.com" autoComplete="email" {...form.register("email")} />
    {mode !== "forgot" && <Field label="Password" type="password" placeholder="At least 8 characters" autoComplete={mode === "login" ? "current-password" : "new-password"} {...form.register("password")} />}
    {Object.values(form.formState.errors).map((item, index) => <small className="field-error" key={index}>{String(item?.message)}</small>)}
    <Button type="submit" disabled={form.formState.isSubmitting}>{form.formState.isSubmitting ? "Please wait…" : mode === "login" ? "Sign in" : mode === "register" ? "Create account" : "Send reset link"}</Button>
    <div className="form-foot">{mode === "login" ? <>New here? <Link to="/register">Create an account</Link><br /><Link to="/forgot-password">Forgot password?</Link></> :
      mode === "register" ? <>Already have an account? <Link to="/login">Sign in</Link></> : <Link to="/login">Back to sign in</Link>}</div>
  </FormShell>;
}

export function ResetPasswordPage() {
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const form = useForm({ resolver: zodResolver(z.object({ password: z.string().min(8) })) });
  const submit = form.handleSubmit(async ({ password }) => {
    setNotice(""); setError("");
    if (!supabase) { setError("Supabase is not configured."); return; }
    const { error: result } = await supabase.auth.updateUser({ password });
    if (result) setError(result.message); else setNotice("Password updated. You can now sign in.");
  });
  return <FormShell title="Choose a new password" description="Use at least 8 characters for your new password." onSubmit={(event) => { void submit(event); }}>
    {error && <Notice tone="error">{error}</Notice>}{notice && <Notice tone="success">{notice}</Notice>}
    <Field label="New password" type="password" autoComplete="new-password" {...form.register("password")} />
    {form.formState.errors.password && <small className="field-error">{String(form.formState.errors.password.message)}</small>}
    <Button type="submit" disabled={form.formState.isSubmitting}>Update password</Button>
    <div className="form-foot"><Link to="/login">Back to sign in</Link></div>
  </FormShell>;
}

export function InfoPage({ page }: { page: "about" | "contact" | "privacy" | "terms" }) {
  const content = {
    about: ["About Shahil Academy", "We’re building a focused online learning space where students can follow structured courses, practice what they learn, and ask for help when they need it.", "Our approach", "Lessons are organized into courses, modules, and topics. Students can track their progress and use course resources at their own pace. Course availability depends on enrollment."],
    contact: ["Contact and support", "For enrollment, course access, or learning support, contact the academy through the support channel shared with you by your administrator.", "Need account help?", "Use the password recovery link on the sign-in page. Never send your password or authentication codes to anyone."],
    privacy: ["Privacy policy", "Shahil Academy uses account and learning information to provide course access, save progress, answer doubts, and operate the platform.", "Information and access", "Student records and course activity are available only to the student and authorized administrators for legitimate learning and support purposes. Authentication is handled by Supabase. Contact the academy to ask about your account data."],
    terms: ["Terms and conditions", "Use your own account and keep your sign-in credentials secure. Course materials are provided for enrolled learners and should not be redistributed without permission.", "Course access", "Course access is managed by the academy and may be changed by an authorized administrator. Availability of third-party links or video services is subject to those providers."],
  }[page];
  return <div className="container text-page"><span className="eyebrow">Shahil Academy</span><h1>{content[0]}</h1><p>{content[1]}</p><h2>{content[2]}</h2><p>{content[3]}</p>{page === "contact" && <Link className="button button-primary" to="/courses">Explore courses</Link>}</div>;
}

function CourseProgressCard({ course, link }: { course: Course; link: string }) {
  return <div className="course-row"><div className="course-cover"><BookOpen size={26} /></div>
    <div style={{ flex: 1 }}><h3><Link to={link}>{course.title}</Link></h3><p>{course.instructor_name} · {course.level}</p>
      <div className="course-row-meta"><span>{course.completed_topics || 0} / {course.topic_count || 0} topics</span><b>{course.progress_percent || 0}%</b></div>
      <div className="progress-track" style={{ marginTop: 7 }}><div className="progress-fill" style={{ width: `${course.progress_percent || 0}%` }} /></div>
    </div></div>;
}

export function StudentDashboardPage() {
  const query = useQuery({ queryKey: ["student-dashboard"], queryFn: () => apiData<{
    profile: { full_name: string }; courses: Course[]; open_doubts: number;
    announcements: { id: string; title: string; message: string }[];
    recent_topics: Topic[];
  }>(api.get("/student/dashboard")) });
  if (query.isPending) return <Loading />;
  if (query.error) return <QueryError error={query.error} />;
  const data = query.data;
  return <>
    <PageTitle eyebrow="Student space" title={`Welcome${data.profile.full_name ? `, ${data.profile.full_name}` : ""}`}
      description="Pick up where you left off or explore your enrolled courses." />
    <div className="stat-grid"><Stat label="Enrolled courses" value={data.courses.length} /><Stat label="Open doubts" value={data.open_doubts} />
      <Stat label="Topics completed" value={data.courses.reduce((total, course) => total + (course.completed_topics || 0), 0)} />
      <Stat label="Announcements" value={data.announcements.length} /></div>
    <div className="dashboard-grid"><section className="panel"><h2>Your courses</h2>
      {data.courses.length ? <div>{data.courses.map((course) => <CourseProgressCard key={course.id} course={course} link={`/student/courses/${course.id}`} />)}</div> :
        <EmptyState title="No courses yet" description="Your administrator can enroll your account in a course." action={<Link className="button button-secondary" to="/courses">Browse catalog</Link>} />}
    </section><div className="stack">
      <section className="panel"><h2>Continue learning</h2>
        {data.recent_topics.length ? data.recent_topics.map((topic) => <div className="content-item" key={topic.id}><Link className="inline-link" to={`/student/learn/${topic.id}`}>{topic.title}</Link></div>) :
          <p className="muted">Your recently visited lessons will appear here.</p>}
      </section>
      <section className="panel"><h2>Announcements</h2>{data.announcements.length ? data.announcements.map((announcement) =>
        <div className="content-item" key={announcement.id}><h3>{announcement.title}</h3><p>{announcement.message}</p></div>) :
          <p className="muted">No announcements at this time.</p>}
      </section>
    </div></div>
  </>;
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return <div className="stat-card"><span>{label}</span><strong>{value}</strong></div>;
}

export function StudentCoursesPage() {
  const courses = useQuery({ queryKey: ["student-courses"], queryFn: () => apiData<Course[]>(api.get("/student/courses")) });
  if (courses.isPending) return <Loading />;
  if (courses.error) return <QueryError error={courses.error} />;
  return <><PageTitle eyebrow="Learning library" title="My courses" description="Your current course access and learning progress." />
    {courses.data.length ? <div className="course-grid">{courses.data.map((course) => <article key={course.id} className="course-card">
      <div className="course-cover"><BookOpen size={30} /></div><span className="badge">{course.level}</span><h3>{course.title}</h3><p>{course.description}</p>
      <div className="preview-progress"><span><b>Progress</b><span>{course.progress_percent || 0}%</span></span><div className="progress-track"><div className="progress-fill" style={{ width: `${course.progress_percent || 0}%` }} /></div></div>
      <Link className="card-link" to={`/student/courses/${course.id}`}>Open course <ArrowRight size={15} /></Link>
    </article>)}</div> :
      <EmptyState title="Your courses will appear here" description="You don’t have an active enrollment yet. Ask your administrator to grant course access." action={<Link to="/courses" className="button button-secondary">Browse catalog</Link>} />}
  </>;
}

export function StudentCoursePage() {
  const { courseId = "" } = useParams();
  const query = useQuery({ queryKey: ["student-course", courseId], queryFn: () => apiData<Course>(api.get(`/student/courses/${courseId}`)) });
  if (query.isPending) return <Loading />;
  if (query.error) return <QueryError error={query.error} />;
  const course = query.data;
  return <>
    <PageTitle eyebrow="Course" title={course.title} description={course.description} />
    <div className="panel"><div className="course-meta" style={{ border: 0, margin: 0, padding: 0 }}><span>{course.instructor_name} · {course.level}</span><span>{course.duration_minutes ? `${course.duration_minutes} min` : "Self-paced"}</span></div></div>
    {course.modules?.length ? course.modules.map((module) => <section className="panel" key={module.id} style={{ marginTop: 18 }}>
      <h2>{module.title}</h2>{module.description && <p className="muted">{module.description}</p>}
      <div className="content-list">{module.topics.map((topic) => <Link key={topic.id} to={`/student/learn/${topic.id}`} className="content-item course-row" style={{ alignItems: "center" }}>
        <div className="empty-icon" style={{ width: 35, height: 35, margin: 0 }}>{topic.is_complete ? <Check size={17} /> : <Play size={15} />}</div>
        <div style={{ flex: 1 }}><h3>{topic.title}</h3><p>{topic.duration_minutes ? `${topic.duration_minutes} min` : "Lesson"}</p></div>
        {topic.is_complete && <span className="badge badge-success">Complete</span>}
      </Link>)}</div>
    </section>) : <EmptyState title="Course outline is not ready" description="Published lessons will appear here." />}
  </>;
}

type QuizQuestion = { id: string; prompt: string; question_type: string; options: string[]; marks: number };
export function LessonPage() {
  const { topicId = "" } = useParams();
  const queryClient = useQueryClient();
  const topic = useQuery({ queryKey: ["student-topic", topicId], queryFn: () => apiData<Topic & { course: Course; module: Module; resources: { id: string; title: string; description: string; external_url: string }[] }>(api.get(`/student/topics/${topicId}`)) });
  const questions = useQuery({ queryKey: ["topic-questions", topicId], queryFn: () => apiData<QuizQuestion[]>(api.get(`/student/topics/${topicId}/questions`)), enabled: Boolean(topic.data) });
  const bookmarks = useQuery({ queryKey: ["student-bookmarks"], queryFn: () => apiData<Topic[]>(api.get("/student/bookmarks")) });
  const outline = useQuery({
    queryKey: ["student-course", topic.data?.module.course_id],
    queryFn: () => apiData<Course>(api.get(`/student/courses/${topic.data?.module.course_id}`)),
    enabled: Boolean(topic.data),
  });
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<{ score: number; max_score: number; percentage: number; passed: boolean } | null>(null);
  const [error, setError] = useState("");
  const complete = useMutation({
    mutationFn: () => apiData(api.post(`/student/topics/${topicId}/complete`)),
    onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ["student-topic", topicId] }); void queryClient.invalidateQueries({ queryKey: ["student-course", topic.data?.module.course_id] }); },
  });
  const toggleBookmark = useMutation({
    mutationFn: (bookmarked: boolean) => bookmarked
      ? apiData(api.delete(`/student/bookmarks/${topicId}`))
      : apiData(api.post(`/student/bookmarks/${topicId}`)),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["student-bookmarks"] }),
  });
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError("");
    try {
      const data = await apiData<{ score: number; max_score: number; percentage: number; passed: boolean }>(api.post(`/student/topics/${topicId}/attempts`, { answers }));
      setResult(data);
    } catch (reason) { setError(errorMessage(reason)); }
  };
  if (topic.isPending) return <Loading />;
  if (topic.error) return <QueryError error={topic.error} />;
  const lesson = topic.data;
  const courseTopics = outline.data?.modules?.flatMap((module) => module.topics) || [];
  const currentTopicIndex = courseTopics.findIndex((item) => item.id === topicId);
  const previousTopic = currentTopicIndex > 0 ? courseTopics[currentTopicIndex - 1] : undefined;
  const nextTopic = currentTopicIndex >= 0 ? courseTopics[currentTopicIndex + 1] : undefined;
  const isBookmarked = bookmarks.data?.some((item) => item.id === topicId) || false;
  return <>
    <PageTitle eyebrow={lesson.course.title} title={lesson.title} description={lesson.description}
      action={<div className="toolbar">
        <Button variant="secondary" disabled={toggleBookmark.isPending || bookmarks.isPending} onClick={() => toggleBookmark.mutate(isBookmarked)}>
          {isBookmarked ? "Bookmarked" : "Bookmark"}
        </Button>
        <Button variant={lesson.is_complete ? "secondary" : "primary"} disabled={complete.isPending || lesson.is_complete} onClick={() => complete.mutate()}>
          {lesson.is_complete ? <><CheckCircle2 size={16} /> Completed</> : "Mark complete"}
        </Button>
      </div>} />
    {complete.error && <QueryError error={complete.error} />}
    {toggleBookmark.error && <QueryError error={toggleBookmark.error} />}
    <div className="lesson-layout">
      <div className="stack">
        {lesson.video_provider === "youtube" && lesson.video_ref ?
          <iframe className="video-frame" src={`https://www.youtube-nocookie.com/embed/${encodeURIComponent(lesson.video_ref)}`}
            title={`${lesson.title} video`} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowFullScreen referrerPolicy="strict-origin-when-cross-origin" /> :
          <div className="video-placeholder"><div><Play size={32} /><p>No video is attached to this lesson.</p></div></div>}
        <section className="panel"><h2>About this lesson</h2><p className="muted">{lesson.description || "Work through the lesson and use the resources below to support your study."}</p>
          <div className="course-meta"><span><Clock3 size={14} /> {lesson.duration_minutes ? `${lesson.duration_minutes} min` : "Self-paced"}</span><span>{lesson.module.title}</span></div>
        </section>
        <section className="panel"><h2>Study resources</h2>{lesson.resources.length ? lesson.resources.map((resource) =>
          <div className="content-item" key={resource.id}><h3>{resource.title}</h3><p>{resource.description}</p>
            <a className="inline-link" href={resource.external_url} target="_blank" rel="noreferrer">Open resource <ArrowRight size={13} /></a></div>) :
          <p className="muted">No resources have been added to this lesson.</p>}</section>
        <section className="panel"><h2>Practice questions</h2>
          {questions.isPending ? <p className="muted">Loading questions…</p> : questions.error ? <QueryError error={questions.error} /> :
            questions.data.length ? <form onSubmit={(event) => { void submit(event); }} className="form-stack">
              {questions.data.map((question) => <fieldset key={question.id} className="content-item">
                <legend><b>{question.prompt}</b> <span className="muted">({question.marks} marks)</span></legend>
                {question.options.length ? <div className="quiz-options">{question.options.map((option) =>
                  <label className="quiz-option" key={option}><input type="radio" name={question.id} value={option}
                    checked={answers[question.id] === option} onChange={() => setAnswers((current) => ({ ...current, [question.id]: option }))} />{option}</label>)}</div> :
                  <Field label="Your answer" value={answers[question.id] || ""} onChange={(event) => setAnswers((current) => ({ ...current, [question.id]: event.target.value }))} />}
              </fieldset>)}
              {error && <Notice tone="error">{error}</Notice>}
              {result && <Notice tone="success">Score: {result.score} / {result.max_score} ({result.percentage}%). {result.passed ? "Passing score achieved." : "Keep practicing and try again if attempts are available."}</Notice>}
              <Button type="submit">Submit answers</Button>
            </form> : <p className="muted">No practice questions are available yet.</p>}
        </section>
      </div>
      <aside className="panel"><h2>In this module</h2><nav className="topic-nav">
        <Link to={`/student/courses/${lesson.module.course_id}`}>← {lesson.module.title}</Link>
        {courseTopics.map((item) => <Link key={item.id} className={item.id === topicId ? "active" : ""} to={`/student/learn/${item.id}`}>
          {item.is_complete ? "✓ " : ""}{item.title}
        </Link>)}</nav>
        <div className="toolbar" style={{ marginTop: 12, justifyContent: "space-between" }}>
          {previousTopic ? <Link className="inline-link" to={`/student/learn/${previousTopic.id}`}>← Previous</Link> : <span />}
          {nextTopic ? <Link className="inline-link" to={`/student/learn/${nextTopic.id}`}>Next →</Link> : <span />}
        </div>
        <hr className="separator" /><Link className="inline-link" to="/student/doubts">Ask or review a doubt <ArrowRight size={13} /></Link>
      </aside>
    </div>
  </>;
}

export function StudentDoubtsPage() {
  const queryClient = useQueryClient();
  const doubts = useQuery({ queryKey: ["student-doubts"], queryFn: () => apiData<Doubt[]>(api.get("/student/doubts")) });
  const courses = useQuery({ queryKey: ["student-courses"], queryFn: () => apiData<Course[]>(api.get("/student/courses")) });
  const outlines = useQueries({ queries: (courses.data || []).map((course) => ({
    queryKey: ["student-course", course.id],
    queryFn: () => apiData<Course>(api.get(`/student/courses/${course.id}`)),
  })) });
  const [topicId, setTopicId] = useState("");
  const [message, setMessage] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const topics = useMemo(() => outlines.flatMap((outline) => outline.data?.modules?.flatMap((module) =>
    module.topics.map((topic) => ({ ...topic, course_title: outline.data?.title || "", module_title: module.title }))) || []), [outlines]);
  const send = async (event: FormEvent) => {
    event.preventDefault(); setError(""); setNotice("");
    try {
      await apiData(api.post("/student/doubts", { topic_id: topicId, message }));
      setNotice("Your doubt was submitted."); setMessage("");
      await queryClient.invalidateQueries({ queryKey: ["student-doubts"] });
    } catch (reason) { setError(errorMessage(reason)); }
  };
  return <>
    <PageTitle eyebrow="Student support" title="My doubts" description="Ask a topic-specific question and follow replies from the academy." />
    <section className="panel"><h2>Ask a doubt</h2>
      {error && <Notice tone="error">{error}</Notice>}{notice && <Notice tone="success">{notice}</Notice>}
      {!topics.length ? <p className="muted">Enroll in a course to submit a doubt about a lesson.</p> :
        <form onSubmit={(event) => { void send(event); }} className="form-stack">
          <label className="field"><span>Topic</span><select className="input" required value={topicId} onChange={(event) => setTopicId(event.target.value)}>
            <option value="">Choose a lesson</option>{topics.map((topic) => <option key={topic.id} value={topic.id}>{topic.course_title} · {topic.module_title} · {topic.title}</option>)}
          </select></label>
          <TextArea label="Your question" required minLength={1} maxLength={10000} value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Describe what you’d like help with…" />
          <Button type="submit">Submit doubt</Button>
        </form>}
    </section>
    <section className="panel"><h2>Your conversations</h2>
      {doubts.isPending ? <Loading /> : doubts.error ? <QueryError error={doubts.error} /> :
        doubts.data.length ? <div className="content-list">{doubts.data.map((doubt) => <article className="content-item" key={doubt.id}>
          <div className="toolbar" style={{ justifyContent: "space-between" }}><h3>{doubt.topic_title || "Lesson doubt"}</h3><span className={`badge ${doubt.status === "answered" || doubt.status === "resolved" ? "badge-success" : "badge-warning"}`}>{doubt.status}</span></div>
          <p>{doubt.message}</p><small className="muted">{new Date(doubt.created_at).toLocaleString()}</small>
          {doubt.replies.map((reply) => <div className="callout" key={reply.id} style={{ marginTop: 12 }}><b>{reply.author_name}</b><p>{reply.message}</p></div>)}
        </article>)}</div> : <EmptyState title="No doubts yet" description="Questions you submit will be listed here with their replies." />}
    </section>
  </>;
}

export function StudentAnnouncementsPage() {
  const query = useQuery({ queryKey: ["student-announcements"], queryFn: () => apiData<{ id: string; title: string; message: string; published_at: string }[]>(api.get("/student/announcements")) });
  return <><PageTitle eyebrow="Academy updates" title="Announcements" description="Updates from Shahil Academy that are relevant to your courses." />
    {query.isPending ? <Loading /> : query.error ? <QueryError error={query.error} /> : query.data.length ? <div className="content-list">
      {query.data.map((item) => <article className="panel" key={item.id}><h2>{item.title}</h2><p className="muted">{item.message}</p><small className="muted">{item.published_at ? new Date(item.published_at).toLocaleString() : ""}</small></article>)}
    </div> : <EmptyState title="No announcements" description="Relevant academy updates will appear here." />}
  </>;
}

export function StudentProfilePage() {
  const { profile, refreshProfile } = useAuth();
  const [name, setName] = useState(profile?.full_name || "");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const save = async (event: FormEvent) => {
    event.preventDefault(); setError(""); setNotice("");
    try { await apiData(api.patch("/auth/me", { full_name: name })); await refreshProfile(); setNotice("Profile saved."); }
    catch (reason) { setError(errorMessage(reason)); }
  };
  return <><PageTitle eyebrow="Account" title="Your profile" description="Update the name shown in your learning space." />
    <div className="panel" style={{ maxWidth: 650 }}>{error && <Notice tone="error">{error}</Notice>}{notice && <Notice tone="success">{notice}</Notice>}
      <form className="form-stack" onSubmit={(event) => { void save(event); }}><Field label="Email address" value={profile?.email || ""} readOnly />
        <Field label="Full name" value={name} onChange={(event) => setName(event.target.value)} required maxLength={160} /><Button type="submit">Save profile</Button></form>
    </div></>;
}

export function AdminDashboardPage() {
  const query = useQuery({ queryKey: ["admin-dashboard"], queryFn: () => apiData<Record<string, number>>(api.get("/admin/dashboard")) });
  if (query.isPending) return <Loading />;
  if (query.error) return <QueryError error={query.error} />;
  return <><PageTitle eyebrow="Administrator" title="Academy overview" description="Current counts from the learning platform database." />
    <div className="stat-grid">{Object.entries(query.data).map(([label, value]) => <Stat key={label} label={label.replaceAll("_", " ")} value={value} />)}</div>
    <div className="callout"><h3>Content and access</h3><p>Manage courses, publish learning content, respond to doubts, and grant course access from the workspace navigation.</p></div>
  </>;
}

const adminEndpoints: Record<string, { title: string; endpoint: string; description: string; fields: { name: string; label: string; type?: string; required?: boolean }[]; columns: string[] }> = {
  courses: { title: "Courses", endpoint: "/admin/courses", description: "Create courses and manage their publication details.", fields: [
    { name: "title", label: "Course title", required: true }, { name: "slug", label: "URL slug", required: true },
    { name: "description", label: "Description", type: "textarea" }, { name: "instructor_name", label: "Instructor" },
    { name: "level", label: "Level" }, { name: "duration_minutes", label: "Duration in minutes", type: "number" },
    { name: "price", label: "Price (optional)", type: "number" }, { name: "thumbnail_url", label: "Thumbnail URL (optional)" },
  ], columns: ["id", "title", "slug", "level", "status"] },
  modules: { title: "Modules", endpoint: "/admin/modules", description: "Add ordered modules to a course. Use the course ID from Courses.", fields: [
    { name: "course_id", label: "Course ID", required: true }, { name: "title", label: "Module title", required: true },
    { name: "description", label: "Description", type: "textarea" }, { name: "position", label: "Order", type: "number" },
  ], columns: ["id", "title", "course_id", "position", "status"] },
  topics: { title: "Topics", endpoint: "/admin/topics", description: "Add lesson topics to a module. YouTube videos can be linked by a valid watch/share/embed URL.", fields: [
    { name: "module_id", label: "Module ID", required: true }, { name: "title", label: "Topic title", required: true },
    { name: "description", label: "Description", type: "textarea" }, { name: "video_url", label: "YouTube URL" },
    { name: "position", label: "Order", type: "number" }, { name: "duration_minutes", label: "Duration in minutes", type: "number" },
    { name: "attempt_limit", label: "Quiz attempt limit (blank for unlimited)", type: "number" },
    { name: "passing_percentage", label: "Passing percentage", type: "number" },
  ], columns: ["id", "title", "module_id", "position", "status"] },
  resources: { title: "Study resources", endpoint: "/admin/resources", description: "Add a permitted external link to a published topic.", fields: [
    { name: "topic_id", label: "Topic ID", required: true }, { name: "title", label: "Resource title", required: true },
    { name: "description", label: "Description", type: "textarea" }, { name: "external_url", label: "HTTPS resource URL", required: true },
  ], columns: ["id", "title", "topic_id", "resource_type"] },
  questions: { title: "Questions", endpoint: "/admin/questions", description: "Create graded practice. Correct answers are returned only after allowed by quiz policy.", fields: [
    { name: "topic_id", label: "Topic ID", required: true }, { name: "prompt", label: "Question", required: true },
    { name: "options", label: "Options (comma separated)" }, { name: "correct_answer", label: "Correct answer", required: true },
    { name: "explanation", label: "Explanation", type: "textarea" }, { name: "marks", label: "Marks", type: "number" },
  ], columns: ["id", "prompt", "topic_id", "question_type", "marks"] },
  announcements: { title: "Announcements", endpoint: "/admin/announcements", description: "Publish an update for every student or target a specific course.", fields: [
    { name: "title", label: "Title", required: true }, { name: "message", label: "Message", type: "textarea", required: true },
    { name: "course_id", label: "Course ID (leave empty for everyone)" },
  ], columns: ["id", "title", "course_id", "status", "published_at"] },
};

export function AdminResourcePage({ resource }: { resource: string }) {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [editing, setEditing] = useState<Record<string, unknown> | null>(null);
  const config = adminEndpoints[resource];
  const listEndpoint = resource === "students" ? `/admin/students${search ? `?q=${encodeURIComponent(search)}` : ""}` :
    resource === "enrollments" ? "/admin/enrollments" : resource === "doubts" ? "/admin/doubts" :
      resource === "reports" ? "/admin/reports" : resource === "settings" ? null : config?.endpoint;
  const list = useQuery({ queryKey: ["admin-list", resource, search], queryFn: () => apiData<Record<string, unknown>[]>(api.get(listEndpoint!)), enabled: Boolean(listEndpoint) });
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(""); setNotice("");
    const values: Record<string, unknown> = Object.fromEntries(new FormData(event.currentTarget).entries());
    const save = (data: Record<string, unknown>) => editing
      ? api.patch(`${config!.endpoint}/${String(editing.id)}`, data)
      : api.post(config!.endpoint, data);
    try {
      if (resource === "enrollments") {
        values.status = "active";
        await apiData(api.post("/admin/enrollments", values));
      } else if (resource === "announcements") {
        if (values.course_id === "") values.course_id = null;
        await apiData(save(values));
      } else if (resource === "courses") {
        values.duration_minutes = Number(values.duration_minutes || 0);
        values.price = values.price === "" ? null : Number(values.price);
        values.thumbnail_url = values.thumbnail_url === "" ? null : values.thumbnail_url;
        await apiData(save(values));
      } else if (resource === "questions") {
        values.options = String(values.options || "").split(",").map((item) => item.trim()).filter(Boolean);
        values.marks = Number(values.marks || 1);
        await apiData(save(values));
      } else if (resource === "topics") {
        values.position = Number(values.position || 0);
        values.duration_minutes = Number(values.duration_minutes || 0);
        if (values.attempt_limit === "") delete values.attempt_limit;
        else values.attempt_limit = Number(values.attempt_limit);
        values.passing_percentage = Number(values.passing_percentage || 0);
        values.results_visible = values.results_visible !== "false";
        values.answers_visible = values.answers_visible === "true";
        values.explanations_visible = values.explanations_visible === "true";
        values.doubts_enabled = values.doubts_enabled !== "false";
        await apiData(save(values));
      } else if (resource === "modules") {
        values.position = Number(values.position || 0);
        await apiData(save(values));
      } else {
        await apiData(save(values));
      }
      setNotice(editing ? "Changes saved." : "Saved successfully.");
      setEditing(null);
      event.currentTarget.reset();
      await queryClient.invalidateQueries({ queryKey: ["admin-list", resource] });
      if (resource === "courses") await queryClient.invalidateQueries({ queryKey: ["admin-dashboard"] });
    } catch (reason) { setError(errorMessage(reason)); }
  };
  const toggleRecord = async (item: Record<string, unknown>) => {
    setError(""); setNotice("");
    try {
      if (resource === "students") {
        const active = item.is_active === true;
        await apiData(api.patch(`/admin/students/${String(item.id)}/status`, null, { params: { is_active: !active } }));
      } else if (resource === "enrollments") {
        const status = item.status === "active" ? "revoked" : "active";
        await apiData(api.patch(`/admin/enrollments/${String(item.id)}`, null, { params: { status } }));
      } else if (resource === "courses") {
        const status = item.status === "published" ? "archived" : "published";
        await apiData(api.patch(`/admin/courses/${String(item.id)}`, { ...item, status }));
      } else if (resource === "resources") {
        await apiData(api.patch(`/admin/resources/${String(item.id)}`, { ...item, is_published: item.is_published !== true }));
      } else if (resource === "questions") {
        await apiData(api.patch(`/admin/questions/${String(item.id)}`, { ...item, is_published: item.is_published !== true }));
      }
      await queryClient.invalidateQueries({ queryKey: ["admin-list", resource] });
      if (resource === "courses" || resource === "students" || resource === "enrollments") {
        await queryClient.invalidateQueries({ queryKey: ["admin-dashboard"] });
      }
    } catch (reason) { setError(errorMessage(reason)); }
  };
  const editValues: Record<string, unknown> = editing ? {
    ...editing,
    video_url: resource === "topics" && editing.video_ref
      ? `https://www.youtube.com/watch?v=${String(editing.video_ref)}` : "",
    options: resource === "questions" && Array.isArray(editing.options) ? editing.options.join(", ") : editing.options,
    course_id: editing.course_id || "",
  } : {};
  if (resource === "settings") return <><PageTitle eyebrow="Configuration" title="Settings" description="Platform configuration guidance." /><div className="callout"><h3>Authentication and storage</h3><p>Configure Supabase Auth and production origins through deployment environment settings. File uploads are not enabled until a private object-storage provider is configured. Never place service-role keys in the frontend.</p></div></>;
  const columns = resource === "enrollments" ? ["id", "student_id", "student_email", "course_id", "course_title", "status", "expires_at"] :
    resource === "students" ? ["id", "full_name", "email", "is_active", "created_at"] :
      resource === "doubts" ? ["student_name", "topic_title", "message", "status"] :
        resource === "reports" ? ["course_title", "topic_count", "active_enrollments", "completion_percent"] : config?.columns || [];
  return <>
    <PageTitle eyebrow="Administrator" title={resource === "reports" ? "Reports" : config?.title || resource}
      description={resource === "reports" ? "Course structure summary from database records." : config?.description || "Review and manage platform records."} />
    {config && <section className="panel"><h2>{editing ? `Edit ${config.title.slice(0, -1)}` : `Add ${config.title.slice(0, -1)}`}</h2>
      {error && <Notice tone="error">{error}</Notice>}{notice && <Notice tone="success">{notice}</Notice>}
      <form key={String(editing?.id || "new-record")} className="form-stack" onSubmit={(event) => { void submit(event); }}>
        {config.fields.map((field) => field.type === "textarea" ?
          <TextArea key={field.name} name={field.name} label={field.label} required={field.required}
            defaultValue={String(editValues[field.name] ?? "")} /> :
          <Field key={field.name} name={field.name} label={field.label} required={field.required}
            defaultValue={String(editValues[field.name] ?? (field.name === "passing_percentage" ? 0 : field.name === "marks" ? 1 : ""))}
            type={field.type || "text"} min={field.type === "number" ? 0 : undefined} />)}
        {resource === "courses" && <>
          <label className="field"><span>Publication status</span><select className="input" name="status" defaultValue={String(editValues.status || "draft")}><option value="draft">Save as draft</option><option value="published">Publish</option><option value="archived">Archive</option></select></label>
          <label className="field"><span>Visible in public catalog</span><select className="input" name="is_public" defaultValue={String(editValues.is_public ?? true)}><option value="true">Yes</option><option value="false">No</option></select></label>
        </>}
        {resource === "modules" && <label className="field"><span>Publication status</span><select className="input" name="status" defaultValue={String(editValues.status || "draft")}><option value="draft">Draft</option><option value="published">Published</option></select></label>}
        {resource === "topics" && <label className="field"><span>Publication status</span><select className="input" name="status" defaultValue={String(editValues.status || "draft")}><option value="draft">Draft</option><option value="published">Published</option></select></label>}
        {resource === "topics" && <>
          <label className="field"><span>Doubt section</span><select className="input" name="doubts_enabled" defaultValue={String(editValues.doubts_enabled ?? true)}><option value="true">Enabled</option><option value="false">Disabled</option></select></label>
          <label className="field"><span>Show quiz results after submission</span><select className="input" name="results_visible" defaultValue={String(editValues.results_visible ?? true)}><option value="true">Yes</option><option value="false">No</option></select></label>
          <label className="field"><span>Reveal correct answers after submission</span><select className="input" name="answers_visible" defaultValue={String(editValues.answers_visible ?? false)}><option value="false">No</option><option value="true">Yes</option></select></label>
          <label className="field"><span>Reveal explanations after submission</span><select className="input" name="explanations_visible" defaultValue={String(editValues.explanations_visible ?? false)}><option value="false">No</option><option value="true">Yes</option></select></label>
        </>}
        {resource === "questions" && <label className="field"><span>Question type</span><select className="input" name="question_type" defaultValue={String(editValues.question_type || "multiple_choice")}>
          <option value="multiple_choice">Multiple choice</option><option value="true_false">True / false</option><option value="short_answer">Short answer</option>
        </select></label>}
        {resource === "questions" && <label className="field"><span>Published question</span><select className="input" name="is_published" defaultValue={String(editValues.is_published ?? true)}><option value="true">Yes</option><option value="false">No</option></select></label>}
        {resource === "resources" && <>
          <label className="field"><span>Resource type</span><select className="input" name="resource_type" defaultValue={String(editValues.resource_type || "link")}><option value="link">External link</option><option value="pdf">PDF</option><option value="document">Document</option><option value="archive">Archive</option></select></label>
          <label className="field"><span>Published resource</span><select className="input" name="is_published" defaultValue={String(editValues.is_published ?? true)}><option value="true">Yes</option><option value="false">No</option></select></label>
        </>}
        {resource === "announcements" && <label className="field"><span>Publication status</span><select className="input" name="status" defaultValue={String(editValues.status || "draft")}><option value="draft">Draft</option><option value="published">Publish now</option><option value="archived">Archive</option></select></label>}
        <div className="toolbar"><Button type="submit">Save</Button>{editing && <Button type="button" variant="quiet" onClick={() => setEditing(null)}>Cancel edit</Button>}</div>
      </form>
    </section>}
    {resource === "students" && <div className="toolbar" style={{ margin: "18px 0" }}><input className="input" aria-label="Search students" placeholder="Search name or email" value={search} onChange={(event) => setSearch(event.target.value)} /></div>}
    {resource === "enrollments" && <section className="panel"><h2>Grant course access</h2>{error && <Notice tone="error">{error}</Notice>}
      <form className="inline-form" onSubmit={(event) => { void submit(event); }}><Field label="Student profile ID" name="student_id" required /><Field label="Course ID" name="course_id" required /><Button type="submit">Grant enrollment</Button></form>
    </section>}
    {resource === "doubts" && list.data && <DoubtAdminList doubts={list.data as unknown as Doubt[]} />}
    {listEndpoint && resource !== "doubts" && <section className="panel"><h2>{resource === "reports" ? "Course summary" : "Records"}</h2>
      {list.isPending ? <Loading /> : list.error ? <QueryError error={list.error} /> : list.data?.length ? <div className="table-wrap"><table><thead><tr>{columns.map((column) => <th key={column}>{column.replaceAll("_", " ")}</th>)}
        {["students", "enrollments", "courses", "modules", "topics", "resources", "questions", "announcements"].includes(resource) && <th>Actions</th>}</tr></thead>
        <tbody>{list.data.map((item, index) => <tr key={String(item.id || index)}>{columns.map((column) =>
          <td key={column}>{column === "status" ? <span className="badge">{String(item[column] ?? "—")}</span> :
            typeof item[column] === "boolean" ? (item[column] ? "Yes" : "No") :
              String(item[column] ?? "—")}</td>)}
          {["students", "enrollments", "courses", "modules", "topics", "resources", "questions", "announcements"].includes(resource) &&
            <td><div className="toolbar">{config && <Button variant="quiet" onClick={() => { setError(""); setEditing(item); }}>Edit</Button>}
            {["students", "enrollments", "courses", "resources", "questions"].includes(resource) && <Button variant="quiet" onClick={() => void toggleRecord(item)}>
              {resource === "students" ? (item.is_active ? "Suspend" : "Reactivate") :
                resource === "enrollments" ? (item.status === "active" ? "Revoke" : "Reactivate") :
                  resource === "courses" ? (item.status === "published" ? "Archive" : "Publish") :
                    item.is_published ? "Unpublish" : "Publish"}
            </Button>}</div></td>}
        </tr>)}</tbody></table></div> :
        <EmptyState title="No records to show" description="Records appear here as the academy adds and manages learning content." />}
    </section>}
  </>;
}

function DoubtAdminList({ doubts }: { doubts: Doubt[] }) {
  const queryClient = useQueryClient();
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const reply = async (doubtId: string) => {
    setError("");
    try {
      await apiData(api.post(`/admin/doubts/${doubtId}/replies`, { message: drafts[doubtId] }));
      setDrafts((current) => ({ ...current, [doubtId]: "" }));
      await queryClient.invalidateQueries({ queryKey: ["admin-list", "doubts"] });
    } catch (reason) { setError(errorMessage(reason)); }
  };
  return <section className="panel"><h2>Student doubts</h2>{error && <Notice tone="error">{error}</Notice>}
    {doubts.length ? <div className="content-list">{doubts.map((doubt) => <article className="content-item" key={doubt.id}>
      <div className="toolbar" style={{ justifyContent: "space-between" }}><h3>{doubt.topic_title} · {doubt.student_name}</h3><span className="badge">{doubt.status}</span></div>
      <p>{doubt.message}</p>{doubt.replies.map((reply) => <div className="callout" key={reply.id}><b>{reply.author_name}</b><p>{reply.message}</p></div>)}
      <div className="inline-form" style={{ marginTop: 12 }}><Field label="Reply" value={drafts[doubt.id] || ""} onChange={(event) => setDrafts((current) => ({ ...current, [doubt.id]: event.target.value }))} />
        <Button onClick={() => void reply(doubt.id)} disabled={!drafts[doubt.id]?.trim()}>Reply</Button>
        <Button variant="secondary" onClick={async () => { await apiData(api.patch(`/admin/doubts/${doubt.id}/status?status=resolved`)); await queryClient.invalidateQueries({ queryKey: ["admin-list", "doubts"] }); }}>Resolve</Button>
      </div>
    </article>)}</div> : <EmptyState title="No doubts yet" description="Student questions will appear here." />}
  </section>;
}

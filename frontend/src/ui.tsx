import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import type * as React from "react";
import { Link, Navigate, NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  ArrowRight, Bell, BookOpen, ChevronDown, GraduationCap, LayoutDashboard, LogOut,
  Menu, MessageCircle, X,
} from "lucide-react";
import { useAuth } from "./auth";

export function Button({
  children, variant = "primary", className = "", ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "quiet" }) {
  return <button className={`button button-${variant} ${className}`} {...props}>{children}</button>;
}

export function PageTitle({ eyebrow, title, description, action }: {
  eyebrow?: string; title: string; description?: string; action?: ReactNode;
}) {
  return <div className="page-title"><div>{eyebrow && <span className="eyebrow">{eyebrow}</span>}
    <h1>{title}</h1>{description && <p>{description}</p>}</div>{action}</div>;
}

export function Notice({ children, tone = "info" }: { children: ReactNode; tone?: "info" | "error" | "success" }) {
  return <div role={tone === "error" ? "alert" : "status"} className={`notice notice-${tone}`}>{children}</div>;
}

export function Loading() { return <div className="loading" role="status">Loading your learning space…</div>; }

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <div className="empty-state"><div className="empty-icon"><BookOpen size={24} /></div><h3>{title}</h3><p>{description}</p>{action}</div>;
}

export function Field({ label, error, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string }) {
  return <label className="field"><span>{label}</span><input {...props} />{error && <small className="field-error">{error}</small>}</label>;
}

export function TextArea({ label, ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string }) {
  return <label className="field"><span>{label}</span><textarea rows={4} {...props} /></label>;
}

export function PublicLayout() {
  const { session, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const onSignOut = async () => { await signOut(); navigate("/"); };
  return <>
    <header className="site-header">
      <div className="container nav-wrap">
        <Link to="/" className="brand"><span className="brand-mark"><GraduationCap size={21} /></span>
          <span>Shahil <b>Academy</b></span></Link>
        <button className="mobile-menu" aria-label={open ? "Close menu" : "Open menu"} onClick={() => setOpen(!open)}>
          {open ? <X /> : <Menu />}
        </button>
        <nav className={`public-nav ${open ? "nav-open" : ""}`}>
          <NavLink to="/courses" onClick={() => setOpen(false)}>Courses</NavLink>
          <NavLink to="/about" onClick={() => setOpen(false)}>About</NavLink>
          <NavLink to="/contact" onClick={() => setOpen(false)}>Contact</NavLink>
          {session ? <>
            <Link className="nav-login" to="/student/dashboard">My learning</Link>
            <Button variant="quiet" onClick={onSignOut}>Sign out</Button>
          </> : <><Link className="nav-login" to="/login">Log in</Link><Link className="button button-primary" to="/register">Get started <ArrowRight size={15} /></Link></>}
        </nav>
      </div>
    </header>
    <main><Outlet /></main>
    <footer className="site-footer">
      <div className="container footer-grid">
        <div><Link to="/" className="brand footer-brand"><span className="brand-mark"><GraduationCap size={20} /></span><span>Shahil <b>Academy</b></span></Link>
          <p>Thoughtful learning, one step at a time.</p></div>
        <div className="footer-links"><Link to="/privacy">Privacy</Link><Link to="/terms">Terms</Link><Link to="/contact">Support</Link></div>
        <small>© {new Date().getFullYear()} Shahil Academy</small>
      </div>
    </footer>
  </>;
}

const studentNav = [
  ["/student/dashboard", "Overview", LayoutDashboard],
  ["/student/courses", "My courses", BookOpen],
  ["/student/doubts", "My doubts", MessageCircle],
  ["/student/announcements", "Announcements", Bell],
  ["/student/profile", "Profile", GraduationCap],
] as const;

const adminNav = [
  ["/admin/dashboard", "Overview", LayoutDashboard],
  ["/admin/courses", "Courses", BookOpen],
  ["/admin/modules", "Modules", ChevronDown],
  ["/admin/topics", "Topics", BookOpen],
  ["/admin/resources", "Resources", BookOpen],
  ["/admin/questions", "Questions", BookOpen],
  ["/admin/students", "Students", GraduationCap],
  ["/admin/enrollments", "Enrollments", GraduationCap],
  ["/admin/doubts", "Doubts", MessageCircle],
  ["/admin/announcements", "Announcements", Bell],
  ["/admin/reports", "Reports", LayoutDashboard],
  ["/admin/settings", "Settings", LayoutDashboard],
] as const;

function PortalLayout({ admin }: { admin: boolean }) {
  const { profile, signOut } = useAuth();
  const [mobile, setMobile] = useState(false);
  const navigate = useNavigate();
  const items = admin ? adminNav : studentNav;
  const logout = async () => { await signOut(); navigate("/login"); };
  return <div className="portal">
    <aside className={`sidebar ${mobile ? "sidebar-open" : ""}`}>
      <Link to={admin ? "/admin/dashboard" : "/student/dashboard"} className="brand sidebar-brand">
        <span className="brand-mark"><GraduationCap size={21} /></span><span>Shahil <b>Academy</b></span>
      </Link>
      <div className="side-label">{admin ? "Workspace" : "Learning space"}</div>
      <nav className="side-nav">{items.map(([to, label, Icon]) =>
        <NavLink key={to} to={to} end={to.endsWith("dashboard")} onClick={() => setMobile(false)}>
          <Icon size={18} /><span>{label}</span>
        </NavLink>)}</nav>
      <div className="sidebar-bottom">
        <div className="profile-mini"><span className="avatar">{(profile?.full_name || profile?.email || "S").slice(0, 1).toUpperCase()}</span>
          <span><b>{profile?.full_name || (admin ? "Administrator" : "Student")}</b><small>{profile?.email}</small></span>
        </div>
        <button className="signout-link" onClick={logout}><LogOut size={17} /> Sign out</button>
      </div>
    </aside>
    {mobile && <button className="sidebar-scrim" aria-label="Close navigation" onClick={() => setMobile(false)} />}
    <section className="portal-main">
      <header className="portal-topbar">
        <button className="mobile-menu portal-menu" aria-label="Open navigation" onClick={() => setMobile(true)}><Menu /></button>
        <span>{admin ? "Admin workspace" : "Your learning space"}</span>
        <div className="topbar-user"><span className="avatar">{(profile?.full_name || profile?.email || "S").slice(0, 1).toUpperCase()}</span>
          <b>{profile?.full_name || "Welcome"}</b></div>
      </header>
      <main className="portal-content"><Outlet /></main>
    </section>
  </div>;
}

export function StudentLayout() { return <PortalLayout admin={false} />; }
export function AdminLayout() { return <PortalLayout admin />; }

export function AuthGuard({ role }: { role: "student" | "admin" }) {
  const { session, profile, loading, configured, refreshProfile } = useAuth();
  const [error, setError] = useState("");
  const [checking, setChecking] = useState(false);
  useEffect(() => {
    if (session && !profile && !checking) {
      setChecking(true);
      refreshProfile()
        .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Could not load your account."))
        .finally(() => setChecking(false));
    }
  }, [session, profile, checking, refreshProfile]);
  if (loading) return <Loading />;
  if (!configured) return <div className="container narrow-page"><Notice tone="error">Authentication is not configured yet. Add the Supabase URL and anon key to <code>frontend/.env</code>.</Notice></div>;
  if (!session) return <NavigateToLogin />;
  if (error) return <div className="container narrow-page"><Notice tone="error">{error}</Notice></div>;
  if (!profile) return <Loading />;
  if (profile.role !== role) return <NavigateToHome />;
  return <Outlet />;
}

function NavigateToLogin() { return <Navigate to="/login" replace />; }
function NavigateToHome() { return <Navigate to="/" replace />; }

export function FormShell({ title, description, children, onSubmit }: {
  title: string; description: string; children: ReactNode; onSubmit: (event: FormEvent) => void;
}) {
  return <div className="auth-page"><div className="auth-card">
    <Link to="/" className="brand auth-brand"><span className="brand-mark"><GraduationCap size={21} /></span><span>Shahil <b>Academy</b></span></Link>
    <h1>{title}</h1><p className="auth-description">{description}</p><form onSubmit={onSubmit} className="form-stack">{children}</form>
  </div></div>;
}

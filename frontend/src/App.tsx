import { Navigate, Route, Routes } from "react-router-dom";
import { AdminLayout, AuthGuard, PublicLayout, StudentLayout } from "./ui";
import {
  AdminDashboardPage, AdminResourcePage, AuthPage, CatalogPage, HomePage, InfoPage,
  LessonPage, PublicCoursePage, ResetPasswordPage, StudentAnnouncementsPage,
  StudentCoursePage, StudentCoursesPage, StudentDashboardPage, StudentDoubtsPage,
  StudentProfilePage,
} from "./pages";

function NotFound() {
  return <div className="container text-page"><span className="eyebrow">404</span><h1>We couldn’t find that page</h1>
    <p>It may have moved or the link may be incorrect.</p><a className="button button-primary" href="/">Return home</a></div>;
}

export default function App() {
  return <Routes>
    <Route element={<PublicLayout />}>
      <Route index element={<HomePage />} />
      <Route path="courses" element={<CatalogPage />} />
      <Route path="courses/:slug" element={<PublicCoursePage />} />
      <Route path="about" element={<InfoPage page="about" />} />
      <Route path="contact" element={<InfoPage page="contact" />} />
      <Route path="privacy" element={<InfoPage page="privacy" />} />
      <Route path="terms" element={<InfoPage page="terms" />} />
      <Route path="login" element={<AuthPage mode="login" />} />
      <Route path="register" element={<AuthPage mode="register" />} />
      <Route path="forgot-password" element={<AuthPage mode="forgot" />} />
      <Route path="reset-password" element={<ResetPasswordPage />} />
      <Route path="*" element={<NotFound />} />
    </Route>
    <Route element={<AuthGuard role="student" />}>
      <Route path="/student" element={<StudentLayout />}>
        <Route index element={<Navigate to="/student/dashboard" replace />} />
        <Route path="dashboard" element={<StudentDashboardPage />} />
        <Route path="courses" element={<StudentCoursesPage />} />
        <Route path="courses/:courseId" element={<StudentCoursePage />} />
        <Route path="learn/:topicId" element={<LessonPage />} />
        <Route path="doubts" element={<StudentDoubtsPage />} />
        <Route path="announcements" element={<StudentAnnouncementsPage />} />
        <Route path="profile" element={<StudentProfilePage />} />
      </Route>
    </Route>
    <Route element={<AuthGuard role="admin" />}>
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<AdminDashboardPage />} />
        <Route path="courses" element={<AdminResourcePage resource="courses" />} />
        <Route path="modules" element={<AdminResourcePage resource="modules" />} />
        <Route path="topics" element={<AdminResourcePage resource="topics" />} />
        <Route path="resources" element={<AdminResourcePage resource="resources" />} />
        <Route path="questions" element={<AdminResourcePage resource="questions" />} />
        <Route path="students" element={<AdminResourcePage resource="students" />} />
        <Route path="enrollments" element={<AdminResourcePage resource="enrollments" />} />
        <Route path="doubts" element={<AdminResourcePage resource="doubts" />} />
        <Route path="announcements" element={<AdminResourcePage resource="announcements" />} />
        <Route path="reports" element={<AdminResourcePage resource="reports" />} />
        <Route path="settings" element={<AdminResourcePage resource="settings" />} />
      </Route>
    </Route>
    <Route path="*" element={<NotFound />} />
  </Routes>;
}


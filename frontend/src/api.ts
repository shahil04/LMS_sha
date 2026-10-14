import axios from "axios";
import { getAccessToken } from "./auth-token";

export const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function apiData<T>(request: Promise<{ data: T }>): Promise<T> {
  const response = await request;
  return response.data;
}

export function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((item: unknown) => {
        if (!item || typeof item !== "object") return String(item);
        const issue = item as { loc?: unknown[]; msg?: unknown };
        const field = Array.isArray(issue.loc) ? issue.loc.slice(1).join(".") : "";
        const message = typeof issue.msg === "string" ? issue.msg : "Invalid value";
        return field ? `${field}: ${message}` : message;
      }).join("; ");
    }
    return error.message;
  }
  return error instanceof Error ? error.message : "Something went wrong.";
}

export type Course = {
  id: string; title: string; slug: string; description: string; thumbnail_url?: string | null;
  instructor_name: string; level: string; duration_minutes: number; price?: number | null;
  progress_percent?: number; topic_count?: number; completed_topics?: number;
  modules?: Module[];
};
export type Module = { id: string; course_id: string; title: string; description: string; position: number; topics: Topic[] };
export type Topic = {
  id: string; module_id: string; title: string; description: string; position: number;
  duration_minutes: number; is_complete?: boolean; video_provider?: string | null;
  video_ref?: string | null; doubts_enabled?: boolean;
};
export type UserProfile = { id: string; email: string; full_name: string; role: "student" | "admin"; is_active: boolean };
export type Doubt = {
  id: string; topic_id: string; topic_title?: string; student_name?: string; student_id: string;
  message: string; status: string; created_at: string;
  replies: { id: string; author_name: string; message: string; created_at: string }[];
};

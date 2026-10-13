import { createClient, type Session, type SupabaseClient } from "@supabase/supabase-js";
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, apiData, type UserProfile } from "./api";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
export const supabase: SupabaseClient | null =
  supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

type AuthValue = {
  session: Session | null;
  profile: UserProfile | null;
  loading: boolean;
  configured: boolean;
  refreshProfile: () => Promise<UserProfile | null>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshProfile = async () => {
    if (!supabase) return null;
    const current = await supabase.auth.getSession();
    if (!current.data.session) {
      setProfile(null);
      return null;
    }
    const result = await apiData<UserProfile>(api.get("/auth/me"));
    setProfile(result);
    return result;
  };

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }
    supabase.auth.getSession().then(async ({ data }) => {
      setSession(data.session);
      if (data.session) {
        try {
          const result = await apiData<UserProfile>(api.get("/auth/me"));
          setProfile(result);
        } catch {
          setProfile(null);
        }
      }
      setLoading(false);
    });
    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      if (!nextSession) setProfile(null);
    });
    return () => listener.subscription.unsubscribe();
  }, []);

  const value = useMemo<AuthValue>(() => ({
    session, profile, loading, configured: Boolean(supabase), refreshProfile,
    signOut: async () => {
      if (!supabase) return;
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      setProfile(null);
    },
  }), [session, profile, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}

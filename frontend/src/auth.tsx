import axios from "axios";
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, apiData, type UserProfile } from "./api";
import { clearAccessToken, getAccessToken, setAccessToken } from "./auth-token";

type Session = { access_token: string };
type AuthResponse = { access_token: string; profile: UserProfile };

type AuthValue = {
  session: Session | null;
  profile: UserProfile | null;
  loading: boolean;
  configured: boolean;
  refreshProfile: () => Promise<UserProfile | null>;
  signIn: (email: string, password: string) => Promise<UserProfile>;
  register: (fullName: string, email: string, password: string) => Promise<UserProfile>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshProfile = useCallback(async () => {
    if (!getAccessToken()) {
      setProfile(null);
      return null;
    }
    try {
      const result = await apiData<UserProfile>(api.get("/auth/me"));
      setProfile(result);
      return result;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        clearAccessToken();
        setSession(null);
        setProfile(null);
      }
      throw error;
    }
  }, []);

  const acceptAuthResponse = useCallback((result: AuthResponse) => {
    setAccessToken(result.access_token);
    setSession({ access_token: result.access_token });
    setProfile(result.profile);
    return result.profile;
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const result = await apiData<AuthResponse>(api.post("/auth/login", { email, password }));
    return acceptAuthResponse(result);
  }, [acceptAuthResponse]);

  const register = useCallback(async (fullName: string, email: string, password: string) => {
    const result = await apiData<AuthResponse>(api.post("/auth/register", {
      full_name: fullName, email, password,
    }));
    return acceptAuthResponse(result);
  }, [acceptAuthResponse]);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    setSession({ access_token: token });
    refreshProfile()
      .catch(() => undefined)
      .finally(() => {
        setLoading(false);
      });
  }, [refreshProfile]);

  const value = useMemo<AuthValue>(() => ({
    session, profile, loading, configured: true, refreshProfile, signIn, register,
    signOut: async () => {
      clearAccessToken();
      setSession(null);
      setProfile(null);
    },
  }), [session, profile, loading, refreshProfile, signIn, register]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}

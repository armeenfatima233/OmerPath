import { createContext, useCallback, useContext, useRef, useState } from "react";
import { apiFetch } from "@/lib/api";

export type AuthUser = {
  user_id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  nationality: string | null;
  country_of_residence: string | null;
};

type AuthStatus = "idle" | "checking" | "authenticated" | "unauthenticated";

type AuthContextValue = {
  user: AuthUser | null;
  status: AuthStatus;
  checkAuth: (force?: boolean) => Promise<AuthUser | null>;
  setAuthenticatedUser: (user: AuthUser) => void;
  clearAuth: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState<AuthStatus>("idle");
  const pendingCheck = useRef<Promise<AuthUser | null> | null>(null);

  const checkAuth = useCallback(async (force = false) => {
    if (!force && user) return user;
    if (pendingCheck.current) return pendingCheck.current;

    setStatus("checking");
    const request = (async () => {
      try {
        const response = await apiFetch("/api/auth/me");
        if (!response.ok) throw new Error("Not authenticated");
        const currentUser: AuthUser = await response.json();
        setUser(currentUser);
        setStatus("authenticated");
        return currentUser;
      } catch {
        setUser(null);
        setStatus("unauthenticated");
        return null;
      } finally {
        pendingCheck.current = null;
      }
    })();
    pendingCheck.current = request;
    return request;
  }, [user]);

  return <AuthContext.Provider value={{
    user,
    status,
    checkAuth,
    setAuthenticatedUser: (nextUser) => {
      setUser(nextUser);
      setStatus("authenticated");
    },
    clearAuth: () => {
      setUser(null);
      setStatus("unauthenticated");
    },
  }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}


import { useEffect } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/contexts/AuthContext";

export default function RequireAuth({ children }: { children: React.ReactNode }) {
  const [, navigate] = useLocation();
  const { status, checkAuth } = useAuth();

  useEffect(() => {
    if (status === "idle") void checkAuth();
  }, [status, checkAuth]);

  useEffect(() => {
    if (status === "unauthenticated") {
      navigate("/login");
    }
  }, [status, navigate]);

  if (status !== "authenticated") {
    return <div role="status" aria-live="polite">Loading...</div>;
  }

  return <>{children}</>;
}

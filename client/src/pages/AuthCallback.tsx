import { useEffect, useState } from "react";
import { Link, useLocation } from "wouter";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function AuthCallback() {
  const [, navigate] = useLocation();
  const { checkAuth } = useAuth();
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function completeAuthentication() {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code");
      const flow = params.get("flow");
      if (!code) {
        setError(true);
        return;
      }
      try {
        const response = await apiFetch("/api/auth/exchange-code", {
          method: "POST",
          body: JSON.stringify({ code }),
        });
        if (!response.ok) throw new Error("Unable to complete authentication");
        await checkAuth(true);
        if (!cancelled) navigate(flow === "recovery" ? "/reset-password" : "/onboarding");
      } catch {
        if (!cancelled) setError(true);
      }
    }
    void completeAuthentication();
    return () => { cancelled = true; };
  }, [checkAuth, navigate]);

  return <main className="auth-shell">
    <section className="auth-form-wrap min-h-screen">
      <div className="auth-form-card">
        <div className="eyebrow">Account verification</div>
        <h2>{error ? "This link could not be completed." : "Confirming your account…"}</h2>
        <p className="auth-subcopy">{error ? "The link may have expired or already been used. Please request a new link and try again." : "Please wait while OmerPath securely finishes the process."}</p>
        {error && <Link href="/login" className="button-primary auth-submit">Return to login</Link>}
      </div>
    </section>
  </main>;
}


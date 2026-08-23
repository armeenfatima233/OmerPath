import { useState } from "react";
import { ArrowLeft, ArrowRight, CheckCircle2, Eye, EyeOff, LockKeyhole, ShieldCheck, Sparkles } from "lucide-react";
import { Link, useLocation } from "wouter";
import { ASSETS, BRAND } from "@/lib/brand";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function Auth({ mode }: { mode: "login" | "signup" | "forgot" | "reset" }) {
  const [, navigate] = useLocation();
  const { checkAuth, clearAuth } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(() => mode === "login" && new URLSearchParams(window.location.search).get("password_reset") === "1" ? "Your password was updated. You can now sign in." : null);
  const [signupComplete, setSignupComplete] = useState(false);
  const isSignup = mode === "signup";
  const isForgot = mode === "forgot";
  const isReset = mode === "reset";

  async function submit(event: React.FormEvent) {
    event.preventDefault();

    setError(null);
    setMessage(null);

    const trimmedEmail = email.trim();
    const trimmedFirstName = firstName.trim();
    const trimmedLastName = lastName.trim();
    if (isSignup && (!trimmedFirstName || !trimmedLastName || !trimmedEmail || !password)) {
      setError("Please complete all fields.");
      return;
    }
    if (isForgot && !trimmedEmail) {
      setError("Please enter your email address.");
      return;
    }
    if (isReset && (!password || !confirmPassword)) {
      setError("Please enter and confirm your new password.");
      return;
    }
    if (isReset && password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }
    if (!isSignup && !isForgot && !isReset && (!trimmedEmail || !password)) {
      setError("Please enter both email and password.");
      return;
    }

    setSubmitting(true);
    try {
      if (isForgot) {
        const response = await apiFetch("/api/auth/forgot-password", {
          method: "POST",
          body: JSON.stringify({ email: trimmedEmail }),
        });
        if (!response.ok) {
          setError("Unable to send a reset email. Please try again.");
          return;
        }
        setMessage("If an account exists for that email, a password-reset link has been sent.");
        return;
      }

      if (isReset) {
        const response = await apiFetch("/api/auth/update-password", {
          method: "POST",
          body: JSON.stringify({ password }),
        });
        if (!response.ok) {
          setError("Unable to update your password. Please request a new reset link.");
          return;
        }
        await apiFetch("/api/auth/logout", { method: "POST" });
        clearAuth();
        navigate("/login?password_reset=1");
        return;
      }

      if (isSignup) {
        const response = await apiFetch("/api/auth/signup", {
          method: "POST",
          body: JSON.stringify({
            first_name: trimmedFirstName,
            last_name: trimmedLastName,
            email: trimmedEmail,
            password,
          }),
        });

        if (!response.ok) {
          setError("Unable to create your account. Please try again.");
          return;
        }

        const result: { email_confirmation_required: boolean } = await response.json();
        if (result.email_confirmation_required) {
          setSignupComplete(true);
          return;
        }
        await checkAuth(true);
        navigate("/onboarding");
        return;
      }

      const response = await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: trimmedEmail, password, remember }),
      });

      if (!response.ok) {
        setError(response.status === 401 ? "Invalid email or password." : "Unable to sign in. Please try again.");
        return;
      }

      const currentUser = await checkAuth(true);
      if (!currentUser) {
        setError("Unable to load your account. Please try again.");
        return;
      }
      navigate("/dashboard");
    } catch {
      setError(isForgot ? "Unable to send a reset email. Please try again." : isReset ? "Unable to update your password." : "Unable to sign in. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return <main className="auth-shell">
    <section className="auth-visual" style={{ backgroundImage: `linear-gradient(180deg, rgba(9,18,23,.24), rgba(9,18,23,.88)), url(${ASSETS.publicHero})` }}>
      <Link href="/" className="auth-back"><ArrowLeft size={16}/> Back to OmerPath</Link>
      <div className="auth-visual-copy">
        <h1>{isSignup ? "Start with the story behind your goals." : "Welcome back to your scholarship path."}</h1>
        <p>Matches, documents, deadlines, and advisor guidance stay connected in one workspace.</p>
        <div className="auth-proof-grid">
          <div><ShieldCheck size={18}/><b>Verified sources</b><span>See where opportunity information comes from.</span></div>
          <div><Sparkles size={18}/><b>Personalized fit</b><span>Understand why a scholarship fits you.</span></div>
        </div>
      </div>
    </section>
    <section className="auth-form-wrap">
      <div className="auth-form-card">
        <Link href="/" className="landing-brand auth-logo"><img src={ASSETS.logo} alt=""/><span><b>{BRAND.name}</b><small>SCHOLARSHIP GUIDANCE</small></span></Link>
        <div className="eyebrow mt-10">{signupComplete ? "Account confirmation" : isSignup ? "Create your free profile" : isForgot ? "Password recovery" : isReset ? "Choose a new password" : "Student sign in"}</div>
        <h2>{signupComplete ? "Check your email" : isSignup ? "Build your OmerPath." : isForgot ? "Reset your password." : isReset ? "Secure your account." : "Continue where you left off."}</h2>
        <p className="auth-subcopy">{signupComplete ? `We sent a confirmation link to ${email.trim()}. Open it to finish creating your account.` : isForgot ? "Enter your account email and we’ll send you a secure reset link." : isReset ? "Enter a new password for your OmerPath account." : "Your scholarship workspace, in one place."}</p>
        {!signupComplete && <form onSubmit={submit} className="auth-form">
          {isSignup && <label><span>First name</span><input value={firstName} onChange={(e) => setFirstName(e.target.value)} required autoComplete="given-name"/></label>}
          {isSignup && <label><span>Last name</span><input value={lastName} onChange={(e) => setLastName(e.target.value)} required autoComplete="family-name"/></label>}
          {!isReset && <label><span>Email</span><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email"/></label>}
          {!isForgot && <label><span>{isReset ? "New password" : "Password"}</span><div className="password-field"><input type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} required minLength={isSignup || isReset ? 8 : 1} autoComplete={isSignup || isReset ? "new-password" : "current-password"}/><button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword((value) => !value)}>{showPassword ? <EyeOff size={17}/> : <Eye size={17}/>}</button></div></label>}
          {isReset && <label><span>Confirm new password</span><input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required minLength={8} autoComplete="new-password"/></label>}
          {mode === "login" && <div className="auth-inline"><label className="check-control"><input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)}/><span>Keep me signed in on this device</span></label><Link href="/forgot-password" className="text-button">Forgot password?</Link></div>}
          {error && <div className="auth-error" role="alert">{error}</div>}
          {message && <div className="auth-terms" role="status"><CheckCircle2 size={15}/>{message}</div>}
          <button className="button-primary auth-submit" type="submit" disabled={submitting}>{isSignup ? submitting ? "Creating profile..." : "Create my profile" : isForgot ? submitting ? "Sending..." : "Send reset link" : isReset ? submitting ? "Updating..." : "Update password" : submitting ? "Signing in..." : "Open my workspace"}<ArrowRight size={16}/></button>
        </form>}
        {isSignup && !signupComplete && <div className="auth-terms"><CheckCircle2 size={15}/> By continuing, you agree that scholarship details may change — always confirm official programme rules before applying.</div>}
        <div className="auth-switch">{signupComplete || isForgot || isReset ? <Link href="/login">Go to log in</Link> : <>{isSignup ? "Already have a profile?" : "New to OmerPath?"} <Link href={isSignup ? "/login" : "/signup"}>{isSignup ? "Log in" : "Create one"}</Link></>}</div>
      </div>
    </section>
  </main>;
}

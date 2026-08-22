import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation } from "wouter";
import {
  ArrowLeft, ArrowRight, Bell, BookOpenCheck, Bookmark, BookmarkCheck, Check, CheckCircle2,
  ChevronDown, ChevronRight, ClipboardCheck, Clock3, Compass, Download, ExternalLink,
  FileCheck2, FileText, Filter, GraduationCap, LayoutDashboard, Library, LockKeyhole, LogOut, MapPin, Menu,
  MoreHorizontal, Pencil, Plus, Search, Send, Settings2, ShieldCheck, SlidersHorizontal, Sparkles,
  Trash2, Upload, UserRound, X, AlertCircle, CalendarDays, Eye, Link2, Copy, RefreshCw, Target,
} from "lucide-react";
import { toast } from "sonner";
import { ASSETS, BRAND, NAV_ITEMS, SECONDARY_ITEMS, Scholarship } from "@/lib/brand";
import { apiFetch } from "@/lib/api";
import { AuthUser, useAuth } from "@/contexts/AuthContext";
import { useAcademicProfile } from "@/contexts/AcademicProfileContext";
import { useSavedScholarships } from "@/contexts/SavedScholarshipsContext";
import { useApplications } from "@/contexts/ApplicationsContext";
import { useDocuments } from "@/contexts/DocumentsContext";
import { useNotifications } from "@/contexts/NotificationsContext";
import { useSettings } from "@/contexts/SettingsContext";
import { useScholarships } from "@/lib/useScholarships";

const iconMap: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  LayoutDashboard, Compass, ClipboardCheck, BookOpenCheck, Sparkles, Library, Bell, UserRound, Settings2,
};

function getUserIdentity(user: AuthUser | null) {
  if (!user) return { name: "", initials: "", secondary: "" };
  const firstName = user.first_name?.trim() ?? "";
  const lastName = user.last_name?.trim() ?? "";
  return {
    name: [firstName, lastName].filter(Boolean).join(" "),
    initials: `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase(),
    secondary: user.country_of_residence?.trim() || user.nationality?.trim() || user.email,
  };
}

function Logo() {
  return <Link href="/dashboard" className="flex items-center gap-3 group focus-ring rounded-xl">
    <div className="size-10 rounded-[13px] bg-ink flex items-center justify-center overflow-hidden shadow-[0_8px_24px_rgba(20,33,38,.16)]"><img src={ASSETS.logo} className="size-7 object-contain" alt="" width="28" height="28"/></div>
    <div><div className="font-display text-xl leading-none tracking-[-.04em]">{BRAND.name}</div><div className="mt-1 text-[9px] uppercase tracking-[.19em] text-ink/45">Scholarship guidance</div></div>
  </Link>;
}

function Sidebar({ mobileOpen, close, user }: { mobileOpen: boolean; close: () => void; user: AuthUser | null }) {
  const [location, navigate] = useLocation();
  const { unreadCount: unread } = useNotifications();
  const isActive = (href: string) => href === "/dashboard" ? location === "/dashboard" : location.startsWith(href);
  const [signingOut, setSigningOut] = useState(false);
  const { clearAuth } = useAuth();
  const identity = getUserIdentity(user);
  async function signOut() {
    if (signingOut) return;
    setSigningOut(true);
    try {
      await apiFetch("/api/auth/logout", { method: "POST" });
    } catch {
      // Network failure: authentication state can no longer be trusted locally, so still sign the user out below.
    } finally {
      clearAuth();
      navigate("/login");
    }
  }
  return <aside aria-label="Workspace navigation" className={`fixed inset-y-0 left-0 z-50 w-[256px] border-r border-ink/10 bg-paper px-5 py-6 transition-transform duration-300 lg:translate-x-0 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
    <div className="flex h-full flex-col">
      <div className="flex items-start justify-between"><Logo/><button aria-label="Close navigation" onClick={close} className="icon-button lg:hidden"><X size={18}/></button></div>
      <div className="mt-10 text-[10px] font-semibold uppercase tracking-[.18em] text-ink/35">Workspace</div>
      <nav className="mt-3 space-y-1">{NAV_ITEMS.map((item) => { const Icon = iconMap[item.icon]; return <Link key={item.href} href={item.href} onClick={close} className={`nav-item focus-ring ${isActive(item.href) ? "nav-active" : ""}`}><Icon size={18}/><span>{item.label}</span></Link>; })}</nav>
      <div className="mt-7 text-[10px] font-semibold uppercase tracking-[.18em] text-ink/35">Account</div>
      <nav className="mt-3 space-y-1">{SECONDARY_ITEMS.map((item) => { const Icon = iconMap[item.icon]; return <Link key={item.href} href={item.href} onClick={close} className={`nav-item focus-ring ${isActive(item.href) ? "nav-active" : ""}`}><Icon size={18}/><span>{item.label}</span>{item.label === "Notifications" && unread > 0 && <span className="ml-auto flex min-w-5 h-5 items-center justify-center rounded-full bg-saffron px-1 text-[9px] font-bold text-paper">{unread}</span>}</Link>; })}<button className="nav-item focus-ring w-full" disabled={signingOut} onClick={signOut}><LogOut size={18}/><span>{signingOut ? "Signing out..." : "Sign out"}</span></button></nav>
      <div className="mt-auto flex items-center gap-3 border-t border-ink/10 pt-5"><div className="flex size-9 items-center justify-center rounded-full bg-sage text-sm font-bold text-ink">{identity.initials}</div><div className="min-w-0"><div className="truncate text-sm font-semibold">{identity.name}</div><div className="text-[11px] text-ink/45">{identity.secondary}</div></div><ChevronDown size={15} className="ml-auto text-ink/35"/></div>
    </div>
  </aside>;
}

function Header({ onMenu, user }: { onMenu: () => void; user: AuthUser | null }) {
  const [, navigate] = useLocation();
  const { unreadCount: unread } = useNotifications();
  const identity = getUserIdentity(user);
  return <header className="sticky top-0 z-30 flex h-[76px] items-center justify-between border-b border-ink/10 bg-paper/90 px-5 backdrop-blur-xl lg:px-10">
    <button aria-label="Open navigation" onClick={onMenu} className="icon-button lg:hidden"><Menu size={20}/></button>
    <div className="ml-auto flex items-center gap-3"><button aria-label={`${unread} unread notifications`} onClick={() => navigate("/dashboard/notifications")} className="icon-button relative"><Bell size={19}/>{unread > 0 && <span className="absolute right-2 top-2 size-1.5 rounded-full bg-saffron"/>}</button><div className="hidden h-7 w-px bg-ink/10 sm:block"/><button aria-label="Open profile" onClick={() => navigate("/dashboard/profile")} className="flex items-center gap-2 rounded-xl px-2 py-1.5 transition hover:bg-ink/5 focus-ring"><div className="flex size-8 items-center justify-center rounded-full bg-sage text-xs font-bold">{identity.initials}</div><ChevronDown size={15} className="text-ink/35"/></button></div>
  </header>;
}

function DemoBanner() {
  return <div className="demo-banner" role="note"><AlertCircle size={14}/><span>Verify eligibility and deadlines with the official source.</span></div>;
}

function PageTitle({ eyebrow, title, description, action }: { eyebrow: string; title: React.ReactNode; description?: string; action?: React.ReactNode }) {
  return <div className="page-title mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><div className="eyebrow signal-label">{eyebrow}</div><h1 className="mt-3 font-display text-[36px] leading-[.98] tracking-[-.055em] sm:text-[50px]">{title}</h1>{description && <p className="mt-3 max-w-2xl text-sm leading-relaxed text-ink/55">{description}</p>}</div>{action}</div>;
}

function StatCard({ label, value, detail, icon: Icon, accent = "saffron" }: { label: string; value: string | number; detail: string; icon: React.ComponentType<{size?:number}>; accent?: "saffron" | "sage" | "clay" }) {
  const tone = accent === "sage" ? "bg-sage/35" : accent === "clay" ? "bg-[#E8D7C8]" : "bg-saffron/15 text-saffron";
  return <div className="paper-card motion-card p-5"><div className="flex items-start justify-between"><div className={`flex size-9 items-center justify-center rounded-xl ${tone}`}><Icon size={17}/></div><span className="text-[9px] uppercase tracking-[.16em] text-ink/30">Live UI</span></div><div className="mt-6 font-display text-[32px] tracking-[-.04em]">{value}</div><div className="mt-1 text-xs font-semibold text-ink/55">{label}</div><div className="mt-3 text-[11px] text-ink/40">{detail}</div></div>;
}

function formatMatch(score: number | null): string {
  return score === null ? "Not enough data" : `${score}%`;
}

// Fit score and eligibility status measure different things: fit score reflects
// how well the criteria OmerPath can evaluate line up, while eligibility can
// still be unknown or ineligible even at a high fit score. This caption keeps
// the two from reading as the same claim without touching the score itself.
function eligibilityCaption(status: Scholarship["eligibilityStatus"]): string | null {
  if (status === "unknown") return "Eligibility unconfirmed";
  if (status === "ineligible") return "Not eligible";
  return null;
}

function detailFitScoreCaption(status: Scholarship["eligibilityStatus"]): string {
  if (status === "unknown") return "Based on criteria OmerPath can evaluate — eligibility unconfirmed";
  if (status === "ineligible") return "Based on criteria OmerPath can evaluate — not eligible";
  return "Based on your profile";
}

function MatchRing({ score }: { score: number | null }) {
  if (score === null) return <div className="relative size-[58px]" aria-label="Match not yet available"><svg viewBox="0 0 42 42" className="size-full -rotate-90" aria-hidden="true"><circle cx="21" cy="21" r="16" fill="none" stroke="currentColor" strokeWidth="4" className="text-ink/8"/></svg><span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-ink/35">—</span></div>;
  return <div className="relative size-[58px]" aria-label={`${score}% match`}><svg viewBox="0 0 42 42" className="size-full -rotate-90" aria-hidden="true"><circle cx="21" cy="21" r="16" fill="none" stroke="currentColor" strokeWidth="4" className="text-ink/8"/><circle cx="21" cy="21" r="16" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeDasharray={`${score} ${100 - score}`} pathLength="100" className="text-saffron"/></svg><span className="absolute inset-0 flex items-center justify-center text-[11px] font-bold">{score}%</span></div>;
}

function ScholarshipCard({ scholarship, compact = false }: { scholarship: Scholarship; compact?: boolean }) {
  const { saved, toggleSave } = useSavedScholarships();
  const isSaved = saved.includes(scholarship.id);
  return <article className={`paper-card motion-card group relative ${compact ? "p-4" : "p-5"}`}>
    <div className="flex items-start gap-4"><div className="flex size-11 shrink-0 items-center justify-center rounded-[14px] bg-ink text-paper"><GraduationCap size={20}/></div><div className="min-w-0 flex-1"><div className="flex items-start justify-between gap-3"><div><h3 className="font-display text-lg leading-tight tracking-[-.02em]">{scholarship.name}</h3><div className="mt-1 text-xs text-ink/45">{scholarship.provider}</div></div><button aria-label={isSaved ? `Remove ${scholarship.name} from saved` : `Save ${scholarship.name}`} onClick={() => { toggleSave(scholarship.id); toast(isSaved ? "Removed from saved scholarships" : "Saved to your shortlist"); }} className="icon-button">{isSaved ? <BookmarkCheck size={18} className="text-saffron"/> : <Bookmark size={18}/>}</button></div></div></div>
    <div className="mt-5 flex flex-wrap gap-2 text-[10px] font-semibold"><span className="chip"><MapPin size={11}/>{scholarship.country}</span><span className="chip"><GraduationCap size={11}/>{scholarship.degree}</span><span className="chip chip-sage">{scholarship.funding}</span></div>
    <div className="mt-5 flex items-end justify-between border-t border-ink/8 pt-4"><div><div className="text-[10px] uppercase tracking-[.15em] text-ink/35">Deadline</div><div className="mt-1 text-xs font-bold">{scholarship.deadline}</div></div><div className="flex items-center gap-3"><div className="text-right"><div className="text-[10px] uppercase tracking-[.15em] text-ink/35">Fit score</div><div className="mt-1 text-sm font-bold text-saffron">{formatMatch(scholarship.match)}</div>{eligibilityCaption(scholarship.eligibilityStatus) && <div className="text-[9px] font-semibold text-ink/40">{eligibilityCaption(scholarship.eligibilityStatus)}</div>}</div><MatchRing score={scholarship.match}/></div></div>
    <Link href={`/dashboard/scholarships/${scholarship.id}`} className="mt-4 flex items-center justify-between rounded-lg text-xs font-bold text-ink/65 transition group-hover:text-ink focus-ring">See why this fits your path <ArrowRight size={14} className="transition-transform group-hover:translate-x-1"/></Link>
  </article>;
}

function ActionItem({ icon: Icon, title, detail, href }: { icon: React.ComponentType<{size?:number}>; title: string; detail: string; href: string }) {
  return <Link href={href} className="flex items-center gap-3 rounded-2xl p-2 transition hover:bg-ink/[.035] focus-ring"><div className="flex size-9 items-center justify-center rounded-xl bg-saffron/15 text-saffron"><Icon size={16}/></div><div className="min-w-0 flex-1"><div className="text-xs font-bold">{title}</div><div className="mt-0.5 text-[10px] text-ink/42">{detail}</div></div><ChevronRight size={15} className="text-ink/25"/></Link>;
}

function Dashboard({ scholarships }: { scholarships: Scholarship[] }) {
  const { documents } = useDocuments();
  const { applications } = useApplications();
  const { saved } = useSavedScholarships();
  const readyDocs = Math.min(documents.length, PASSPORT_READINESS_TARGET);
  const next = scholarships.slice().sort((a,b) => (b.match ?? -1) - (a.match ?? -1))[0];
  return <>
    <PageTitle eyebrow="Overview" title={<>Your next<br/><em>strongest move.</em></>} description="A clear view of the scholarships, documents, and deadlines that matter most to your path." action={<Link href="/dashboard/profile" className="button-primary"><Pencil size={15}/> Complete profile <span className="rounded-full bg-paper/20 px-2 py-0.5 text-[10px]">82%</span></Link>}/>
    <div className="route-strip mb-8"><div className="route-stop"><span className="route-dot route-dot-live"/><span>Profile</span><b>82%</b></div><div className="route-track"/><div className="route-stop"><span className="route-dot"/><span>Matches</span><b>{scholarships.length} ranked</b></div><div className="route-track"/><div className="route-stop"><span className="route-dot"/><span>Applications</span><b>{applications.length} active</b></div></div>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><StatCard label="Strong matches" value={scholarships.filter((s) => (s.match ?? 0) >= 79).length} detail="79% match or higher" icon={Target}/><StatCard label="Saved" value={saved.length} detail="Shortlist saved locally" icon={BookmarkCheck} accent="sage"/><StatCard label="Applications" value={applications.length} detail="Across preparation stages" icon={ClipboardCheck} accent="clay"/><StatCard label="Passport readiness" value={`${readyDocs}/${PASSPORT_READINESS_TARGET}`} detail="Documents uploaded" icon={FileCheck2} accent="sage"/></div>
    <div className="mt-8 grid gap-6 xl:grid-cols-[1.25fr_.75fr]">
      <div className="paper-card overflow-hidden"><div className="relative min-h-[260px]"><img src={ASSETS.students} alt="International students on a university campus" loading="lazy" className="absolute inset-0 size-full object-cover"/><div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(20,33,38,.92),rgba(20,33,38,.22))]"/><div className="relative max-w-[560px] p-7 text-paper"><div className="eyebrow text-paper/55">Highest-leverage next step</div><h2 className="mt-4 font-display text-3xl leading-tight tracking-[-.04em]">Secure your recommendation letter before polishing another essay.</h2><p className="mt-3 max-w-md text-sm leading-relaxed text-paper/65">It unlocks two high-priority applications and is the only document you're missing.</p><Link href="/dashboard/passport" className="mt-6 button-primary bg-saffron">Open Passport <ArrowRight size={15}/></Link></div></div></div>
      <div className="paper-card p-6"><div className="flex items-center justify-between"><div><div className="eyebrow">Advisor brief</div><h2 className="mt-2 font-display text-2xl">What deserves attention now.</h2></div><Sparkles size={20} className="text-saffron"/></div><div className="mt-5 space-y-2"><ActionItem icon={FileText} title="Recommendation letter" detail="Needed for 2 top matches" href="/dashboard/passport"/>{next && next.match !== null && <ActionItem icon={GraduationCap} title={`${next.match}% match · ${next.name}`} detail="Review why the fit is strong" href={`/dashboard/scholarships/${next.id}`}/>}<ActionItem icon={ClipboardCheck} title="Erasmus application" detail="91% ready · final statement review" href="/dashboard/applications"/></div><Link href="/dashboard/advisor" className="mt-5 text-link">Ask Omer AI <ArrowRight size={14}/></Link></div>
    </div>
    <div className="mt-8"><div className="mb-4 flex items-end justify-between"><div><div className="eyebrow">Your strongest matches</div><h2 className="mt-2 font-display text-2xl">A shortlist with reasons.</h2></div><Link href="/dashboard/scholarships" className="text-link">View all <ArrowRight size={14}/></Link></div><div className="grid gap-4 xl:grid-cols-3">{scholarships.slice(0,3).map((scholarship) => <ScholarshipCard key={scholarship.id} scholarship={scholarship} compact/>)}</div></div>
  </>;
}

function Scholarships({ scholarships }: { scholarships: Scholarship[] }) {
  const { saved } = useSavedScholarships();
  const [query, setQuery] = useState("");
  const [country, setCountry] = useState("All");
  const [funding, setFunding] = useState("All");
  const [savedOnly, setSavedOnly] = useState(false);
  const [sort, setSort] = useState("match");
  const countries = ["All", ...Array.from(new Set(scholarships.map((s) => s.country)))];
  const filtered = useMemo(() => {
    const result = scholarships.filter((s) => `${s.name} ${s.provider} ${s.country} ${s.fields.join(" ")}`.toLowerCase().includes(query.toLowerCase()))
      .filter((s) => country === "All" || s.country === country)
      .filter((s) => funding === "All" || s.funding === funding)
      .filter((s) => !savedOnly || saved.includes(s.id));
    return result.sort((a,b) => sort === "match" ? (b.match ?? -1) - (a.match ?? -1) : a.name.localeCompare(b.name));
  }, [scholarships, query, country, funding, savedOnly, saved, sort]);
  return <>
    <PageTitle eyebrow="Opportunity library" title={<>Find the right<br/><em>fit faster.</em></>} description="Search and filter scholarships, then open any match to see eligibility, requirements, source status, and readiness." action={<Link href="/dashboard/advisor" className="button-secondary"><Sparkles size={15}/> Ask AI to narrow it down</Link>}/>
    <div className="paper-card p-4 sm:p-5"><div className="grid gap-3 lg:grid-cols-[1.5fr_repeat(3,minmax(140px,.5fr))]"><label className="search-field"><Search size={16}/><span className="sr-only">Search scholarships</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search scholarship, country, provider, field…"/></label><label className="select-field"><span className="sr-only">Country</span><MapPin size={15}/><select value={country} onChange={(e) => setCountry(e.target.value)}>{countries.map((value) => <option key={value}>{value}</option>)}</select></label><label className="select-field"><span className="sr-only">Funding</span><Filter size={15}/><select value={funding} onChange={(e) => setFunding(e.target.value)}><option>All</option><option>Fully Funded</option><option>Partially Funded</option></select></label><label className="select-field"><span className="sr-only">Sort scholarships</span><SlidersHorizontal size={15}/><select value={sort} onChange={(e) => setSort(e.target.value)}><option value="match">Best match</option><option value="name">A–Z</option></select></label></div><div className="mt-4 flex flex-wrap items-center justify-between gap-3"><button className={`filter-pill ${savedOnly ? "filter-pill-active" : ""}`} onClick={() => setSavedOnly((value) => !value)}><BookmarkCheck size={14}/> Saved only</button><span className="text-xs text-ink/45">{filtered.length} opportunities · ranked for {BRAND.student.name}</span></div></div>
    {filtered.length ? <div className="mt-6 grid gap-5 lg:grid-cols-2 2xl:grid-cols-3">{filtered.map((scholarship) => <ScholarshipCard key={scholarship.id} scholarship={scholarship}/>)}</div> : <div className="empty-state"><Search size={26}/><h2>No matches in this filter.</h2><p>Try a broader country or funding filter.</p><button className="button-secondary" onClick={() => { setQuery(""); setCountry("All"); setFunding("All"); setSavedOnly(false); }}>Clear filters</button></div>}
  </>;
}

function ScholarshipDetail({ id, scholarships }: { id: string; scholarships: Scholarship[] }) {
  const [, navigate] = useLocation();
  const scholarship = scholarships.find((item) => item.id === id);
  const { applications, startApplication } = useApplications();
  const { saved, toggleSave } = useSavedScholarships();
  const [starting, setStarting] = useState(false);
  if (!scholarship) return <NotFoundWorkspace/>;
  const isSaved = saved.includes(id);
  const application = applications.find((app) => app.scholarshipId === id);
  async function handleApplicationAction() {
    if (application) { navigate("/dashboard/applications"); return; }
    if (starting) return;
    setStarting(true);
    try {
      await startApplication(id);
      navigate("/dashboard/applications");
    } catch {
      toast("Unable to start application. Please try again.");
    } finally {
      setStarting(false);
    }
  }
  return <>
    <Link href="/dashboard/scholarships" className="inline-flex items-center gap-2 rounded-lg text-xs font-bold text-ink/50 hover:text-ink focus-ring"><ArrowLeft size={14}/> Back to scholarships</Link>
    <div className="mt-6 scholarship-detail-hero"><div><div className="flex flex-wrap gap-2"><span className="chip chip-sage">{scholarship.funding}</span><span className="chip">{scholarship.country}</span><span className="chip">{scholarship.degree}</span></div><h1>{scholarship.name}</h1><p>{scholarship.provider}</p><div className="mt-7 flex flex-wrap gap-3"><button className="button-primary" onClick={() => { toggleSave(id); toast(isSaved ? "Removed from shortlist" : "Saved to shortlist"); }}>{isSaved ? <BookmarkCheck size={15}/> : <Bookmark size={15}/>} {isSaved ? "Saved" : "Save scholarship"}</button><button className="button-secondary" onClick={() => toast("Opens the official programme source.")}><ExternalLink size={15}/> Official source</button></div></div><div className="detail-score"><span>{formatMatch(scholarship.match)}</span><b>Fit score</b><small>{detailFitScoreCaption(scholarship.eligibilityStatus)}</small></div></div>
    <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_.8fr]">
      <div className="space-y-6"><section className="paper-card p-6"><div className="eyebrow">Why OmerPath recommends this</div><h2 className="mt-3 font-display text-2xl">The fit is explainable.</h2><p className="mt-3 text-sm leading-relaxed text-ink/55">{scholarship.summary}</p><div className="mt-6 grid gap-3 sm:grid-cols-2">{scholarship.fitReasons.map((reason) => <div key={reason} className="criteria-row criteria-pass"><CheckCircle2 size={16}/><span>{reason}</span><b>Matches</b></div>)}</div></section>
      <section className="paper-card p-6"><div className="eyebrow">Needs attention</div><h2 className="mt-3 font-display text-2xl">What could block progress.</h2><div className="mt-5 space-y-3">{scholarship.attention.map((item) => <div key={item} className="criteria-row criteria-warn"><AlertCircle size={16}/><span>{item}</span><b>Review</b></div>)}</div></section>
      <section className="paper-card p-6"><div className="eyebrow">Funding coverage</div><h2 className="mt-3 font-display text-2xl">What the opportunity may cover.</h2><div className="mt-5 flex flex-wrap gap-2">{scholarship.coverage.map((item) => <span key={item} className="chip chip-sage"><Check size={12}/>{item}</span>)}</div><p className="mt-4 text-[11px] leading-relaxed text-ink/42">Confirm exact coverage on the official programme page.</p></section></div>
      <aside className="space-y-6"><section className="paper-card p-6"><div className="eyebrow">Freshness & source</div><div className="mt-5 space-y-4"><div className="source-row"><ShieldCheck size={17}/><div><b>{scholarship.sourceLabel}</b><span>Where this comes from</span></div></div><div className="source-row"><RefreshCw size={17}/><div><b>{scholarship.lastChecked}</b><span>Last checked</span></div></div><div className="source-row"><CalendarDays size={17}/><div><b>{scholarship.deadline}</b><span>{scholarship.deadlineNote}</span></div></div></div></section><section className="paper-card p-6"><div className="eyebrow">Application readiness</div><div className="mt-3 font-display text-3xl">{application ? `${application.progress}%` : "Not started"}</div><p className="mt-2 text-xs leading-relaxed text-ink/50">{application ? application.nextAction : "Add this opportunity to your applications when you're ready to work on it."}</p><button onClick={handleApplicationAction} disabled={starting} className="button-primary mt-5">{starting ? "Starting..." : application ? "Open application" : "Start application"}<ArrowRight size={14}/></button></section><section className="paper-card p-6"><div className="eyebrow">Ask before you decide</div><h2 className="mt-3 font-display text-xl">Need a second opinion?</h2><p className="mt-2 text-xs leading-relaxed text-ink/50">The Advisor can compare this opportunity with your other top matches using your profile and readiness data.</p><Link href="/dashboard/advisor" className="button-secondary mt-5"><Sparkles size={14}/> Compare with AI</Link></section></aside>
    </div>
  </>;
}

function Applications({ scholarships }: { scholarships: Scholarship[] }) {
  const { applications, updateApplicationStatus } = useApplications();
  const stages = ["Preparing", "Ready to apply", "Submitted"] as const;
  return <>
    <PageTitle eyebrow="Application planner" title={<>From shortlist<br/><em>to submitted.</em></>} description="Track readiness, next actions, and status, connected to your Passport documents."/>
    <div className="application-image-strip rounded-[24px]"><img src={ASSETS.application} alt="Student reviewing an application" loading="lazy"/><div><div className="eyebrow text-paper/55">Application pulse</div><h2 className="mt-2 font-display text-2xl text-paper">One ready to submit. Two still need deliberate work.</h2></div></div>
    <div className="mt-6 grid gap-5 xl:grid-cols-3">{stages.map((stage) => <section key={stage} className="application-column"><div className="application-column-head"><span>{stage}</span><b>{applications.filter((app) => app.status === stage).length}</b></div><div className="space-y-3">{applications.filter((app) => app.status === stage).map((app) => { const scholarship = scholarships.find((s) => s.id === app.scholarshipId); if (!scholarship) return null; return <article className="paper-card p-5" key={app.id}><div className="flex items-start justify-between gap-3"><div><h3 className="font-display text-lg leading-tight">{scholarship.name}</h3><p className="mt-1 text-[11px] text-ink/45">{scholarship.country} · Fit score: {formatMatch(scholarship.match)}</p></div><Link href={`/dashboard/scholarships/${scholarship.id}`} aria-label={`Open ${scholarship.name}`} className="icon-button"><ExternalLink size={15}/></Link></div><div className="mt-5"><div className="flex justify-between text-[10px] font-semibold"><span>Readiness</span><span>{app.progress}%</span></div><div className="progress-track mt-2"><i style={{ width: `${app.progress}%` }}/></div></div><div className="mt-4 rounded-xl bg-ink/[.035] p-3"><div className="eyebrow">Next action</div><div className="mt-1 text-xs font-semibold">{app.nextAction}</div></div><div className="mt-4 flex gap-2">{stage !== "Preparing" && <button className="mini-button" onClick={() => updateApplicationStatus(app.id, stage === "Submitted" ? "Ready to apply" : "Preparing")}><ArrowLeft size={13}/> Back</button>}{stage !== "Submitted" && <button className="mini-button mini-button-primary" onClick={() => updateApplicationStatus(app.id, stage === "Preparing" ? "Ready to apply" : "Submitted")}>{stage === "Ready to apply" ? "Mark submitted" : "Mark ready"}<ArrowRight size={13}/></button>}</div></article>; })}{applications.filter((app) => app.status === stage).length === 0 && <div className="application-empty">Nothing here yet.</div>}</div></section>)}</div>
  </>;
}

const PASSPORT_READINESS_TARGET = 5;

function formatFileSize(bytes: number): string {
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

function formatUploadedDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

function Passport() {
  const { documents, uploadDocument, deleteDocument, getDownloadUrl } = useDocuments();
  const { user } = useAuth();
  const { academicProfile } = useAcademicProfile();
  const identity = getUserIdentity(user);
  const inputRef = useRef<HTMLInputElement>(null);
  const [shareOpen, setShareOpen] = useState(false);
  const [expiry, setExpiry] = useState("7 days");
  const [allowDownload, setAllowDownload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const ready = Math.min(documents.length, PASSPORT_READINESS_TARGET);
  async function onFile(file?: File) {
    if (!file || uploading) return;
    setUploading(true);
    try {
      await uploadDocument(file);
      toast(`${file.name} added to your Passport`);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to upload document");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }
  async function onView(id: string) {
    try {
      const url = await getDownloadUrl(id);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch {
      toast("Unable to open document. Please try again.");
    }
  }
  async function onDelete(id: string, name: string) {
    if (!window.confirm(`Delete "${name}"? This cannot be undone.`)) return;
    try {
      await deleteDocument(id);
      toast(`${name} deleted`);
    } catch {
      toast("Unable to delete document. Please try again.");
    }
  }
  return <>
    <PageTitle eyebrow="Your reusable profile" title={<>The scholarship<br/><em>passport.</em></>} description="One trusted place for the documents, facts, and story you carry into every application." action={<button onClick={() => setShareOpen(true)} className="button-secondary"><Send size={15}/> Share passport</button>}/>
    <div className="grid gap-6 xl:grid-cols-[.85fr_1.3fr]"><div className="relative min-h-[390px] overflow-hidden rounded-[26px] bg-ink p-7 text-paper"><img src={ASSETS.passport} alt="Organized scholarship documents" loading="lazy" className="absolute inset-0 size-full object-cover opacity-30"/><div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(20,33,38,.25),rgba(20,33,38,.94))]"/><div className="relative flex h-full flex-col"><div className="flex items-center justify-between"><div className="eyebrow text-paper/50">OmerPath · Student passport</div><LockKeyhole size={16} className="text-saffron"/></div><div className="mt-auto"><div className="flex size-14 items-center justify-center rounded-full bg-sage text-lg font-bold text-ink">{identity.initials || "—"}</div><div className="mt-5 font-display text-4xl tracking-[-.05em]">{identity.name || "Your name"}</div><div className="mt-2 text-sm text-paper/60">{academicProfile?.current_degree || "Add your degree"} · {user?.nationality || "Add your nationality"}</div><div className="mt-8 grid grid-cols-3 gap-5 border-t border-paper/15 pt-5"><div><div className="eyebrow text-paper/40">Target</div><div className="mt-1 text-sm font-semibold">{academicProfile?.target_degree || "—"}</div></div><div><div className="eyebrow text-paper/40">GPA</div><div className="mt-1 text-sm font-semibold">{academicProfile?.gpa || "—"}</div></div><div><div className="eyebrow text-paper/40">IELTS</div><div className="mt-1 text-sm font-semibold">{academicProfile?.language_test_score || "—"}</div></div></div></div></div></div>
      <div className="paper-card p-6"><div className="flex flex-wrap items-end justify-between gap-4"><div><div className="eyebrow">Document readiness</div><div className="mt-2 font-display text-3xl tracking-[-.04em]">{ready} <span className="text-lg text-ink/35">of {PASSPORT_READINESS_TARGET} ready</span></div></div><button onClick={() => inputRef.current?.click()} disabled={uploading} className="button-secondary"><Plus size={15}/> {uploading ? "Uploading..." : "Add file"}</button><input ref={inputRef} className="sr-only" type="file" accept=".pdf,.docx,.jpg,.jpeg,.png" onChange={(e) => onFile(e.target.files?.[0])}/></div><div className="mt-6 space-y-3">{documents.map((doc) => <div key={doc.id} className="document-row"><div className="flex size-9 items-center justify-center rounded-xl bg-sage/30 text-ink"><Check size={16}/></div><div className="flex-1"><div className="text-sm font-semibold">{doc.originalFilename}</div><div className="mt-0.5 text-[11px] text-ink/45">{formatFileSize(doc.fileSize)} · added {formatUploadedDate(doc.createdAt)}</div></div><button aria-label={`View ${doc.originalFilename}`} className="icon-button" onClick={() => onView(doc.id)}><Eye size={16}/></button><button aria-label={`Delete ${doc.originalFilename}`} className="icon-button" onClick={() => onDelete(doc.id, doc.originalFilename)}><Trash2 size={16}/></button></div>)}{documents.length === 0 && <div className="application-empty">No documents uploaded yet.</div>}</div><button className="drop-zone mt-6" onClick={() => inputRef.current?.click()} onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); onFile(e.dataTransfer.files?.[0]); }}><Upload size={18}/><b>Drop a document here or choose a file</b><span>PDF, DOCX, JPG or PNG · up to 10 MB</span></button></div></div>
    {shareOpen && <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="share-title"><div className="modal-card"><div className="flex items-start justify-between"><div><div className="eyebrow">Passport sharing</div><h2 id="share-title" className="mt-2 font-display text-2xl">Control what leaves your workspace.</h2></div><button aria-label="Close share dialog" className="icon-button" onClick={() => setShareOpen(false)}><X size={17}/></button></div><p className="mt-3 text-sm leading-relaxed text-ink/55">Anyone with this link can view your shared documents until it expires.</p><label className="settings-row mt-5"><span><b>Link expiry</b><small>How long the link stays active.</small></span><select value={expiry} onChange={(e) => setExpiry(e.target.value)}><option>24 hours</option><option>7 days</option><option>30 days</option></select></label><label className="settings-row"><span><b>Allow document downloads</b><small>Off keeps sharing read-only.</small></span><input type="checkbox" checked={allowDownload} onChange={(e) => setAllowDownload(e.target.checked)}/></label><div className="share-link"><Link2 size={15}/><span>omerpath.app/p/ali-r-7f2a</span><button aria-label="Copy share link" onClick={() => { navigator.clipboard?.writeText("https://omerpath.app/p/ali-r-7f2a"); toast(`Link copied · expires in ${expiry}`); }}><Copy size={15}/></button></div><div className="mt-5 flex justify-end gap-2"><button className="button-secondary" onClick={() => setShareOpen(false)}>Cancel</button><button className="button-primary" onClick={() => { toast(`Share link created · ${expiry} · downloads ${allowDownload ? "allowed" : "blocked"}`); setShareOpen(false); }}>Create share link</button></div></div></div>}
  </>;
}

type AdvisorMessage = { from: "ai" | "you"; text: string };
type AdvisorHistoryEntry = { role: "user" | "assistant"; content: string };
type AdvisorApiResponse = { answer: string };

const ADVISOR_ERROR_MESSAGE = "The Advisor is temporarily unavailable. Please try again in a moment.";
const ADVISOR_HISTORY_LIMIT = 10;

function Advisor() {
  const { user } = useAuth();
  const firstName = getUserIdentity(user).name.split(" ")[0] || "there";
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<AdvisorMessage[]>([{ from: "ai", text: `Hi ${firstName}, ask me about your scholarships, matches, applications, or documents — I'll answer using your real OmerPath data.` }]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send(text = message) {
    const clean = text.trim();
    if (!clean || sending) return;
    const history: AdvisorHistoryEntry[] = messages.slice(-ADVISOR_HISTORY_LIMIT).map((m) => ({ role: m.from === "you" ? "user" : "assistant", content: m.text }));
    setMessages((prev) => [...prev, { from: "you", text: clean }]);
    setMessage("");
    setError(null);
    setSending(true);
    try {
      const response = await apiFetch("/api/advisor/chat", {
        method: "POST",
        body: JSON.stringify({ message: clean, history }),
      });
      if (!response.ok) throw new Error(ADVISOR_ERROR_MESSAGE);
      const data: AdvisorApiResponse = await response.json();
      setMessages((prev) => [...prev, { from: "ai", text: data.answer }]);
    } catch {
      setError(ADVISOR_ERROR_MESSAGE);
    } finally {
      setSending(false);
    }
  }
  const prompts = ["Why do I match Chevening?", "What documents am I missing?", "Compare my top 3"];
  return <>
    <PageTitle eyebrow="" title={<>Clarity for every<br/><em>next step.</em></>} description="Ask about eligibility, documents, deadlines, or your shortlist." action={<div className="chip chip-sage"><span className="size-2 rounded-full bg-[#78917d]"/> AI Advisor is ready</div>}/>
    <div className="grid gap-6 xl:grid-cols-[1.2fr_.75fr]"><div className="paper-card flex min-h-[560px] flex-col overflow-hidden"><div className="flex items-center gap-4 border-b border-ink/8 p-5"><div className="flex size-11 items-center justify-center rounded-[14px] bg-ink text-saffron"><Sparkles size={20}/></div><div><div className="font-display text-xl">OmerPath Advisor</div><div className="text-xs text-ink/45">Context: profile · Passport · applications · shortlist</div></div></div><div className="flex-1 space-y-4 overflow-auto p-5" aria-live="polite">{messages.map((m,i) => <div key={i} className={`flex ${m.from === "you" ? "justify-end" : "justify-start"}`}><div className={`max-w-[85%] whitespace-pre-line rounded-[18px] px-4 py-3 text-sm leading-relaxed ${m.from === "you" ? "bg-ink text-paper" : "bg-sage/20 text-ink"}`}>{m.text}</div></div>)}{sending && <div className="flex justify-start"><div className="max-w-[85%] rounded-[18px] bg-sage/20 px-4 py-3 text-sm leading-relaxed text-ink/50">OmerPath Advisor is thinking…</div></div>}{error && <div role="alert" className="rounded-[14px] border border-red-200 bg-red-50 px-4 py-3 text-sm leading-relaxed text-red-700">{error}</div>}</div><div className="border-t border-ink/8 p-4"><div className="flex gap-2 rounded-2xl bg-ink/[.04] p-2"><input aria-label="Ask OmerPath Advisor" value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} disabled={sending} placeholder="Ask about your scholarship path…" className="min-w-0 flex-1 bg-transparent px-3 text-sm outline-none placeholder:text-ink/35 disabled:opacity-50"/><button aria-label="Send message" onClick={() => send()} disabled={sending} className="flex size-9 items-center justify-center rounded-xl bg-ink text-paper transition hover:bg-saffron focus-ring disabled:opacity-50"><ArrowRight size={16}/></button></div><div className="mt-3 flex flex-wrap gap-2">{prompts.map((q) => <button key={q} onClick={() => send(q)} disabled={sending} className="chip transition hover:bg-ink/10 focus-ring disabled:opacity-50">{q}</button>)}</div></div></div><div className="space-y-6"><div className="relative min-h-[230px] overflow-hidden rounded-[26px] bg-ink p-6 text-paper"><img src={ASSETS.advisor} alt="Student researching scholarships" loading="lazy" className="absolute inset-0 size-full object-cover opacity-35"/><div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(20,33,38,.95),rgba(20,33,38,.35))]"/><div className="relative max-w-[75%]"><div className="eyebrow text-paper/55">Advisor brief</div><div className="mt-3 font-display text-2xl leading-tight">Your profile has a clear story.</div><p className="mt-3 text-xs leading-relaxed text-paper/60">Computer Science → AI → impact. Make that through-line visible in every statement.</p></div></div><div className="paper-card p-6"><div className="eyebrow">Suggested focus</div><div className="mt-4 space-y-3"><ActionItem icon={FileText} title="Finish reusable documents" detail="Recommendation letter first" href="/dashboard/passport"/><ActionItem icon={ClipboardCheck} title="Submit the closest-ready application" detail="Erasmus is at 91%" href="/dashboard/applications"/><ActionItem icon={Compass} title="Compare opportunity tradeoffs" detail="Funding, fit, country, readiness" href="/dashboard/scholarships"/></div></div></div></div>
  </>;
}

function Resources() {
  const [query, setQuery] = useState("");
  const resources = [
    { title: "Scholarship statement checklist", type: "Checklist", body: "A concise structure for evidence, motivation, fit, and impact." },
    { title: "Recommendation letter briefing pack", type: "Template", body: "What to send your recommender so they can write with useful specificity." },
    { title: "How OmerPath match scores work", type: "Explainer", body: "Eligibility signals, fit signals, missing data, and the difference between fit and outcome probability." },
    { title: "Official-source verification guide", type: "Guide", body: "How to confirm deadlines, funding, and eligibility before you submit." },
    { title: "Interview story bank", type: "Worksheet", body: "Build concise examples for leadership, impact, resilience, and collaboration." },
    { title: "Application timeline planner", type: "Planner", body: "Work backward from deadlines and protect time for references and document checks." },
  ];
  const visible = resources.filter((resource) => `${resource.title} ${resource.type} ${resource.body}`.toLowerCase().includes(query.toLowerCase()));
  return <><PageTitle eyebrow="Resource library" title={<>Prepare with<br/><em>less guesswork.</em></>} description="Practical guidance for the steps around the scholarship itself: evidence, documents, recommendations, interviews, and verification."/><label className="search-field max-w-xl"><Search size={16}/><span className="sr-only">Search resources</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search guides, templates, checklists…"/></label><div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{visible.map((resource) => <article key={resource.title} className="paper-card p-6"><div className="flex items-center justify-between"><span className="chip chip-sage">{resource.type}</span><FileText size={18} className="text-ink/30"/></div><h2 className="mt-6 font-display text-xl">{resource.title}</h2><p className="mt-2 text-xs leading-relaxed text-ink/50">{resource.body}</p><button onClick={() => toast(`${resource.title} opened`)} className="text-link mt-6">Open resource <ArrowRight size={14}/></button></article>)}</div></>;
}

const NOTIFICATION_TYPE_LABELS: Record<string, string> = {
  application_started: "Application",
  application_status_changed: "Application",
  document_uploaded: "Passport",
  document_deleted: "Passport",
};

function formatNotificationTime(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

function Notifications() {
  const { notifications, markRead, markAllRead } = useNotifications();
  return <><PageTitle eyebrow="Notifications" title={<>Only the things<br/><em>that can change a decision.</em></>} description="Deadline reminders, readiness changes, source checks, and advisor nudges in one quieter inbox." action={<button className="button-secondary" onClick={() => { markAllRead(); toast("All notifications marked as read"); }}><Check size={15}/> Mark all read</button>}/><div className="space-y-3">{notifications.map((note) => <button key={note.id} onClick={() => markRead(note.id)} className={`notification-row ${note.isRead ? "notification-read" : ""}`}><span className="notification-dot"/><div className="flex-1 text-left"><div className="flex flex-wrap items-center gap-2"><b>{note.title}</b><span className="chip">{NOTIFICATION_TYPE_LABELS[note.type] ?? note.type}</span></div><p>{note.message}</p></div><time>{formatNotificationTime(note.createdAt)}</time></button>)}{notifications.length === 0 && <div className="application-empty">No notifications yet.</div>}</div></>;
}

function Profile() {
  type ProfileData = AuthUser;
  type ProfileDraft = {
    first_name: string;
    last_name: string;
    email: string;
    nationality: string;
    country_of_residence: string;
  };

  const { user, setAuthenticatedUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [draft, setDraft] = useState<ProfileDraft | null>(() => user ? ({
    first_name: user.first_name ?? "",
    last_name: user.last_name ?? "",
    email: user.email,
    nationality: user.nationality ?? "",
    country_of_residence: user.country_of_residence ?? "",
  }) : null);

  async function save() {
    if (!draft || saving) return;
    setSaveError(null);
    setSaving(true);
    try {
      const response = await apiFetch("/api/profile/me", {
        method: "PATCH",
        body: JSON.stringify({
          first_name: draft.first_name.trim(),
          last_name: draft.last_name.trim(),
          nationality: draft.nationality.trim(),
          country_of_residence: draft.country_of_residence.trim(),
        }),
      });
      if (!response.ok) throw new Error("Unable to update profile");
      const profile: ProfileData = await response.json();
      setDraft({
        first_name: profile.first_name ?? "",
        last_name: profile.last_name ?? "",
        email: profile.email,
        nationality: profile.nationality ?? "",
        country_of_residence: profile.country_of_residence ?? "",
      });
      setAuthenticatedUser(profile);
      setEditing(false);
      toast("Profile updated.");
    } catch {
      setSaveError("Unable to update your profile. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  if (!draft) return <div role="alert">Unable to load your profile.</div>;

  const fields = [
    ["First name", "first_name"],
    ["Last name", "last_name"],
    ["Email", "email"],
    ["Nationality", "nationality"],
    ["Country of residence", "country_of_residence"],
  ] as const;
  const completedFields = fields.filter(([, key]) => draft[key].trim()).length;
  const profileCompleteness = Math.round((completedFields / fields.length) * 100);

  return <><PageTitle eyebrow="Your profile" title={<>The story behind<br/><em>your matches.</em></>} description="Keep the inputs current so match explanations and advisor guidance remain relevant." action={<button className="button-primary" disabled={saving} onClick={() => editing ? save() : setEditing(true)}>{editing ? <Check size={15}/> : <Pencil size={15}/>} {saving ? "Saving..." : editing ? "Save changes" : "Edit profile"}</button>}/><div className="grid gap-6 xl:grid-cols-[1fr_.7fr]"><div className="paper-card p-6"><div className="form-grid two">{fields.map(([label,key]) => <label key={key}><span>{label}</span><input disabled={!editing || key === "email"} value={draft[key]} onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}/></label>)}</div>{saveError && <p className="mt-4 text-xs text-red-700" role="alert">{saveError}</p>}</div><div className="space-y-6"><div className="paper-card p-6"><div className="eyebrow">Profile completeness</div><div className="mt-3 font-display text-4xl">{profileCompleteness}%</div><div className="progress-track mt-4"><i style={{ width: `${profileCompleteness}%` }}/></div><p className="mt-4 text-xs leading-relaxed text-ink/50">Complete your profile details to keep your scholarship information current.</p></div><div className="paper-card p-6"><div className="eyebrow">Preferred destinations</div><p className="mt-4 text-xs leading-relaxed text-ink/50">No preferred destinations are available in your profile yet.</p><Link href="/onboarding" className="text-link mt-5">Revisit matching setup <ArrowRight size={14}/></Link></div></div></div></>;
}

function Settings() {
  const { settings, updateSetting } = useSettings();
  const items: Array<[keyof typeof settings,string,string]> = [
    ["deadlineReminders","Deadline reminders","Notify me when a saved or active application is approaching a deadline."],
    ["eligibilityChanges","Eligibility/source changes","Surface meaningful changes after an official-source refresh."],
    ["advisorNudges","Advisor nudges","Suggest a next action when readiness data shows a clear bottleneck."],
    ["weeklyDigest","Weekly progress digest","Summarize saved matches, readiness changes, and upcoming work."],
    ["shareAnalytics","Anonymous product analytics","Allow anonymous usage analytics. Off by default."],
  ];
  return <><PageTitle eyebrow="Settings" title={<>Make OmerPath<br/><em>work your way.</em></>} description="Control notifications, privacy preferences, and the behaviors that shape your workspace."/><div className="grid gap-6 xl:grid-cols-[1fr_.7fr]"><div className="paper-card divide-y divide-ink/8">{items.map(([key,title,desc]) => <label key={key} className="settings-row"><span><b>{title}</b><small>{desc}</small></span><input type="checkbox" checked={settings[key]} onChange={(e) => updateSetting(key, e.target.checked)}/></label>)}</div><div className="space-y-6"><div className="paper-card p-6"><div className="flex items-center gap-3"><ShieldCheck size={19} className="text-[#78917d]"/><div className="font-display text-xl">Privacy by design</div></div><p className="mt-3 text-xs leading-relaxed text-ink/50">Sharing uses explicit permissions, link expiry, revocation, and encrypted storage.</p></div><div className="paper-card p-6"><div className="eyebrow">Reset data</div><p className="mt-3 text-xs leading-relaxed text-ink/50">Your changes are stored only in this browser.</p><button className="button-secondary mt-5" onClick={() => { if (window.confirm("Reset all OmerPath data in this browser?")) { ["omerpath-saved","omerpath-applications","omerpath-documents","omerpath-profile","omerpath-settings","omerpath-notification-read"].forEach((key) => localStorage.removeItem(key)); window.location.reload(); } }}><Trash2 size={14}/> Reset data</button></div></div></div></>;
}

function NotFoundWorkspace() {
  return <div className="empty-state"><Compass size={28}/><h2>This workspace page does not exist.</h2><p>Use the navigation to return to your scholarship path.</p><Link href="/dashboard" className="button-primary">Back to overview <ArrowRight size={14}/></Link></div>;
}

export default function Home() {
  const [location] = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user: authUser } = useAuth();
  const { scholarships } = useScholarships();
  const path = location.split("/").filter(Boolean);
  const section = path[1] || "overview";
  const detailId = path[2];
  let page: React.ReactNode;
  if (section === "overview") page = <Dashboard scholarships={scholarships}/>;
  else if (section === "scholarships" && detailId) page = <ScholarshipDetail id={detailId} scholarships={scholarships}/>;
  else if (section === "scholarships") page = <Scholarships scholarships={scholarships}/>;
  else if (section === "applications") page = <Applications scholarships={scholarships}/>;
  else if (section === "passport") page = <Passport/>;
  else if (section === "advisor") page = <Advisor/>;
  else if (section === "resources") page = <Resources/>;
  else if (section === "notifications") page = <Notifications/>;
  else if (section === "profile") page = <Profile/>;
  else if (section === "settings") page = <Settings/>;
  else page = <NotFoundWorkspace/>;

  return <div className="min-h-screen bg-paper text-ink"><Sidebar mobileOpen={mobileOpen} close={() => setMobileOpen(false)} user={authUser}/>{mobileOpen && <button aria-label="Close navigation overlay" onClick={() => setMobileOpen(false)} className="fixed inset-0 z-40 bg-ink/20 backdrop-blur-sm lg:hidden"/>}<div className="lg:pl-[256px]"><Header onMenu={() => setMobileOpen(true)} user={authUser}/><div className="px-5 pt-4 lg:px-10"><DemoBanner/></div><main className="mx-auto max-w-[1440px] px-5 py-8 lg:px-10 lg:py-10">{page}</main><footer className="px-5 pb-8 pt-2 text-[10px] text-ink/35 lg:px-10">OmerPath · <Link href="/dashboard/settings" className="underline focus-ring">Privacy & settings</Link></footer></div></div>;
}

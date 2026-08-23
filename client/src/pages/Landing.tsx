import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Check, Compass, FileCheck2, GraduationCap, Menu, ShieldCheck, Sparkles, X, MapPin, Target } from "lucide-react";
import { Link, useLocation } from "wouter";
import { ASSETS } from "@/lib/brand";
import { useScholarships } from "@/lib/useScholarships";

const navItems = [
  ["Scholarships", "#scholarships"],
  ["How it works", "#how-it-works"],
  ["Scholarship Passport", "#passport"],
  ["AI Advisor", "#advisor"],
  ["Trust", "#trust"],
] as const;

function useReveal() {
  useEffect(() => {
    const items = document.querySelectorAll<HTMLElement>(".landing-reveal");
    if (!("IntersectionObserver" in window)) { items.forEach((item) => item.classList.add("is-visible")); return; }
    const observer = new IntersectionObserver((entries) => entries.forEach((entry) => { if (entry.isIntersecting) entry.target.classList.add("is-visible"); }), { threshold: 0.12 });
    items.forEach((item) => observer.observe(item));
    return () => observer.disconnect();
  }, []);
}

function SectionIntro({ kicker, title, body }: { kicker:string; title:React.ReactNode; body:string }) {
  return <div className="landing-intro landing-reveal"><div className="landing-kicker">{kicker}</div><h2>{title}</h2><p>{body}</p></div>;
}

function LandingNav() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => { const onScroll = () => setScrolled(window.scrollY > 48); window.addEventListener("scroll", onScroll, { passive: true }); onScroll(); return () => window.removeEventListener("scroll", onScroll); }, []);
  return <header className={`landing-nav ${scrolled ? "landing-nav-scrolled" : ""}`}>
    <a href="#top" className="landing-brand focus-ring"><img src={ASSETS.logo} alt="" width="38" height="38"/><span><b>OmerPath</b><small>SCHOLARSHIP GUIDANCE</small></span></a>
    <nav className="landing-desktop-nav" aria-label="Public navigation">{navItems.map(([label, href]) => <a className="focus-ring" key={href} href={href}>{label}</a>)}</nav>
    <div className="landing-nav-actions"><Link href="/login" className="landing-login focus-ring">Log in</Link><Link href="/signup" className="landing-signup focus-ring">Sign up <ArrowRight size={15}/></Link></div>
    <button aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open} onClick={() => setOpen(!open)} className="landing-menu focus-ring">{open ? <X size={22}/> : <Menu size={22}/>}</button>
    {open && <div className="landing-mobile-menu">{navItems.map(([label, href]) => <a key={href} href={href} onClick={() => setOpen(false)}>{label}</a>)}<Link href="/login" onClick={() => setOpen(false)}>Log in</Link><Link href="/signup" className="landing-mobile-cta" onClick={() => setOpen(false)}>Create my profile <ArrowRight size={15}/></Link></div>}
  </header>;
}

function Hero() {
  return <section id="top" className="landing-hero"><div className="landing-hero-image"/><div className="landing-hero-overlay"/><LandingNav/><div className="landing-hero-content landing-reveal"><div className="landing-kicker light-kicker"><span/> Global education, clearly guided</div><h1>Your global education <em>starts here.</em></h1><p>See scholarships matched to your profile, understand why they fit, and manage every step through to submission.</p><div className="landing-hero-actions"><Link href="/signup" className="landing-primary focus-ring">Find my scholarships <ArrowRight size={17}/></Link><a href="#quick-match" className="landing-secondary focus-ring">Try the matcher <span>↓</span></a></div><div className="landing-hero-note"><span className="landing-note-line"/> Based on your profile. Never a promise of outcome.</div></div></section>;
}

function QuickMatch() {
  const [, navigate] = useLocation();
  const [nationality, setNationality] = useState("Pakistan");
  const [degree, setDegree] = useState("Master's");
  const [field, setField] = useState("Computer Science & AI");
  const [destination, setDestination] = useState("Open to multiple countries");
  const [analysed, setAnalysed] = useState(false);
  const count = useMemo(() => 38 + (degree === "Master's" ? 14 : 7) + (destination.includes("multiple") ? 8 : 3), [degree, destination]);
  return <section id="quick-match" className="quick-match-section landing-reveal"><div className="quick-match-copy"><div className="landing-kicker">Try OmerPath in 30 seconds</div><h2>See matching <em>in action.</em></h2><p>Enter a few details and see how OmerPath builds a shortlist.</p><div className="prototype-data-note light-note">This quick check doesn't evaluate real eligibility — it shows how matching and explanations work.</div></div><div className="quick-match-card"><div className="quick-match-grid"><label><span>Nationality</span><input value={nationality} onChange={(e) => { setNationality(e.target.value); setAnalysed(false); }}/></label><label><span>Target degree</span><select value={degree} onChange={(e) => { setDegree(e.target.value); setAnalysed(false); }}><option>Master's</option><option>PhD</option><option>Bachelor's</option></select></label><label><span>Field</span><select value={field} onChange={(e) => { setField(e.target.value); setAnalysed(false); }}><option>Computer Science & AI</option><option>Data Science</option><option>Engineering</option><option>Business & Management</option><option>Public Policy</option></select></label><label><span>Destination</span><select value={destination} onChange={(e) => { setDestination(e.target.value); setAnalysed(false); }}><option>Open to multiple countries</option><option>United Kingdom</option><option>Germany</option><option>Canada</option><option>Australia</option></select></label></div>{!analysed ? <button className="landing-primary quick-match-action" onClick={() => setAnalysed(true)}>Analyze my profile <Sparkles size={16}/></button> : <div className="quick-match-result" aria-live="polite"><div className="quick-match-count"><strong>{count}</strong><span>potential opportunities</span></div><div className="quick-match-stats"><span><b>12</b> strong matches</span><span><b>5</b> fully funded</span><span><b>3</b> actions to improve readiness</span></div><div className="quick-match-reason"><Target size={16}/><span><b>Why this result?</b> {nationality}, {degree}, {field}, and your destination preference shape the shortlist.</span></div><button className="landing-primary" onClick={() => navigate("/signup")}>Create my profile <ArrowRight size={16}/></button></div>}</div></section>;
}

function OpportunitySection() {
  return <section id="scholarships" className="landing-section landing-split landing-reveal"><div className="landing-photo-frame"><img src={ASSETS.publicOpportunities} alt="International students walking through a university campus" loading="lazy"/><div className="photo-stamp">GLOBAL<br/><b>OPPORTUNITIES</b></div></div><div className="landing-copy"><div className="landing-kicker">01 / The opportunity library</div><h2>Find global <em>opportunities.</em></h2><p>OmerPath collects scholarship opportunities in one library and ranks the ones that fit your profile.</p><div className="landing-check-list"><div><Check size={15}/> Official-source field built into each record</div><div><Check size={15}/> Fit explained in plain language</div><div><Check size={15}/> Freshness status visible before you act</div></div><Link href="/signup" className="text-link focus-ring">Build my shortlist <ArrowRight size={16}/></Link></div></section>;
}

function MatchingSection() {
  return <section className="landing-section landing-dark-section landing-split reverse landing-reveal"><div className="landing-photo-frame dark-photo"><img src={ASSETS.publicAi} alt="Student researching scholarships in a university library" loading="lazy"/><div className="match-float"><div className="landing-kicker">Match example</div><strong>95%</strong><span>Profile match</span><small>Chevening · example score</small></div></div><div className="landing-copy text-paper"><div className="landing-kicker">02 / A clearer shortlist</div><h2>AI-powered matches <em>you can question.</em></h2><p>A score means little without reasons. OmerPath shows what matches, what's missing, and how competitive it is.</p><div className="landing-score-row"><div><b>95%</b><span>Profile fit example</span></div><div><b>4</b><span>Reasons explained</span></div><div><b>2</b><span>Items to review</span></div></div><Link href="/signup" className="text-link light-link focus-ring">See how fit is explained <ArrowRight size={16}/></Link></div></section>;
}

function PassportSection() {
  return <section id="passport" className="landing-section landing-split landing-reveal"><div className="landing-copy"><div className="landing-kicker">03 / Your reusable profile</div><h2>Your scholarship <em>passport.</em></h2><p>Keep your documents, essays, references, and verification status in one place, and see how ready you are for each opportunity.</p><div className="passport-file-list"><span><FileCheck2 size={15}/> Academic transcript <b>Ready</b></span><span><FileCheck2 size={15}/> English test report <b>Ready</b></span><span><FileCheck2 size={15}/> Recommendation letter <b>Needed next</b></span></div><Link href="/signup" className="text-link focus-ring">Build my Passport <ArrowRight size={16}/></Link></div><div className="landing-photo-frame passport-photo"><img src={ASSETS.publicPassport} alt="Organized scholarship documents on a study desk" loading="lazy"/><div className="passport-card">OMERPATH<br/><b>STUDENT PASSPORT</b><small>Reusable evidence. Controlled sharing. Clear readiness.</small></div></div></section>;
}

function TrustSection() {
  return <section id="trust" className="landing-verified landing-reveal"><div className="landing-verified-image"><img src={ASSETS.campus} alt="University campus architecture" loading="lazy"/></div><div className="landing-verified-copy"><div className="landing-kicker">04 / Trust in the details</div><h2>Transparent about where <em>information comes from.</em></h2><p>Scholarship rules change. OmerPath shows the source, last-check time, and eligibility basis instead of hiding them behind a single score.</p><div className="verified-badges"><span><ShieldCheck size={17}/> Official source</span><span><ShieldCheck size={17}/> Last checked</span><span><ShieldCheck size={17}/> Eligibility explained</span><span><ShieldCheck size={17}/> AI limitations stated</span></div></div></section>;
}

function AdvisorSection() {
  return <section id="advisor" className="landing-advisor landing-reveal"><div className="landing-advisor-image"/><div className="landing-advisor-overlay"/><div className="landing-advisor-content"><div className="landing-kicker light-kicker">05 / A second pair of eyes</div><h2>Meet the OmerPath <em>AI Advisor.</em></h2><p>Not a generic chatbot — it uses your profile, shortlist, documents, and readiness to tell you what deserves attention next.</p><div className="advisor-window"><div className="advisor-question">Which application should I work on first?</div><div className="advisor-answer"><span className="advisor-dot"/><div><b>Erasmus is closest to submission, but your missing recommendation letter affects more than one top match.</b><div className="advisor-recs"><span>Finish reference <strong>1st</strong></span><span>Review Erasmus <strong>2nd</strong></span><span>Compare DAAD <strong>3rd</strong></span></div></div></div></div><Link href="/signup" className="landing-primary focus-ring">Try the Advisor <Sparkles size={16}/></Link></div></section>;
}

function HowItWorks() {
  const steps = [
    ["01", "Build your profile", "Add your academic background, goals, tests, and experience.", Compass],
    ["02", "Understand your matches", "See the score, reasons, caveats, and source status.", Target],
    ["03", "Build your Passport", "Reuse documents and track readiness across applications.", FileCheck2],
    ["04", "Prioritize with AI", "Ask what to do next using your actual workspace context.", Sparkles],
    ["05", "Track every application", "Move from preparation to submission without losing context.", GraduationCap],
  ] as const;
  return <section id="how-it-works" className="landing-how landing-reveal"><SectionIntro kicker="06 / A clear route" title={<>Less noise.<br/><em>More momentum.</em></>} body="OmerPath turns scholarship search into a sequence of decisions you can understand and act on."/><div className="landing-steps">{steps.map(([number, title, body, Icon]) => <div className="landing-step" key={number}><span>{number}</span><Icon size={21}/><h3>{title}</h3><p>{body}</p></div>)}</div></section>;
}

function Featured() {
  const { scholarships } = useScholarships();
  return <section id="featured" className="landing-featured landing-reveal"><SectionIntro kicker="07 / A considered shortlist" title={<>Opportunities worth<br/><em>a closer look.</em></>} body="Compare fit, funding, deadline status, and source transparency at a glance."/><div className="landing-featured-grid">{scholarships.slice(0,4).map((s) => <article key={s.id} className="featured-card"><div className="featured-card-top"><span>{s.country}</span><strong>{s.funding}</strong></div><h3>{s.name}</h3><p>{s.provider} · {s.degree}</p><div className="featured-card-bottom"><span>Deadline <b>{s.deadline}</b></span><span className="featured-match">{s.match === null ? "—" : `${s.match}%`} <small>match</small></span></div></article>)}</div></section>;
}

function FinalCTA() {
  return <section className="landing-final landing-reveal"><div className="landing-final-image"/><div className="landing-final-overlay"/><div className="landing-final-content"><h2>Start with your <em>profile.</em></h2><p>Create your profile and see your matches, ranked and explained.</p><Link href="/signup" className="landing-primary focus-ring">Create my profile <ArrowRight size={17}/></Link></div><div className="landing-final-footer"><span>OmerPath</span><span>© 2026</span></div></section>;
}

export default function Landing() {
  useReveal();
  return <main className="landing-page"><Hero/><QuickMatch/><OpportunitySection/><MatchingSection/><PassportSection/><TrustSection/><AdvisorSection/><HowItWorks/><Featured/><FinalCTA/></main>;
}

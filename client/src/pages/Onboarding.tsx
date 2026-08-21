import { useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, Check, GraduationCap, MapPin, Sparkles, UserRound } from "lucide-react";
import { Link, useLocation } from "wouter";
import { ASSETS } from "@/lib/brand";
import { usePrototype } from "@/contexts/PrototypeContext";

const destinations = ["United Kingdom", "Germany", "Canada", "United States", "Australia", "Multiple Countries"];
const degreeTargets = ["Master's", "PhD", "Bachelor's"];
const fields = ["Computer Science & AI", "Data Science", "Engineering", "Business & Management", "Public Policy", "Health Sciences"];

export default function Onboarding() {
  const [, navigate] = useLocation();
  const { profile, updateProfile } = usePrototype();
  const [step, setStep] = useState(1);
  const [draft, setDraft] = useState(profile);
  const progress = step / 4 * 100;
  const matchesEstimate = useMemo(() => 36 + draft.destinations.length * 5 + (draft.ielts ? 7 : 0), [draft.destinations.length, draft.ielts]);

  function next() {
    if (step < 4) setStep((value) => value + 1);
    else {
      updateProfile(draft);
      navigate("/dashboard/scholarships");
    }
  }

  function toggleDestination(destination: string) {
    setDraft((prev) => ({ ...prev, destinations: prev.destinations.includes(destination) ? prev.destinations.filter((value) => value !== destination) : [...prev.destinations, destination] }));
  }

  return <main className="onboarding-shell">
    <header className="onboarding-header">
      <Link href="/" className="landing-brand"><img src={ASSETS.logo} alt=""/><span><b>OmerPath</b><small>SCHOLARSHIP GUIDANCE</small></span></Link>
      <div className="onboarding-progress-wrap"><span>Profile setup</span><div className="onboarding-progress"><i style={{ width: `${progress}%` }}/></div><b>{step}/4</b></div>
      <Link href="/dashboard" className="text-link">Skip for now <ArrowRight size={14}/></Link>
    </header>

    <section className="onboarding-content">
      <aside className="onboarding-aside">
        <div className="eyebrow">Why this matters</div>
        {step === 1 && <><UserRound size={28}/><h2>Your academic starting point.</h2><p>OmerPath uses this to rule out obvious mismatches and explain the matches that remain.</p></>}
        {step === 2 && <><GraduationCap size={28}/><h2>Where you want to go next.</h2><p>Your target degree and field shape the opportunity shortlist.</p></>}
        {step === 3 && <><MapPin size={28}/><h2>Make the world a little smaller.</h2><p>Choose destinations you would genuinely consider. You can change these later.</p></>}
        {step === 4 && <><Sparkles size={28}/><h2>Your first shortlist is ready.</h2><p>OmerPath will rank scholarships that fit your profile and explain why.</p></>}
      </aside>

      <div className="onboarding-card">
        {step === 1 && <div className="onboarding-step">
          <div className="eyebrow">Step 1 · Academic profile</div><h1>Tell us where you're starting.</h1>
          <div className="form-grid two"><label><span>Nationality</span><input value={draft.nationality} onChange={(e) => setDraft({ ...draft, nationality: e.target.value })}/></label><label><span>Current degree</span><input value={draft.degree} onChange={(e) => setDraft({ ...draft, degree: e.target.value })}/></label><label><span>GPA</span><input value={draft.gpa} onChange={(e) => setDraft({ ...draft, gpa: e.target.value })}/></label><label><span>IELTS / English test</span><input value={draft.ielts} onChange={(e) => setDraft({ ...draft, ielts: e.target.value })}/></label><label className="span-two"><span>Professional experience</span><input value={draft.experience} onChange={(e) => setDraft({ ...draft, experience: e.target.value })}/></label></div>
        </div>}
        {step === 2 && <div className="onboarding-step"><div className="eyebrow">Step 2 · Study goals</div><h1>What are you aiming for?</h1><div className="choice-group"><span>Target degree</span><div>{degreeTargets.map((target) => <button key={target} className={draft.target === target ? "choice-active" : ""} onClick={() => setDraft({ ...draft, target })}>{target}{draft.target === target && <Check size={14}/>}</button>)}</div></div><div className="choice-group"><span>Primary field</span><div>{fields.map((field) => <button key={field} className={draft.field === field ? "choice-active" : ""} onClick={() => setDraft({ ...draft, field })}>{field}{draft.field === field && <Check size={14}/>}</button>)}</div></div></div>}
        {step === 3 && <div className="onboarding-step"><div className="eyebrow">Step 3 · Destinations</div><h1>Where could your path take you?</h1><p>Select as many as you would realistically consider.</p><div className="destination-choice-grid">{destinations.map((destination) => <button key={destination} className={draft.destinations.includes(destination) ? "destination-choice-active" : ""} onClick={() => toggleDestination(destination)}><MapPin size={17}/><span>{destination}</span>{draft.destinations.includes(destination) && <Check size={15}/>}</button>)}</div></div>}
        {step === 4 && <div className="onboarding-step onboarding-result"><div className="result-orbit"><span>{matchesEstimate}</span><small>potential matches</small></div><div className="eyebrow">Step 4 · First analysis</div><h1>Your profile is ready to work.</h1><p>OmerPath can now show a ranked shortlist, explain why each opportunity fits, and flag what needs attention.</p><div className="result-summary"><span><b>{draft.target}</b> target degree</span><span><b>{draft.destinations.length}</b> destinations</span><span><b>{draft.ielts || "Not added"}</b> English score</span></div><div className="prototype-data-note">Match scores and deadlines are estimates until verified against the official source.</div></div>}

        <div className="onboarding-actions"><button className="button-secondary" onClick={() => step === 1 ? navigate("/") : setStep((value) => value - 1)}><ArrowLeft size={15}/>{step === 1 ? "Back home" : "Back"}</button><button className="button-primary" onClick={next}>{step === 4 ? "Show my matches" : "Continue"}<ArrowRight size={15}/></button></div>
      </div>
    </section>
  </main>;
}

import { ArrowRight, Compass } from "lucide-react";
import { Link } from "wouter";

export default function NotFound() {
  return <main className="min-h-screen bg-paper px-5 text-ink flex items-center justify-center"><div className="empty-state mt-0 w-full max-w-2xl"><div className="eyebrow">404 · Route not found</div><Compass size={34} className="mt-5 text-saffron"/><h1 className="mt-5 font-display text-4xl tracking-[-.05em]">This path isn’t on the map.</h1><p className="mt-3 max-w-md text-sm leading-relaxed">Return to OmerPath and continue from the public site or your scholarship workspace.</p><div className="mt-5 flex flex-wrap justify-center gap-2"><Link href="/" className="button-secondary">Public site</Link><Link href="/dashboard" className="button-primary">Open workspace <ArrowRight size={14}/></Link></div></div></main>;
}

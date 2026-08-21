import { AlertTriangle, RotateCcw } from "lucide-react";
import { Component, ReactNode } from "react";

interface Props { children: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error: Error): State { return { hasError: true, error }; }
  render() {
    if (this.state.hasError) return <main className="min-h-screen bg-paper px-5 text-ink flex items-center justify-center"><div className="empty-state mt-0 w-full max-w-2xl"><AlertTriangle size={34} className="text-saffron"/><h1 className="mt-5 font-display text-3xl tracking-[-.04em]">Something went wrong.</h1><p className="mt-3 max-w-lg text-xs leading-relaxed">Reload the page to try again. Your data is stored only in this browser.</p><button onClick={() => window.location.reload()} className="button-primary mt-4"><RotateCcw size={15}/> Reload page</button></div></main>;
    return this.props.children;
  }
}
export default ErrorBoundary;

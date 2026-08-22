import { Toaster } from "sonner";
import Landing from "@/pages/Landing";
import Home from "@/pages/Home";
import Auth from "@/pages/Auth";
import Onboarding from "@/pages/Onboarding";
import NotFound from "@/pages/NotFound";
import AuthCallback from "@/pages/AuthCallback";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import RequireAuth from "./components/RequireAuth";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import { AcademicProfileProvider } from "./contexts/AcademicProfileContext";
import { SavedScholarshipsProvider } from "./contexts/SavedScholarshipsContext";
import { ApplicationsProvider } from "./contexts/ApplicationsContext";
import { DocumentsProvider } from "./contexts/DocumentsContext";
import { NotificationsProvider } from "./contexts/NotificationsContext";
import { SettingsProvider } from "./contexts/SettingsContext";

const workspaceRoutes = [
  "/dashboard",
  "/dashboard/scholarships",
  "/dashboard/applications",
  "/dashboard/passport",
  "/dashboard/advisor",
  "/dashboard/resources",
  "/dashboard/notifications",
  "/dashboard/profile",
  "/dashboard/settings",
] as const;

function Router() {
  return <Switch>
    <Route path="/" component={Landing}/>
    <Route path="/login">{() => <Auth mode="login"/>}</Route>
    <Route path="/signup">{() => <Auth mode="signup"/>}</Route>
    <Route path="/auth/callback" component={AuthCallback}/>
    <Route path="/forgot-password">{() => <Auth mode="forgot"/>}</Route>
    <Route path="/reset-password">{() => <RequireAuth><Auth mode="reset"/></RequireAuth>}</Route>
    <Route path="/onboarding">{() => <RequireAuth><Onboarding/></RequireAuth>}</Route>
    <Route path="/dashboard/scholarships/:id">{() => <RequireAuth><Home/></RequireAuth>}</Route>
    {workspaceRoutes.map((path) => <Route key={path} path={path}>{() => <RequireAuth><Home/></RequireAuth>}</Route>)}
    <Route component={NotFound}/>
  </Switch>;
}

export default function App() {
  return <ErrorBoundary><ThemeProvider defaultTheme="light"><AuthProvider><AcademicProfileProvider><SavedScholarshipsProvider><ApplicationsProvider><DocumentsProvider><NotificationsProvider><SettingsProvider><Toaster position="top-right" richColors/><Router/></SettingsProvider></NotificationsProvider></DocumentsProvider></ApplicationsProvider></SavedScholarshipsProvider></AcademicProfileProvider></AuthProvider></ThemeProvider></ErrorBoundary>;
}

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { BRAND } from "@/lib/brand";

type ApplicationStatus = "Preparing" | "Ready to apply" | "Submitted";

type Application = {
  id: string;
  scholarshipId: string;
  status: ApplicationStatus;
  progress: number;
  nextAction: string;
};

type DocumentItem = {
  id: string;
  name: string;
  detail: string;
  status: "Verified" | "Ready" | "Needed" | "Draft";
};

type Profile = {
  name: string;
  nationality: string;
  degree: string;
  gpa: string;
  target: string;
  ielts: string;
  experience: string;
  field: string;
  destinations: string[];
};

type Settings = {
  deadlineReminders: boolean;
  eligibilityChanges: boolean;
  advisorNudges: boolean;
  weeklyDigest: boolean;
  shareAnalytics: boolean;
};

type PrototypeContextType = {
  saved: string[];
  toggleSave: (id: string) => void;
  applications: Application[];
  updateApplicationStatus: (id: string, status: ApplicationStatus) => void;
  documents: DocumentItem[];
  addDocument: (name: string, size?: number) => void;
  profile: Profile;
  updateProfile: (updates: Partial<Profile>) => void;
  settings: Settings;
  updateSetting: (key: keyof Settings, value: boolean) => void;
  notificationsRead: string[];
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
};

const defaultProfile: Profile = {
  ...BRAND.student,
  field: "Computer Science & AI",
  destinations: ["United Kingdom", "Germany", "Multiple Countries"],
};

const defaultApplications: Application[] = [
  { id: "app-chevening", scholarshipId: "chevening", status: "Preparing", progress: 72, nextAction: "Secure recommendation letter" },
  { id: "app-erasmus", scholarshipId: "erasmus", status: "Ready to apply", progress: 91, nextAction: "Final review of motivation statement" },
  { id: "app-daad", scholarshipId: "daad", status: "Preparing", progress: 58, nextAction: "Select qualifying course" },
];

const defaultDocuments: DocumentItem[] = [
  { id: "doc-cv", name: "Curriculum vitae", detail: "PDF · updated 12 Aug 2026", status: "Ready" },
  { id: "doc-transcript", name: "Academic transcript", detail: "PDF · verified", status: "Verified" },
  { id: "doc-ielts", name: "IELTS test report", detail: "Overall 7.5 · verified", status: "Verified" },
  { id: "doc-recommendation", name: "Recommendation letter", detail: "Needed for 2 high-priority matches", status: "Needed" },
  { id: "doc-sop", name: "Statement of purpose", detail: "Draft · 62% complete", status: "Draft" },
];

const defaultSettings: Settings = {
  deadlineReminders: true,
  eligibilityChanges: true,
  advisorNudges: true,
  weeklyDigest: false,
  shareAnalytics: false,
};

const PrototypeContext = createContext<PrototypeContextType | null>(null);

function readStorage<T>(key: string, fallback: T): T {
  try {
    const value = window.localStorage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
}

export function PrototypeProvider({ children }: { children: React.ReactNode }) {
  const [saved, setSaved] = useState<string[]>(() => readStorage("omerpath-saved", ["chevening", "erasmus"]));
  const [applications, setApplications] = useState<Application[]>(() => readStorage("omerpath-applications", defaultApplications));
  const [documents, setDocuments] = useState<DocumentItem[]>(() => readStorage("omerpath-documents", defaultDocuments));
  const [profile, setProfile] = useState<Profile>(() => readStorage("omerpath-profile", defaultProfile));
  const [settings, setSettings] = useState<Settings>(() => readStorage("omerpath-settings", defaultSettings));
  const [notificationsRead, setNotificationsRead] = useState<string[]>(() => readStorage("omerpath-notification-read", []));

  useEffect(() => window.localStorage.setItem("omerpath-saved", JSON.stringify(saved)), [saved]);
  useEffect(() => window.localStorage.setItem("omerpath-applications", JSON.stringify(applications)), [applications]);
  useEffect(() => window.localStorage.setItem("omerpath-documents", JSON.stringify(documents)), [documents]);
  useEffect(() => window.localStorage.setItem("omerpath-profile", JSON.stringify(profile)), [profile]);
  useEffect(() => window.localStorage.setItem("omerpath-settings", JSON.stringify(settings)), [settings]);
  useEffect(() => window.localStorage.setItem("omerpath-notification-read", JSON.stringify(notificationsRead)), [notificationsRead]);

  const value = useMemo<PrototypeContextType>(() => ({
    saved,
    toggleSave: (id) => setSaved((prev) => prev.includes(id) ? prev.filter((value) => value !== id) : [...prev, id]),
    applications,
    updateApplicationStatus: (id, status) => setApplications((prev) => prev.map((app) => app.id === id ? {
      ...app,
      status,
      progress: status === "Submitted" ? 100 : status === "Ready to apply" ? Math.max(app.progress, 90) : Math.min(app.progress, 89),
      nextAction: status === "Submitted" ? "Track result and correspondence" : status === "Ready to apply" ? "Submit when final checks are complete" : app.nextAction,
    } : app)),
    documents,
    addDocument: (name, size) => setDocuments((prev) => [{
      id: `doc-${Date.now()}`,
      name,
      detail: `${size ? `${Math.max(1, Math.round(size / 1024))} KB` : "Uploaded"} · added`,
      status: "Ready",
    }, ...prev]),
    profile,
    updateProfile: (updates) => setProfile((prev) => ({ ...prev, ...updates })),
    settings,
    updateSetting: (key, value) => setSettings((prev) => ({ ...prev, [key]: value })),
    notificationsRead,
    markNotificationRead: (id) => setNotificationsRead((prev) => prev.includes(id) ? prev : [...prev, id]),
    markAllNotificationsRead: () => setNotificationsRead(["n1", "n2", "n3", "n4"]),
  }), [saved, applications, documents, profile, settings, notificationsRead]);

  return <PrototypeContext.Provider value={value}>{children}</PrototypeContext.Provider>;
}

export function usePrototype() {
  const value = useContext(PrototypeContext);
  if (!value) throw new Error("usePrototype must be used inside PrototypeProvider");
  return value;
}

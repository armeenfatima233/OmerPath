import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export type ApplicationStatus = "Preparing" | "Ready to apply" | "Submitted";

export type Application = {
  id: string;
  scholarshipId: string;
  status: ApplicationStatus;
  progress: number;
  nextAction: string;
};

type ApiApplication = {
  id: string;
  scholarship_id: string;
  status: ApplicationStatus;
  progress: number;
  next_action: string | null;
};

function toApplication(record: ApiApplication): Application {
  return {
    id: record.id,
    scholarshipId: record.scholarship_id,
    status: record.status,
    progress: record.progress,
    nextAction: record.next_action ?? "",
  };
}

type ApplicationsContextValue = {
  applications: Application[];
  updateApplicationStatus: (id: string, status: ApplicationStatus) => void;
  startApplication: (scholarshipId: string) => Promise<Application>;
};

const ApplicationsContext = createContext<ApplicationsContextValue | null>(null);

export function ApplicationsProvider({ children }: { children: React.ReactNode }) {
  const { status } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);

  const load = useCallback(async () => {
    const response = await apiFetch("/api/applications");
    if (!response.ok) return;
    const data: ApiApplication[] = await response.json();
    setApplications(data.map(toApplication));
  }, []);

  useEffect(() => {
    if (status === "authenticated") {
      void load();
    } else if (status === "unauthenticated") {
      setApplications([]);
    }
  }, [status, load]);

  const updateApplicationStatus = useCallback((id: string, nextStatus: ApplicationStatus) => {
    const previous = applications;
    setApplications((prev) => prev.map((app) => app.id === id ? { ...app, status: nextStatus } : app));
    apiFetch(`/api/applications/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: nextStatus }),
    })
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to update application");
        const data: ApiApplication = await response.json();
        setApplications((prev) => prev.map((app) => app.id === id ? toApplication(data) : app));
      })
      .catch(() => setApplications(previous));
  }, [applications]);

  const startApplication = useCallback(async (scholarshipId: string) => {
    const response = await apiFetch("/api/applications", {
      method: "POST",
      body: JSON.stringify({ scholarship_id: scholarshipId }),
    });
    if (!response.ok) throw new Error("Unable to start application");
    const data: ApiApplication = await response.json();
    const application = toApplication(data);
    setApplications((prev) => prev.some((app) => app.id === application.id) ? prev : [...prev, application]);
    return application;
  }, []);

  return <ApplicationsContext.Provider value={{ applications, updateApplicationStatus, startApplication }}>{children}</ApplicationsContext.Provider>;
}

export function useApplications() {
  const value = useContext(ApplicationsContext);
  if (!value) throw new Error("useApplications must be used inside ApplicationsProvider");
  return value;
}

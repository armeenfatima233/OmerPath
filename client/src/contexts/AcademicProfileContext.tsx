import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export type AcademicProfile = {
  current_degree: string | null;
  field_of_study: string | null;
  target_degree: string | null;
  gpa: string | null;
  language_test_type: string | null;
  language_test_score: string | null;
  experience_summary: string | null;
  preferred_destinations: string[];
  onboarding_completed_at: string | null;
};

export type AcademicProfileUpdate = Partial<Omit<AcademicProfile, "onboarding_completed_at">> & {
  onboarding_completed?: boolean;
};

type AcademicProfileContextValue = {
  academicProfile: AcademicProfile | null;
  loadAcademicProfile: () => Promise<AcademicProfile | null>;
  saveAcademicProfile: (updates: AcademicProfileUpdate) => Promise<AcademicProfile>;
};

const AcademicProfileContext = createContext<AcademicProfileContextValue | null>(null);

export function AcademicProfileProvider({ children }: { children: React.ReactNode }) {
  const { status } = useAuth();
  const [academicProfile, setAcademicProfile] = useState<AcademicProfile | null>(null);

  const loadAcademicProfile = useCallback(async () => {
    const response = await apiFetch("/api/academic-profile/me");
    if (!response.ok) return null;
    const data: AcademicProfile = await response.json();
    setAcademicProfile(data);
    return data;
  }, []);

  const saveAcademicProfile = useCallback(async (updates: AcademicProfileUpdate) => {
    const response = await apiFetch("/api/academic-profile/me", {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error("Unable to save academic profile");
    const data: AcademicProfile = await response.json();
    setAcademicProfile(data);
    return data;
  }, []);

  useEffect(() => {
    if (status === "authenticated") {
      void loadAcademicProfile();
    } else if (status === "unauthenticated") {
      setAcademicProfile(null);
    }
  }, [status, loadAcademicProfile]);

  return <AcademicProfileContext.Provider value={{ academicProfile, loadAcademicProfile, saveAcademicProfile }}>{children}</AcademicProfileContext.Provider>;
}

export function useAcademicProfile() {
  const value = useContext(AcademicProfileContext);
  if (!value) throw new Error("useAcademicProfile must be used inside AcademicProfileProvider");
  return value;
}

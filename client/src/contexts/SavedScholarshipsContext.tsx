import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

type SavedScholarshipsResponse = { scholarship_ids: string[] };

type SavedScholarshipsContextValue = {
  saved: string[];
  toggleSave: (id: string) => void;
};

const SavedScholarshipsContext = createContext<SavedScholarshipsContextValue | null>(null);

export function SavedScholarshipsProvider({ children }: { children: React.ReactNode }) {
  const { status } = useAuth();
  const [saved, setSaved] = useState<string[]>([]);

  const load = useCallback(async () => {
    const response = await apiFetch("/api/saved-scholarships");
    if (!response.ok) return;
    const data: SavedScholarshipsResponse = await response.json();
    setSaved(data.scholarship_ids);
  }, []);

  useEffect(() => {
    if (status === "authenticated") {
      void load();
    } else if (status === "unauthenticated") {
      setSaved([]);
    }
  }, [status, load]);

  const toggleSave = useCallback((id: string) => {
    const isSaved = saved.includes(id);
    setSaved(isSaved ? saved.filter((value) => value !== id) : [...saved, id]);
    apiFetch(`/api/saved-scholarships/${id}`, { method: isSaved ? "DELETE" : "POST" })
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to update saved scholarships");
        const data: SavedScholarshipsResponse = await response.json();
        setSaved(data.scholarship_ids);
      })
      .catch(() => setSaved(saved));
  }, [saved]);

  return <SavedScholarshipsContext.Provider value={{ saved, toggleSave }}>{children}</SavedScholarshipsContext.Provider>;
}

export function useSavedScholarships() {
  const value = useContext(SavedScholarshipsContext);
  if (!value) throw new Error("useSavedScholarships must be used inside SavedScholarshipsProvider");
  return value;
}

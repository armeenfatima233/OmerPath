import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export type Settings = {
  deadlineReminders: boolean;
  eligibilityChanges: boolean;
  advisorNudges: boolean;
  weeklyDigest: boolean;
  shareAnalytics: boolean;
};

type ApiSettings = {
  deadline_reminders: boolean;
  eligibility_changes: boolean;
  advisor_nudges: boolean;
  weekly_digest: boolean;
  share_analytics: boolean;
};

const DEFAULT_SETTINGS: Settings = {
  deadlineReminders: true,
  eligibilityChanges: true,
  advisorNudges: true,
  weeklyDigest: false,
  shareAnalytics: false,
};

function toSettings(record: ApiSettings): Settings {
  return {
    deadlineReminders: record.deadline_reminders,
    eligibilityChanges: record.eligibility_changes,
    advisorNudges: record.advisor_nudges,
    weeklyDigest: record.weekly_digest,
    shareAnalytics: record.share_analytics,
  };
}

const FIELD_MAP: Record<keyof Settings, keyof ApiSettings> = {
  deadlineReminders: "deadline_reminders",
  eligibilityChanges: "eligibility_changes",
  advisorNudges: "advisor_nudges",
  weeklyDigest: "weekly_digest",
  shareAnalytics: "share_analytics",
};

type SettingsContextValue = {
  settings: Settings;
  updateSetting: (key: keyof Settings, value: boolean) => void;
};

const SettingsContext = createContext<SettingsContextValue | null>(null);

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const { status } = useAuth();
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);

  const load = useCallback(async () => {
    const response = await apiFetch("/api/settings");
    if (!response.ok) return;
    const data: ApiSettings = await response.json();
    setSettings(toSettings(data));
  }, []);

  useEffect(() => {
    if (status === "authenticated") {
      void load();
    } else if (status === "unauthenticated") {
      setSettings(DEFAULT_SETTINGS);
    }
  }, [status, load]);

  const updateSetting = useCallback((key: keyof Settings, value: boolean) => {
    const previous = settings;
    setSettings((prev) => ({ ...prev, [key]: value }));
    apiFetch("/api/settings", {
      method: "PATCH",
      body: JSON.stringify({ [FIELD_MAP[key]]: value }),
    })
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to update settings");
        const data: ApiSettings = await response.json();
        setSettings(toSettings(data));
      })
      .catch(() => setSettings(previous));
  }, [settings]);

  return <SettingsContext.Provider value={{ settings, updateSetting }}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const value = useContext(SettingsContext);
  if (!value) throw new Error("useSettings must be used inside SettingsProvider");
  return value;
}

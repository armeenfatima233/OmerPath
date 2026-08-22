import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { Scholarship } from "@/lib/brand";

type ApiScholarship = {
  id: string;
  name: string;
  provider_name: string;
  description: string | null;
  funding_type: string | null;
  coverage: string[];
  degree_levels: string[];
  fields_of_study: string[];
  destinations: string[];
  eligibility_notes: string | null;
  deadline_at: string | null;
  deadline_note: string | null;
  official_source_url: string | null;
  application_url: string | null;
  source_label: string | null;
  last_verified_at: string | null;
  fit_reasons: string[];
  attention_points: string[];
};

type ApiMatch = {
  scholarship_id: string;
  eligibility_status: "eligible" | "ineligible" | "unknown";
  match_score: number | null;
  matched_criteria: string[];
  unmet_criteria: string[];
  unknown_criteria: string[];
};

const STATUS_NOTE: Record<ApiMatch["eligibility_status"], string> = {
  eligible: "Our records indicate you meet this scholarship's verified eligibility criteria.",
  ineligible: "Our records indicate you do not meet at least one hard eligibility requirement for this scholarship.",
  unknown: "Eligibility could not be fully verified — some requirements are unknown or not yet recorded in your profile.",
};

function formatDate(iso: string | null): string | null {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

function toScholarship(record: ApiScholarship, match: ApiMatch | undefined): Scholarship {
  const statusNote = match ? STATUS_NOTE[match.eligibility_status] : null;
  const fitReasons = match?.matched_criteria ?? [];
  const attention = [...(match?.unmet_criteria ?? []), ...(match?.unknown_criteria ?? [])];
  return {
    id: record.id,
    name: record.name,
    provider: record.provider_name,
    country: record.destinations.join(", ") || "Not specified",
    degree: record.degree_levels.join(", ") || "Not specified",
    funding: (record.funding_type as Scholarship["funding"]) ?? "Fully Funded",
    match: match?.match_score ?? null,
    eligibilityStatus: match?.eligibility_status ?? null,
    deadline: formatDate(record.deadline_at) ?? "See official website",
    deadlineNote: record.deadline_note ?? "",
    eligibility: record.eligibility_notes ?? "",
    fields: record.fields_of_study,
    sourceLabel: record.source_label ?? "Official programme website",
    lastChecked: formatDate(record.last_verified_at) ?? "Not yet verified",
    summary: record.description ?? "",
    fitReasons: statusNote && match?.eligibility_status === "eligible" ? [statusNote, ...fitReasons] : fitReasons,
    attention: statusNote && match?.eligibility_status !== "eligible" ? [statusNote, ...attention] : attention,
    coverage: record.coverage,
  };
}

export function useScholarships() {
  const [scholarships, setScholarships] = useState<Scholarship[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const response = await apiFetch("/api/scholarships");
        if (!response.ok) throw new Error("Unable to load scholarships");
        const data: { items: ApiScholarship[] } = await response.json();

        let matches: Record<string, ApiMatch> = {};
        try {
          const matchResponse = await apiFetch("/api/matches");
          if (matchResponse.ok) {
            const matchData: { items: ApiMatch[] } = await matchResponse.json();
            matches = Object.fromEntries(matchData.items.map((m) => [m.scholarship_id, m]));
          }
        } catch {
          // Not authenticated (e.g. public landing page) or match service unavailable —
          // scholarships still render without personalized match data.
        }

        if (!cancelled) setScholarships(data.items.map((item) => toScholarship(item, matches[item.id])));
      } catch {
        if (!cancelled) setError("Unable to load scholarships. Please try again.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { scholarships, loading, error };
}

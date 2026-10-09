import type { IntakeResponse, PatientDetail, RecordEntrySummary } from "@/lib/contracts";
import type { RecordEntryDetail } from "@/lib/contracts";

type DashboardPayload = {
  patient: PatientDetail;
  entries: RecordEntrySummary[];
  intake: IntakeResponse;
};

const FALLBACK_API_BASE_URL = "http://localhost:8000";

function getApiBaseUrl() {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  return configured || FALLBACK_API_BASE_URL;
}

async function safeJson<T>(response: Response): Promise<T | null> {
  if (!response.ok) {
    return null;
  }

  try {
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

async function fetchJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      cache: "no-store"
    });
    return await safeJson<T>(response);
  } catch {
    return null;
  }
}

export async function fetchDashboardData(): Promise<DashboardPayload | null> {
  return fetchJson<DashboardPayload>("/api/v1/dashboard");
}

export async function fetchPatientById(id: string): Promise<PatientDetail | null> {
  return fetchJson<PatientDetail>(`/api/v1/patients/${id}`);
}

export async function fetchPatientTimeline(id: string): Promise<RecordEntrySummary[] | null> {
  return fetchJson<RecordEntrySummary[]>(`/api/v1/patients/${id}/entries`);
}

export async function fetchEntryById(id: string): Promise<RecordEntryDetail | null> {
  return fetchJson<RecordEntryDetail>(`/api/v1/entries/${id}`);
}
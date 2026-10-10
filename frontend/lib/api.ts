import type {
  EvalRunResponse,
  IntakeResponse,
  PatientDetail,
  PatientSummary,
  QrPayload,
  RecordEntryDetail,
  RecordEntrySummary,
} from "@/lib/contracts";

type DashboardPayload = {
  patient: PatientDetail;
  entries: RecordEntrySummary[];
  intake: IntakeResponse;
};

const FALLBACK_API_BASE_URL = "http://localhost:8000";

export function getApiBaseUrl() {
  const configured = (
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_URL
  )?.trim();
  if (configured) {
    return configured.replace(/\/api\/v1\/?$/, "").replace(/\/+$/, "");
  }
  return FALLBACK_API_BASE_URL;
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

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T | null> {
  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      cache: "no-store",
      ...options,
    });
    return await safeJson<T>(response);
  } catch {
    return null;
  }
}

export async function fetchHealth(): Promise<{ status: string; service: string; model: string } | null> {
  return fetchJson("/api/v1/health");
}

export async function fetchDashboardData(): Promise<DashboardPayload | null> {
  return fetchJson<DashboardPayload>("/api/v1/dashboard");
}

export async function fetchPatients(): Promise<PatientSummary[] | null> {
  return fetchJson<PatientSummary[]>("/api/v1/patients");
}

export async function fetchPatientById(id: string): Promise<PatientDetail | null> {
  return fetchJson<PatientDetail>(`/api/v1/patients/${id}`);
}

export async function fetchPatientRecord(
  id: string
): Promise<{ patient: PatientDetail; entries: RecordEntrySummary[] } | null> {
  return fetchJson<{ patient: PatientDetail; entries: RecordEntrySummary[] }>(`/api/v1/patients/${id}/record`);
}

export async function fetchPatientTimeline(id: string): Promise<RecordEntrySummary[] | null> {
  const record = await fetchPatientRecord(id);
  return record ? record.entries : null;
}

export async function fetchEntryById(patientId: string, entryId: string): Promise<RecordEntryDetail | null> {
  return fetchJson<RecordEntryDetail>(`/api/v1/patients/${patientId}/entries/${entryId}`);
}

export async function fetchPatientQr(id: string): Promise<QrPayload | null> {
  return fetchJson<QrPayload>(`/api/v1/patients/${id}/qr`);
}

export async function postIntakeText(text: string, useModel = false, correct = true): Promise<IntakeResponse | null> {
  return fetchJson<IntakeResponse>("/api/v1/intake/text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, use_model: useModel, correct }),
  });
}

export async function postCommitEntry(
  patientId: string,
  payload: Record<string, unknown>
): Promise<RecordEntryDetail | null> {
  return fetchJson<RecordEntryDetail>(`/api/v1/patients/${patientId}/entries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function fetchLatestEval(): Promise<EvalRunResponse | null> {
  return fetchJson<EvalRunResponse>("/api/v1/eval/latest");
}

export async function runLiveEval(useModel = false, limit?: number): Promise<EvalRunResponse | null> {
  return fetchJson<EvalRunResponse>("/api/v1/eval/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ use_model: useModel, persist: true, limit }),
  });
}

export async function fetchEvalRuns(): Promise<Array<{ run_id: string; created_at: string; total: number; exact: number }> | null> {
  return fetchJson<Array<{ run_id: string; created_at: string; total: number; exact: number }>>("/api/v1/eval/runs");
}

export type ChatbotPatient = {
  id: string;
  name: string;
  name_np?: string | null;
  sanchai_id: string;
  blood_group?: string | null;
  district?: string | null;
  allergies: string[];
  conditions: string[];
};

export type ChatbotResponse = {
  reply: string;
  patient_id?: string | null;
  patient_name?: string | null;
  safety_alerts: string[];
  attachment?: {
    filename: string;
    document_class: string;
    raw_text: string;
    concepts: Array<{
      canonical_en: string;
      canonical_np: string;
      type: string;
      surface: string;
      negated: boolean;
      tier: number;
    }>;
  } | null;
  suggested_prompts: string[];
};

export async function fetchChatbotPatients(): Promise<ChatbotPatient[] | null> {
  return fetchJson<ChatbotPatient[]>("/api/v1/chatbot/patients");
}

export async function fetchChatbotContext(patientId: string): Promise<Record<string, unknown> | null> {
  return fetchJson<Record<string, unknown>>(`/api/v1/chatbot/context/${patientId}`);
}

export async function postChatbotMessage(formData: FormData): Promise<ChatbotResponse | null> {
  try {
    const res = await fetch(`${getApiBaseUrl()}/api/v1/chatbot/message`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) return null;
    return (await res.json()) as ChatbotResponse;
  } catch {
    return null;
  }
}
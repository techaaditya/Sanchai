import {
  getEmergencySummary,
  getEntryById,
  getIntakeStudio,
  getPatientOverview,
  getScannerSession,
  getTimelineEntries,
} from "@/lib/mock-api";
import {
  fetchPatientById,
  fetchPatientRecord,
  fetchPatientQr,
  getApiBaseUrl,
} from "@/lib/api";

export async function loadDashboardData() {
  try {
    const live = await fetchPatientRecord("patient_ram");
    if (live && live.patient) {
      const overview = await getPatientOverview();
      return {
        patient: live.patient,
        entries: live.entries,
        intake: overview.intake,
        timeline: live.entries,
      };
    }
  } catch {
    // fallback
  }

  const overview = await getPatientOverview();
  return {
    patient: overview.patient,
    entries: overview.entries,
    intake: overview.intake,
    timeline: getTimelineEntries(),
  };
}

export async function loadPatientData(id: string) {
  try {
    const live = await fetchPatientRecord(id);
    if (live && live.patient) {
      return {
        patient: live.patient,
        timeline: live.entries,
      };
    }
  } catch {
    // fallback
  }

  const overview = await getPatientOverview();
  if (overview.patient.id === id || id === "patient_ram") {
    return {
      patient: overview.patient,
      timeline: getTimelineEntries(),
    };
  }
  return null;
}

export async function loadEntryData(id: string) {
  try {
    const res = await fetch(`${getApiBaseUrl()}/api/v1/entries/${id}`, { cache: "no-store" });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // fallback
  }
  return getEntryById(id);
}

export async function loadEmergencySummary(token: string) {
  try {
    const res = await fetch(`${getApiBaseUrl()}/api/v1/emergency/${token}`, { cache: "no-store" });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // fallback
  }
  const overview = getEmergencySummary();
  if (overview.qrPayload.qr_token === token || token.length >= 8) {
    return overview;
  }
  return null;
}

export async function loadIntakeStudio() {
  return getIntakeStudio();
}

export async function loadScannerSession() {
  return getScannerSession();
}
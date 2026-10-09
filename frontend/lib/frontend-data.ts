import { getEmergencySummary, getEntryById, getPatientOverview, getTimelineEntries } from "@/lib/mock-api";

export async function loadDashboardData() {
  const overview = await getPatientOverview();

  return {
    patient: overview.patient,
    entries: overview.entries,
    intake: overview.intake,
    timeline: getTimelineEntries()
  };
}

export async function loadPatientData(id: string) {
  const overview = await getPatientOverview();
  if (overview.patient.id !== id) {
    return null;
  }

  return {
    patient: overview.patient,
    timeline: getTimelineEntries()
  };
}

export async function loadEntryData(id: string) {
  return getEntryById(id);
}

export async function loadEmergencySummary(token: string) {
  const overview = getEmergencySummary();
  if (overview.qrPayload.qr_token !== token) {
    return null;
  }
  return overview;
}
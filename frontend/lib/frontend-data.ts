import { fetchDashboardData, fetchEntryById, fetchPatientById, fetchPatientTimeline } from "@/lib/api";
import { getEntryById, getPatientOverview, getTimelineEntries } from "@/lib/mock-api";

export async function loadDashboardData() {
  const remote = await fetchDashboardData();

  if (remote) {
    return {
      patient: remote.patient,
      entries: remote.entries,
      intake: remote.intake,
      timeline: remote.entries
    };
  }

  const overview = await getPatientOverview();

  return {
    patient: overview.patient,
    entries: overview.entries,
    intake: overview.intake,
    timeline: getTimelineEntries()
  };
}

export async function loadPatientData(id: string) {
  const [patient, timeline] = await Promise.all([
    fetchPatientById(id),
    fetchPatientTimeline(id)
  ]);

  if (patient && timeline) {
    return {
      patient,
      timeline
    };
  }

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
  const remote = await fetchEntryById(id);

  if (remote) {
    return remote;
  }

  return getEntryById(id);
}
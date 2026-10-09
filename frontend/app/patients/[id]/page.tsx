import { notFound } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { loadPatientData } from "@/lib/frontend-data";

type PatientPageProps = {
  params: Promise<{ id: string }>;
};

export default async function PatientPage({ params }: PatientPageProps) {
  const { id } = await params;
  const data = await loadPatientData(id);

  if (!data) {
    notFound();
  }

  const { patient, timeline } = data;
  const latestEntry = timeline[0] ?? null;

  return (
    <DashboardShell>
      <section className="panel panel--paper">
        <div className="panel__inner">
          <span className="eyebrow">Patient record</span>
          <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.8rem)" }}>
            {patient.name_np ?? patient.name}
          </h1>
          <p className="lede">
            {patient.sanchai_id} · {patient.blood_group ?? "Unknown blood group"} · {patient.district}
          </p>

          <div className="metrics">
            <article className="metric metric--neutral">
              <span className="metric__label">Entries</span>
              <div className="metric__value">{patient.entry_count}</div>
            </article>
            <article className="metric metric--positive">
              <span className="metric__label">Latest intake</span>
              <div className="metric__value">{latestEntry?.document_class ?? "N/A"}</div>
            </article>
            <article className="metric metric--warning">
              <span className="metric__label">Approval gate</span>
              <div className="metric__value">Required</div>
            </article>
          </div>
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Confirmed details</p>
        <div className="timeline">
          <article className="timeline-item">
            <div className="timeline-item__top">
              <span className="timeline-item__label">Allergies</span>
              <span className="tag tag--review">{patient.allergies.length}</span>
            </div>
            <p className="timeline-item__summary">
              {patient.allergies.map((allergy) => allergy.substance_np ?? allergy.substance_en).join(", ")}
            </p>
          </article>

          <article className="timeline-item">
            <div className="timeline-item__top">
              <span className="timeline-item__label">Active conditions</span>
              <span className="tag tag--committed">{patient.conditions.length}</span>
            </div>
            <p className="timeline-item__summary">
              {patient.conditions.map((condition) => condition.canonical_np).join(", ")}
            </p>
          </article>
        </div>
      </section>
    </DashboardShell>
  );
}
import { notFound } from "next/navigation";
import Link from "next/link";
import { DashboardShell } from "@/components/dashboard-shell";
import { loadPatientData } from "@/lib/frontend-data";
import { getApiBaseUrl } from "@/lib/api";

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

          <div className="actions" style={{ marginTop: 24, alignItems: "center" }}>
            <Link className="button button--primary" href={`/emergency/${patient.qr_token}`}>
              Open emergency summary
            </Link>
            <Link className="button button--secondary" href={`/chatbot?patient=${patient.id}`}>
              💬 Consult SanchAI Assistant
            </Link>
            <a
              className="button button--secondary"
              href={`${getApiBaseUrl()}/api/v1/patients/${patient.id}/summary.pdf`}
              target="_blank"
              rel="noopener noreferrer"
            >
              📄 Download Doctor Summary PDF
            </a>
            <a
              className="button button--secondary"
              href={`${getApiBaseUrl()}/api/v1/patients/${patient.id}/fhir`}
              target="_blank"
              rel="noopener noreferrer"
            >
              ⚡ View HL7 FHIR R4 Bundle
            </a>
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

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Recent timeline</p>
        <div className="timeline">
          {timeline.map((entry) => (
            <article key={entry.id} className="timeline-item">
              <div className="timeline-item__top">
                <span className="timeline-item__label">{entry.label}</span>
                <span className={`tag tag--${entry.status}`}>
                  {entry.status === "review" ? "Needs approval" : "Committed"}
                </span>
              </div>
              <p className="timeline-item__summary">{entry.summary_np}</p>
              <div className="review-meta">
                <span>{entry.record_date}</span>
                <span>{entry.document_class ?? "entry"}</span>
              </div>
            </article>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
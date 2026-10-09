import { notFound } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { loadEmergencySummary } from "@/lib/frontend-data";

type EmergencyPageProps = {
  params: Promise<{ token: string }>;
};

export default async function EmergencyPage({ params }: EmergencyPageProps) {
  const { token } = await params;
  const data = await loadEmergencySummary(token);

  if (!data) {
    notFound();
  }

  return (
    <DashboardShell>
      <section className="panel panel--paper">
        <div className="panel__inner">
          <span className="eyebrow">Emergency summary</span>
          <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.8rem)" }}>
            {data.patient.name_np ?? data.patient.name}
          </h1>
          <p className="lede">
            Offline-friendly, shareable summary for quick viewing on a phone during urgent care.
          </p>

          <div className="metrics">
            <article className="metric metric--neutral">
              <span className="metric__label">Blood group</span>
              <div className="metric__value">{data.patient.blood_group}</div>
            </article>
            <article className="metric metric--positive">
              <span className="metric__label">QR token</span>
              <div className="metric__value">{data.qrPayload.qr_token}</div>
            </article>
            <article className="metric metric--warning">
              <span className="metric__label">Patient type</span>
              <div className="metric__value">Synthetic demo</div>
            </article>
          </div>
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Emergency highlights</p>
        <div className="timeline">
          {data.highlights.map((highlight) => (
            <article key={highlight} className="timeline-item">
              <p className="timeline-item__summary">{highlight}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Encoded payload</p>
        <div className="timeline">
          <article className="timeline-item">
            <div className="timeline-item__top">
              <span className="timeline-item__label">sanchai://p/{data.qrPayload.qr_token}</span>
              <span className="tag tag--committed">Ready</span>
            </div>
            <p className="timeline-item__summary">
              {data.qrPayload.allergies.join(", ")} · {data.qrPayload.conditions.join(", ")}
            </p>
          </article>
        </div>
      </section>
    </DashboardShell>
  );
}
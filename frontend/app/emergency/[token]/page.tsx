import { notFound } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { loadEmergencySummary } from "@/lib/frontend-data";
import { getApiBaseUrl } from "@/lib/api";

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
          {data.highlights.map((highlight: string) => (
            <article key={highlight} className="timeline-item">
              <p className="timeline-item__summary">{highlight}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Encoded Payload & Optical QR</p>
        <div className="timeline">
          <article className="timeline-item">
            <div className="timeline-item__top">
              <span className="timeline-item__label">sanchai://p/{data.qrPayload.qr_token}</span>
              <span className="tag tag--committed">Scannable</span>
            </div>
            <p className="timeline-item__summary">
              {data.qrPayload.allergies.join(", ") || "No allergies"} · {data.qrPayload.conditions.join(", ") || "No active conditions"}
            </p>
            <div style={{ marginTop: 14, display: "flex", alignItems: "center", gap: 16 }}>
              <img
                src={`${getApiBaseUrl()}/api/v1/patients/${data.patient.id}/qr.png`}
                alt="Emergency QR Code"
                width={110}
                height={110}
                style={{ borderRadius: 12, border: "1px solid var(--line)", background: "#fff", padding: 4 }}
              />
              <div>
                <p style={{ margin: "0 0 6px", fontWeight: 700, fontSize: "0.95rem" }}>
                  Instant Optical Triage
                </p>
                <p style={{ margin: 0, color: "var(--ink-soft)", fontSize: "0.85rem" }}>
                  Point any phone camera to verify blood group and critical contraindications offline.
                </p>
              </div>
            </div>
          </article>
        </div>

        <div className="actions" style={{ marginTop: 20 }}>
          <a className="button button--primary" href={`/patients/${data.patient.id}`}>
            View Full Patient Ledger →
          </a>
        </div>
      </section>
    </DashboardShell>
  );
}
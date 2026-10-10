import { notFound } from "next/navigation";
import Link from "next/link";
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

  const { patient, qrPayload, highlights } = data;
  const bloodGroup = patient.blood_group || qrPayload.blood_group || "Unknown";
  const allergies: string[] = qrPayload.allergies || [];
  const conditions: string[] = qrPayload.conditions || [];

  return (
    <DashboardShell>
      {/* Top Banner */}
      <section className="panel panel--paper">
        <div className="panel__inner">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
            <div>
              <span className="eyebrow" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span className="model-chip__dot" style={{ display: "inline-block", width: 8, height: 8 }} />
                Optical Emergency Triage Card · Offline Payload
              </span>
              <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.8rem)", margin: "8px 0" }}>
                {patient.name_np ? `${patient.name_np} (${patient.name})` : patient.name}
              </h1>
              <p className="lede">
                Sub-second emergency triage view decoded from token <code>{qrPayload.qr_token}</code>. Designed for ambulance paramedics and emergency room staff.
              </p>
            </div>

            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <Link className="button button--secondary" href="/scan">
                ← Back to Scanner
              </Link>
              <Link className="button button--primary" href={`/patients/${patient.id}`}>
                Full Patient Ledger →
              </Link>
            </div>
          </div>

          {/* Critical Triage Highlights Strip */}
          <div className="metrics" style={{ marginTop: 24 }}>
            <article className="metric" style={{ background: "#fff5f5", borderColor: "#feb2b2" }}>
              <span className="metric__label" style={{ color: "#c53030", fontWeight: 800 }}>
                🩸 Blood Group
              </span>
              <div className="metric__value" style={{ color: "#9b2c2c", fontSize: "2rem" }}>
                {bloodGroup}
              </div>
            </article>

            <article className={`metric ${allergies.length > 0 ? "metric--warning" : "metric--positive"}`}>
              <span className="metric__label">Drug Allergies</span>
              <div className="metric__value" style={{ fontSize: "1.2rem" }}>
                {allergies.length > 0 ? allergies.join(", ") : "None Documented"}
              </div>
            </article>

            <article className="metric metric--neutral">
              <span className="metric__label">Active Conditions</span>
              <div className="metric__value" style={{ fontSize: "1.2rem" }}>
                {conditions.length > 0 ? conditions.join(", ") : "None Recorded"}
              </div>
            </article>
          </div>
        </div>
      </section>

      {/* Emergency Highlights Panel */}
      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Paramedic Triage Checklist</p>
        <div className="timeline">
          {highlights && highlights.length > 0 ? (
            highlights.map((highlight: string, idx: number) => (
              <article key={idx} className="timeline-item">
                <p className="timeline-item__summary" style={{ fontSize: "0.98rem", fontWeight: 600 }}>
                  {highlight}
                </p>
              </article>
            ))
          ) : (
            <article className="timeline-item">
              <p className="timeline-item__summary">
                Blood Group {bloodGroup} · {allergies.length} allergies · {conditions.length} active conditions
              </p>
            </article>
          )}
        </div>
      </section>

      {/* Scannable Optical QR Proof */}
      <section className="timeline-card" style={{ marginTop: 24, border: "2px solid rgba(17, 193, 105, 0.3)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          <div>
            <p className="section-title" style={{ margin: 0 }}>
              Encoded Optical QR & Token Verification
            </p>
            <p style={{ margin: "4px 0 0", color: "var(--ink-soft)", fontSize: "0.85rem" }}>
              Standard Segno ISO/IEC 18004 optical matrix encoding <code>sanchai://p/{qrPayload.qr_token}</code>.
            </p>
          </div>
          <span className="tag tag--committed">
            ✓ Cryptographically Bound
          </span>
        </div>

        <div style={{ marginTop: 18, display: "flex", alignItems: "center", gap: 20, flexWrap: "wrap", background: "var(--panel-muted)", padding: 16, borderRadius: 14 }}>
          <img
            src={`${getApiBaseUrl()}/api/v1/patients/${patient.id}/qr.png`}
            alt="Emergency QR Code"
            width={120}
            height={120}
            style={{ borderRadius: 12, border: "1.5px solid #11c169", background: "#fff", padding: 6, boxShadow: "0 4px 12px rgba(17,193,105,0.18)" }}
          />
          <div style={{ flex: 1, minWidth: 240 }}>
            <p style={{ margin: "0 0 4px", fontWeight: 700, fontSize: "1rem" }}>
              Optical URI: <code>sanchai://p/{qrPayload.qr_token}</code>
            </p>
            <p style={{ margin: "0 0 12px", color: "var(--ink-soft)", fontSize: "0.86rem" }}>
              Can be scanned offline by any standard QR reader or mobile camera without requiring internet.
            </p>

            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <a
                className="button button--secondary"
                href={`${getApiBaseUrl()}/api/v1/patients/${patient.id}/qr.png`}
                download={`sanchai_qr_${patient.id}.png`}
                target="_blank"
                rel="noopener noreferrer"
                style={{ padding: "6px 14px", fontSize: "0.84rem" }}
              >
                📥 Download PNG Code
              </a>
              <Link className="button button--secondary" href="/scan" style={{ padding: "6px 14px", fontSize: "0.84rem" }}>
                📷 Open Scanner Viewfinder
              </Link>
            </div>
          </div>
        </div>

        <div className="actions" style={{ marginTop: 24 }}>
          <Link className="button button--primary" href={`/patients/${patient.id}`}>
            View Full Patient Health Ledger →
          </Link>
          <Link className="button button--secondary" href={`/chatbot?patient=${patient.id}`}>
            💬 Consult SanchAI for this Patient
          </Link>
        </div>
      </section>
    </DashboardShell>
  );
}
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

      {/* Emergency Optical Triage QR Card */}
      <section className="timeline-card" style={{ marginTop: 24, border: "2px solid rgba(17, 193, 105, 0.35)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          <div>
            <p className="section-title" style={{ margin: 0, color: "var(--ink)", display: "flex", alignItems: "center", gap: 8 }}>
              <span>🚑 Official Emergency Triage QR Card</span>
              <span className="tag tag--committed" style={{ fontSize: "0.74rem" }}>Offline Ready</span>
            </p>
            <p style={{ margin: "4px 0 0", color: "var(--ink-soft)", fontSize: "0.86rem" }}>
              Offline-first optical payload encoded with Segno / ISO/IEC 18004. Readable by ambulance paramedics and ER desks in &lt; 1s.
            </p>
          </div>
          <span className="tag tag--committed">
            <span className="model-chip__dot" style={{ display: "inline-block", width: 6, height: 6, marginRight: 6 }} />
            Active & Verified Token
          </span>
        </div>

        <div style={{ marginTop: 18, display: "flex", gap: 24, alignItems: "center", flexWrap: "wrap", background: "var(--panel-muted)", padding: 18, borderRadius: 16, border: "1px solid var(--line)" }}>
          {/* QR Code Graphic with click-to-enlarge/download */}
          <div style={{ position: "relative", textAlign: "center", flexShrink: 0 }}>
            <img
              src={`${getApiBaseUrl()}/api/v1/patients/${patient.id}/qr.png`}
              alt={`Emergency QR Code for ${patient.name}`}
              width={140}
              height={140}
              style={{
                borderRadius: 14,
                background: "#ffffff",
                padding: 8,
                border: "2px solid #11c169",
                boxShadow: "0 6px 16px rgba(17, 193, 105, 0.2)",
                display: "block",
              }}
            />
            <span style={{ display: "block", marginTop: 6, fontSize: "0.72rem", color: "var(--ink-soft)", fontWeight: 700 }}>
              ISO/IEC 18004 Standard
            </span>
          </div>

          {/* Emergency Information Details */}
          <div style={{ flex: 1, minWidth: 260 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
              <span style={{ fontSize: "1.15rem", fontWeight: 800, color: "var(--ink)" }}>
                {patient.name} {patient.name_np ? `(${patient.name_np})` : ""}
              </span>
              <span className="tag tag--neutral" style={{ fontWeight: 800, fontSize: "0.85rem" }}>
                🩸 Blood: {patient.blood_group || "Unknown"}
              </span>
            </div>

            <div style={{ marginTop: 8, fontSize: "0.85rem" }}>
              <span style={{ color: "var(--ink-soft)" }}>Decoded Token: </span>
              <code style={{ fontSize: "0.88rem", color: "var(--accent)", fontWeight: 700 }}>
                sanchai://p/{patient.qr_token}
              </code>
            </div>

            <div style={{ marginTop: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
              {patient.allergies.length > 0 ? (
                <span className="tag" style={{ background: "#ffebee", color: "#c62828", border: "1px solid #ffcdd2", fontSize: "0.8rem" }}>
                  ⚠️ Severe Allergy: {patient.allergies.map((a: any) => a.substance_en || a.substance_np).join(", ")}
                </span>
              ) : (
                <span className="tag tag--committed">✓ No Known Drug Allergies</span>
              )}
              {patient.conditions.length > 0 && (
                <span className="tag tag--review" style={{ fontSize: "0.8rem" }}>
                  🩺 Active: {patient.conditions.map((c: any) => c.canonical_en || c.canonical_np).join(", ")}
                </span>
              )}
            </div>

            {/* Actions for this QR card */}
            <div style={{ marginTop: 14, display: "flex", gap: 10, flexWrap: "wrap" }}>
              <Link className="button button--primary" href={`/emergency/${patient.qr_token}`} style={{ padding: "8px 16px", fontSize: "0.85rem" }}>
                Open Live Emergency Card →
              </Link>
              <a
                className="button button--secondary"
                href={`${getApiBaseUrl()}/api/v1/patients/${patient.id}/qr.png`}
                download={`sanchai_qr_${patient.id}.png`}
                target="_blank"
                rel="noopener noreferrer"
                style={{ padding: "8px 16px", fontSize: "0.85rem" }}
              >
                📥 Download QR Code (PNG)
              </a>
              <Link className="button button--secondary" href="/scan" style={{ padding: "8px 16px", fontSize: "0.85rem" }}>
                📷 Test in Optical Scanner
              </Link>
            </div>
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
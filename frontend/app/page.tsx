import Link from "next/link";
import { loadDashboardData } from "@/lib/frontend-data";

export default async function HomePage() {
  const { intake, patient, timeline } = await loadDashboardData();

  return (
    <main className="shell">
      <section className="hero">
        <div className="panel panel--paper">
          <div className="panel__inner">
            <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 14, flexWrap: "wrap" }}>
              <img
                src="/logo512.svg"
                alt="Sanchai App Logo"
                width={48}
                height={48}
                style={{
                  borderRadius: 14,
                  background: "#ffffff",
                  padding: 6,
                  border: "1.5px solid rgba(17, 193, 105, 0.28)",
                  boxShadow: "0 4px 14px rgba(17, 193, 105, 0.16)",
                  flexShrink: 0,
                }}
              />
              <div>
                <span className="eyebrow" style={{ margin: 0 }}>Clinical Health Ledger · Zero-Hallucination AI</span>
                <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "var(--ink)", display: "flex", alignItems: "center", gap: 8, marginTop: 2 }}>
                  <span>Sanchai (सञ्चै)</span>
                  <span className="tag tag--committed" style={{ fontSize: "0.74rem" }}>Verified Nepal DDA</span>
                </div>
              </div>
            </div>
            <h1 className="title">Paper in. Structure out.</h1>
            <p className="lede">
              Sanchai turns Nepali clinical input into a reviewed, longitudinal record.
              This first slice establishes the visual language, the intake/review split,
              and a stable surface for later backend wiring.
            </p>

            <div className="actions">
              <Link className="button button--primary" href="/evidence">
                NepClinBench Evidence (96.7%)
              </Link>
              <Link className="button button--secondary" href="/intake">
                Open intake studio
              </Link>
              <Link className="button button--secondary" href="/scan">
                Open QR scanner
              </Link>
              <Link className="button button--secondary" href={`/patients/${patient.id}`}>
                Open patient record
              </Link>
              <Link className="button button--secondary" href="/review/entry-1024">
                Open approval screen
              </Link>
              <Link className="button button--secondary" href={`/emergency/${patient.qr_token}`}>
                Open emergency summary
              </Link>
              <a className="button button--secondary" href="#review-queue">
                Open review queue
              </a>
              <a className="button button--secondary" href="#timeline">
                View record timeline
              </a>
            </div>

            <div className="metrics">
              <article className="metric metric--positive">
                <span className="metric__label">Patient</span>
                <div className="metric__value">{patient.name_np ?? patient.name}</div>
              </article>
              <article className="metric metric--neutral">
                <span className="metric__label">Lexicon coverage</span>
                <div className="metric__value">261 concepts</div>
              </article>
              <article className="metric metric--warning">
                <span className="metric__label">Safety gate</span>
                <div className="metric__value">Approval before write</div>
              </article>
            </div>
          </div>
        </div>

        <div className="workspace">
          <section id="review-queue" className="review-card">
            <p className="section-title">Review queue</p>
            <div className="review-grid">
              <div className="review-meta">
                <span>Current review queue</span>
                <span>{Math.round((intake.normalized?.concepts.length ?? 0) / 3 * 100)}% structured</span>
              </div>
              <p className="review-excerpt">{intake.corrected_text}</p>
              <div className="review-meta">
                <span>{intake.extraction_method}</span>
                <span>Approval before write</span>
              </div>
            </div>
          </section>

          <section className="status-card">
            <p className="section-title">Current operating mode</p>
            <div className="stack">
              <div className="timeline-item">
                <div className="timeline-item__top">
                  <span className="timeline-item__label">Vision + text intake</span>
                  <span className="tag tag--review">Ready</span>
                </div>
                <p className="timeline-item__summary">
                  The first release focuses on the intake-to-review loop, with backend data
                  mapped into the UI in the next phase.
                </p>
              </div>

              <div className="timeline-item">
                <div className="timeline-item__top">
                  <span className="timeline-item__label">Audio intake</span>
                  <span className="tag tag--committed">De-scoped</span>
                </div>
                <p className="timeline-item__summary">
                  Voice support stays out of this release so the frontend can stay focused
                  on the clinical document workflow.
                </p>
              </div>

              <div className="timeline-item">
                <div className="timeline-item__top">
                  <span className="timeline-item__label">Emergency QR</span>
                  <span className="tag tag--committed">Ready</span>
                </div>
                <p className="timeline-item__summary">
                  The emergency summary is available as a simple dummy-data card for quick demo flows.
                </p>
              </div>
            </div>
          </section>
        </div>
      </section>

      <section id="timeline" className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Record timeline</p>
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
                <span>{entry.input_type.toUpperCase()}</span>
                <span>{entry.id}</span>
              </div>
            </article>
          ))}
        </div>
        <p className="footer-note">
          Next phase: replace this mock data layer with real FastAPI endpoints, starting
          with intake and patient summary reads.
        </p>
      </section>
    </main>
  );
}
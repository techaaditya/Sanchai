import { intakePreview, metrics, timeline } from "@/lib/mock-data";

export default function HomePage() {
  return (
    <main className="shell">
      <section className="hero">
        <div className="panel panel--paper">
          <div className="panel__inner">
            <span className="eyebrow">Phase 1 · frontend shell</span>
            <h1 className="title">Paper in. Structure out.</h1>
            <p className="lede">
              Sanchai turns Nepali clinical input into a reviewed, longitudinal record.
              This first slice establishes the visual language, the intake/review split,
              and a stable surface for later backend wiring.
            </p>

            <div className="actions">
              <a className="button button--primary" href="#review-queue">
                Open review queue
              </a>
              <a className="button button--secondary" href="#timeline">
                View record timeline
              </a>
            </div>

            <div className="metrics">
              {metrics.map((metric) => (
                <article key={metric.label} className={`metric metric--${metric.tone}`}>
                  <span className="metric__label">{metric.label}</span>
                  <div className="metric__value">{metric.value}</div>
                </article>
              ))}
            </div>
          </div>
        </div>

        <div className="workspace">
          <section id="review-queue" className="review-card">
            <p className="section-title">Review queue</p>
            <div className="review-grid">
              <div className="review-meta">
                <span>{intakePreview.title}</span>
                <span>{Math.round(intakePreview.confidence * 100)}% confidence</span>
              </div>
              <p className="review-excerpt">{intakePreview.excerpt}</p>
              <div className="review-meta">
                <span>{intakePreview.source}</span>
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
              <p className="timeline-item__summary">{entry.summary}</p>
              <div className="review-meta">
                <span>{entry.date}</span>
                <span>{entry.mode.toUpperCase()}</span>
                <span>{entry.id}</span>
              </div>
            </article>
          ))}
        </div>
        <p className="footer-note">
          Next phase: connect these cards to backend intake, patient, and normalization
          endpoints one at a time.
        </p>
      </section>
    </main>
  );
}
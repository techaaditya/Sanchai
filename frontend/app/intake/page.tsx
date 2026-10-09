import { DashboardShell } from "@/components/dashboard-shell";
import { loadIntakeStudio } from "@/lib/frontend-data";

export default async function IntakePage() {
  const studio = await loadIntakeStudio();

  return (
    <DashboardShell>
      <section className="panel panel--paper">
        <div className="panel__inner">
          <span className="eyebrow">Intake studio</span>
          <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.8rem)" }}>
            Fast intake, clear review.
          </h1>
          <p className="lede">
            A dummy-data intake workspace for prescriptions, lab reports, and direct text.
          </p>

          <div className="metrics">
            {studio.sourceModes.map((mode) => (
              <article key={mode} className="metric metric--neutral">
                <span className="metric__label">Mode</span>
                <div className="metric__value">{mode}</div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Drop zone</p>
        <div className="timeline-item" style={{ minHeight: 220, justifyContent: "center" }}>
          <div className="timeline-item__top">
            <span className="timeline-item__label">Drag document here</span>
            <span className="tag tag--review">Dummy only</span>
          </div>
          <p className="timeline-item__summary">
            Use a prescription image, a lab PDF, or pasted clinical text. In this phase the
            interface is illustrative and uses seeded examples.
          </p>
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Review queue</p>
        <div className="timeline">
          {studio.queue.map((item) => (
            <article key={item.id} className="timeline-item">
              <div className="timeline-item__top">
                <span className="timeline-item__label">{item.title}</span>
                <span className="tag tag--committed">{item.status}</span>
              </div>
              <p className="timeline-item__summary">{item.subtitle}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Capture hints</p>
        <div className="timeline">
          {studio.documentHints.map((hint) => (
            <article key={hint} className="timeline-item">
              <p className="timeline-item__summary">{hint}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Preview text</p>
        <div className="timeline-item">
          <div className="timeline-item__top">
            <span className="timeline-item__label">{studio.preview.text}</span>
            <span className="tag tag--review">{Math.round(studio.preview.confidence * 100)}%</span>
          </div>
          <p className="timeline-item__summary">{studio.preview.prepared_text}</p>
        </div>
      </section>
    </DashboardShell>
  );
}
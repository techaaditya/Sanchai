import { DashboardShell } from "@/components/dashboard-shell";
import { loadScannerSession } from "@/lib/frontend-data";

export default async function ScanPage() {
  const session = await loadScannerSession();

  return (
    <DashboardShell>
      <section className="panel panel--paper">
        <div className="panel__inner">
          <span className="eyebrow">QR scanner</span>
          <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.8rem)" }}>
            Camera first, emergency ready.
          </h1>
          <p className="lede">
            A dummy utility page for scanning or simulating emergency QR token reads.
          </p>

          <div className="metrics">
            <article className="metric metric--neutral">
              <span className="metric__label">Last scan</span>
              <div className="metric__value">{session.lastScan.token}</div>
            </article>
            <article className="metric metric--positive">
              <span className="metric__label">Matched patient</span>
              <div className="metric__value">{session.lastScan.patientName}</div>
            </article>
            <article className="metric metric--warning">
              <span className="metric__label">Source</span>
              <div className="metric__value">{session.lastScan.source}</div>
            </article>
          </div>
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Scanner frame</p>
        <div className="timeline-item" style={{ minHeight: 280, justifyContent: "space-between" }}>
          <div className="timeline-item__top">
            <span className="timeline-item__label">Live preview placeholder</span>
            <span className="tag tag--review">Idle</span>
          </div>
          <p className="timeline-item__summary">
            This space would host the camera feed in a production build. For now it shows a
            visually clear placeholder for the QR workflow.
          </p>
          <div className="timeline-item__top">
            <span className="timeline-item__label">Current token</span>
            <span className="tag tag--committed">{session.lastScan.token}</span>
          </div>
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Recent scans</p>
        <div className="timeline">
          {session.recentScans.map((scan) => (
            <article key={scan.token} className="timeline-item">
              <div className="timeline-item__top">
                <span className="timeline-item__label">{scan.label}</span>
                <span className="tag tag--committed">Done</span>
              </div>
              <p className="timeline-item__summary">{scan.outcome}</p>
            </article>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
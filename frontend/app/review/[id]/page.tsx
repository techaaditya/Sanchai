import { notFound } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { ApprovalActions } from "@/components/approval-actions";
import { loadEntryData } from "@/lib/frontend-data";
import type { NormalizedConcept } from "@/lib/contracts";

type ReviewPageProps = {
  params: Promise<{ id: string }>;
};

export default async function ReviewPage({ params }: ReviewPageProps) {
  const { id } = await params;
  const entry = await loadEntryData(id);

  if (!entry) {
    notFound();
  }

  const normalizedConcepts: NormalizedConcept[] = entry.normalized?.concepts ?? [];

  return (
    <DashboardShell>
      <section className="panel panel--paper">
        <div className="panel__inner">
          <span className="eyebrow">Approval gate</span>
          <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.6rem)" }}>
            {entry.label}
          </h1>
          <p className="lede">
            Review the extracted text, normalized concepts, and negation flags before the
            record is committed.
          </p>

          <div className="metrics">
            <article className="metric metric--neutral">
              <span className="metric__label">Document class</span>
              <div className="metric__value">{entry.document_class ?? "Unknown"}</div>
            </article>
            <article className="metric metric--positive">
              <span className="metric__label">Concepts</span>
              <div className="metric__value">{entry.concept_count}</div>
            </article>
            <article className="metric metric--warning">
              <span className="metric__label">Negated findings</span>
              <div className="metric__value">{entry.negated_count}</div>
            </article>
          </div>
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Source text</p>
        <div className="timeline">
          <article className="timeline-item">
            <div className="timeline-item__top">
              <span className="timeline-item__label">Raw transcript</span>
              <span className="tag tag--review">{entry.extraction_method}</span>
            </div>
            <p className="timeline-item__summary">{entry.raw_transcript ?? entry.summary_np}</p>
          </article>

          <article className="timeline-item">
            <div className="timeline-item__top">
              <span className="timeline-item__label">Corrected text</span>
              <span className="tag tag--committed">Prepared</span>
            </div>
            <p className="timeline-item__summary">{entry.corrected_text ?? entry.summary_np}</p>
          </article>
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Normalized concepts</p>
        <div className="timeline">
          {normalizedConcepts.length === 0 ? (
            <article className="timeline-item">
              <p className="timeline-item__summary">No normalized concepts are attached yet.</p>
            </article>
          ) : (
            normalizedConcepts.map((concept) => (
              <article key={`${concept.concept_id}-${concept.start}`} className="timeline-item">
                <div className="timeline-item__top">
                  <span className="timeline-item__label">{concept.canonical_np}</span>
                  <span className={`tag ${concept.negated ? "tag--review" : "tag--committed"}`}>
                    Tier {concept.tier}
                  </span>
                </div>
                <p className="timeline-item__summary">
                  {concept.surface_form} · {concept.canonical_en}
                  {concept.negated ? " · negated" : ""}
                  {concept.generic ? ` · generic ${concept.generic.canonical_en}` : ""}
                </p>
              </article>
            ))
          )}
        </div>
      </section>

      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Approval</p>
        <ApprovalActions entryId={entry.id} />
        <p className="footer-note">
          This screen is the human-in-the-loop gate. The commit action writes to the seeded
          backend now, and later phases can swap it for persistence.
        </p>
      </section>
    </DashboardShell>
  );
}
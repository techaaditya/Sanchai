import type { IntakePreview, RecordMetric, TimelineEntry } from "@/lib/types";

export const metrics: RecordMetric[] = [
  { label: "Lexicon coverage", value: "261 concepts", tone: "positive" },
  { label: "Safety gate", value: "Approval before write", tone: "neutral" },
  { label: "Voice intake", value: "De-scoped", tone: "warning" }
];

export const timeline: TimelineEntry[] = [
  {
    id: "entry-1024",
    date: "2026-10-09",
    mode: "image",
    label: "Handwritten prescription",
    summary: "Cetamol 500 mg resolved to Paracetamol, with fever marked as negated.",
    status: "review"
  },
  {
    id: "entry-1023",
    date: "2026-10-08",
    mode: "pdf",
    label: "Digital lab report",
    summary: "CBC extracted directly with zero model calls and preserved values.",
    status: "committed"
  },
  {
    id: "entry-1022",
    date: "2026-10-05",
    mode: "text",
    label: "Clinic note",
    summary: "Romanized Nepali intake normalized into clinical concepts and durations.",
    status: "committed"
  }
];

export const intakePreview: IntakePreview = {
  title: "Current review queue",
  excerpt: "ज्वरो छैन, खोकी छ, सिटामोल ५०० एमजी",
  source: "Vision OCR + 3-tier normalization",
  confidence: 0.98
};
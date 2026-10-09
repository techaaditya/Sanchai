export type IntakeMode = "image" | "pdf" | "text";

export type TimelineEntry = {
  id: string;
  date: string;
  mode: IntakeMode;
  label: string;
  summary: string;
  status: "review" | "committed";
};

export type RecordMetric = {
  label: string;
  value: string;
  tone: "positive" | "neutral" | "warning";
};

export type IntakePreview = {
  title: string;
  excerpt: string;
  source: string;
  confidence: number;
};
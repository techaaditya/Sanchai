"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { DashboardShell } from "@/components/dashboard-shell";
import type { IntakeResponse, NormalizedConcept } from "@/lib/contracts";
import { getApiBaseUrl } from "@/lib/api";

const DEMO_PRESETS = [
  {
    label: "Prescription Slip (Handwritten / Mixed)",
    docClass: "prescription",
    text: `Rx
1. Tab Cetamol 500mg - 1 TDS x 3 days
2. Tab Cifran 500 - 1 BD
3. खोकी छ, ज्वरो छैन`,
  },
  {
    label: "Clinic Note (Romanized + Negation)",
    docClass: "note",
    text: `jworo chaina tara khoki cha 4 din dekhi, tauko dukhcha`,
  },
  {
    label: "Printed Lab Report (CBC)",
    docClass: "lab_report",
    text: `PATIENT: Ram Bahadur Shrestha
INVESTIGATION: Complete Blood Count (CBC)
Haemoglobin: 13.8 g/dL
Platelet Count: 210,000 /uL
Widal Test: Positive (1:160)`,
  },
];

const DEFAULT_SAMPLE_RESULT: IntakeResponse = {
  raw_transcript: `Rx\n1. Tab Cetamol 500mg - 1 TDS x 3 days\n2. Tab Cifran 500 - 1 BD\n3. खोकी छ, ज्वरो छैन`,
  corrected_text: `Rx 1. Tab Cetamol 500mg - 1 TDS x 3 days 2. Tab Cifran 500 - 1 BD 3. खोकी छ, ज्वरो छैन`,
  extraction_method: "direct",
  extraction_status: "ok",
  input_type: "text",
  document_class: "prescription",
  document_class_evidence: ["medication brands", "frequency codes"],
  corrections: [],
  unverified: [],
  notes: [
    {
      level: "info",
      message_np: "ज्वरो नकारात्मक रूपमा पहिचान गरिएको छ (अभिलेखमा समावेश हुँदैन)।",
      message_en: "Fever recognized as negated (will not be written as an active condition).",
    },
  ],
  normalized: {
    text: "Rx 1. Tab Cetamol 500mg - 1 TDS x 3 days 2. Tab Cifran 500 - 1 BD 3. खोकी छ, ज्वरो छैन",
    prepared_text: "Rx 1. Tab Cetamol 500mg - 1 TDS x 3 days 2. Tab Cifran 500 - 1 BD 3. खोकी छ, ज्वरो छैन",
    duration_days: 3,
    frequency_per_day: 3,
    unmatched: [],
    tier_counts: { "1": 3, "2": 1, "3": 0 },
    modifiers: [],
    concepts: [
      {
        concept_id: "NCL-0002",
        canonical_en: "Cough",
        canonical_np: "खोकी",
        surface_form: "खोकी",
        concept_type: "symptom",
        tier: 1,
        confidence: 1.0,
        negated: false,
        start: 72,
        end: 76,
        icd11_code: "MD11",
      },
      {
        concept_id: "NCL-0001",
        canonical_en: "Fever",
        canonical_np: "ज्वरो",
        surface_form: "ज्वरो",
        concept_type: "condition",
        tier: 1,
        confidence: 1.0,
        negated: true,
        start: 80,
        end: 85,
        icd11_code: "MG26",
      },
      {
        concept_id: "NCL-0051",
        canonical_en: "Cetamol",
        canonical_np: "सिटामोल",
        surface_form: "Cetamol",
        concept_type: "drug_brand",
        tier: 1,
        confidence: 1.0,
        negated: false,
        start: 11,
        end: 18,
        generic: {
          concept_id: "NCL-0201",
          canonical_en: "Paracetamol",
          canonical_np: "प्यारासिटामोल",
        },
      },
      {
        concept_id: "NCL-0052",
        canonical_en: "Cifran",
        canonical_np: "सिफ्रान",
        surface_form: "Cifran",
        concept_type: "drug_brand",
        tier: 1,
        confidence: 1.0,
        negated: false,
        start: 46,
        end: 52,
        generic: {
          concept_id: "NCL-0205",
          canonical_en: "Ciprofloxacin",
          canonical_np: "सिप्रोफ्लोक्सासिन",
        },
      },
    ],
  },
};

export default function IntakePage() {
  const [inputText, setInputText] = useState(DEMO_PRESETS[0].text);
  const [useModel, setUseModel] = useState(false);
  const [result, setResult] = useState<IntakeResponse | null>(DEFAULT_SAMPLE_RESULT);
  const [isProcessing, startTransition] = useTransition();
  const [commitMessage, setCommitMessage] = useState<string | null>(null);
  const [committedEntryId, setCommittedEntryId] = useState<string | null>(null);

  const runIntake = () => {
    setCommitMessage(null);
    setCommittedEntryId(null);
    startTransition(async () => {
      try {
        const response = await fetch(`${getApiBaseUrl()}/api/v1/intake/text`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: inputText,
            use_model: useModel,
            correct: true,
          }),
        });
        if (response.ok) {
          const data: IntakeResponse = await response.json();
          setResult(data);
        }
      } catch {
        // Keeps state
      }
    });
  };

  const commitToPatient = async () => {
    if (!result || !result.normalized) return;
    setCommitMessage(null);

    const payload = {
      input_type: "text",
      document_class: result.document_class || "prescription",
      facility_name: "Community Health Clinic",
      record_date: new Date().toISOString().slice(0, 10),
      raw_transcript: result.raw_transcript,
      corrected_text: result.corrected_text,
      extraction_method: result.extraction_method,
      meaning_np: "चिकित्सकीय टिपोट सफलतापूर्वक प्रशोधित गरियो।",
      normalized: {
        text: result.raw_transcript,
        prepared_text: result.corrected_text,
        concepts: result.normalized.concepts,
        modifiers: result.normalized.modifiers || [],
        duration_days: result.normalized.duration_days,
        frequency_per_day: result.normalized.frequency_per_day,
        unmatched: result.normalized.unmatched || [],
        tier_counts: result.normalized.tier_counts || { "1": 1 },
      },
      notes: result.notes || [],
    };

    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/patients/patient_ram/entries`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        setCommittedEntryId(data.id);
        setCommitMessage("✓ Record successfully approved and written to Ram Bahadur Shrestha's ledger!");
      } else {
        setCommitMessage("Could not commit to record right now.");
      }
    } catch {
      setCommitMessage("Backend offline or connection error.");
    }
  };

  const concepts: NormalizedConcept[] = result?.normalized?.concepts || [];

  return (
    <DashboardShell>
      <section className="panel panel--paper">
        <div className="panel__inner">
          <span className="eyebrow">Interactive Clinical Intake</span>
          <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.8rem)" }}>
            Intake Studio & Approval Gate
          </h1>
          <p className="lede">
            Input clinical notes in Devanagari, Romanized Nepali, or prescription abbreviations.
            The 3-tier lexicon resolves brands to generics and strictly suppresses negated symptoms before writing to the patient ledger.
          </p>

          <div className="actions" style={{ marginTop: 20 }}>
            {DEMO_PRESETS.map((preset) => (
              <button
                key={preset.label}
                type="button"
                className="button button--secondary"
                onClick={() => {
                  setInputText(preset.text);
                  setCommitMessage(null);
                }}
              >
                Preset: {preset.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Input Workspace */}
      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Clinical Input Text</p>
        <div style={{ display: "grid", gap: 14 }}>
          <textarea
            rows={5}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            style={{
              width: "100%",
              padding: "16px",
              borderRadius: "16px",
              border: "1px solid var(--line)",
              background: "#fff",
              fontSize: "1.05rem",
              lineHeight: "1.6",
              color: "var(--ink)",
              fontFamily: "inherit",
              resize: "vertical",
            }}
            placeholder="Type or paste doctor slip notes..."
          />

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.9rem", color: "var(--ink-soft)", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={useModel}
                  onChange={(e) => setUseModel(e.target.checked)}
                />
                Enable Tier 3 Gemma Model candidate selection
              </label>
            </div>

            <button
              className="button button--primary"
              type="button"
              onClick={runIntake}
              disabled={isProcessing}
            >
              {isProcessing ? "Running Pipeline..." : "⚡ Run Sanchai Intake Pipeline"}
            </button>
          </div>
        </div>
      </section>

      {/* Extraction & Normalization Results */}
      {result ? (
        <section className="timeline-card" style={{ marginTop: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
            <div>
              <p className="section-title">Pipeline Output</p>
              <h2 style={{ margin: "0 0 4px", fontSize: "1.4rem", letterSpacing: "-0.02em" }}>
                Extracted & Grounded Findings
              </h2>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <span className="tag tag--committed" style={{ textTransform: "uppercase" }}>
                Class: {result.document_class}
              </span>
              <span className="tag tag--review">
                Method: {result.extraction_method}
              </span>
            </div>
          </div>

          {/* Concepts Grid */}
          <div className="timeline" style={{ marginTop: 18 }}>
            {concepts.length === 0 ? (
              <article className="timeline-item">
                <p className="timeline-item__summary">No clinical concepts recognized.</p>
              </article>
            ) : (
              concepts.map((c) => (
                <article key={`${c.concept_id}-${c.start}`} className="timeline-item">
                  <div className="timeline-item__top">
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <span className="timeline-item__label" style={{ fontSize: "1.05rem" }}>
                        {c.canonical_np} ({c.canonical_en})
                      </span>
                      <span className={`tag tag--tier${c.tier}`}>
                        Tier {c.tier} {c.tier === 1 ? "Exact" : c.tier === 2 ? "Fuzzy" : "Gemma"}
                      </span>
                      {c.concept_type ? (
                        <span className="tag" style={{ background: "#f5f0eb", color: "var(--ink)" }}>
                          {c.concept_type}
                        </span>
                      ) : null}
                    </div>

                    <span className={`tag ${c.negated ? "tag--negated" : "tag--committed"}`}>
                      {c.negated ? "¬ Negated (Denied)" : "✓ Confirmed Present"}
                    </span>
                  </div>

                  <p className="timeline-item__summary">
                    Surface text: <strong>"{c.surface_form}"</strong>
                    {c.generic ? (
                      <> · Generic Active Ingredient: <strong>{c.generic.canonical_en} ({c.generic.canonical_np})</strong></>
                    ) : null}
                    {c.icd11_code ? <> · ICD-11: <code>{c.icd11_code}</code></> : null}
                  </p>
                </article>
              ))
            )}
          </div>

          {/* Meta & Duration */}
          <div className="metrics" style={{ marginTop: 18 }}>
            <article className="metric metric--positive">
              <span className="metric__label">Identified Concepts</span>
              <div className="metric__value">{concepts.length}</div>
            </article>
            <article className="metric metric--warning">
              <span className="metric__label">Negated Findings</span>
              <div className="metric__value">
                {concepts.filter((c) => c.negated).length}
              </div>
            </article>
            <article className="metric metric--neutral">
              <span className="metric__label">Duration / Frequency</span>
              <div className="metric__value">
                {result.normalized?.duration_days
                  ? `${result.normalized.duration_days} days`
                  : "None"}{" "}
                {result.normalized?.frequency_per_day
                  ? `· ${result.normalized.frequency_per_day}x/day`
                  : ""}
              </div>
            </article>
          </div>

          {/* Human-in-the-Loop Approval Action */}
          <div style={{ marginTop: 24, padding: "20px", borderRadius: "18px", background: "var(--panel-muted)" }}>
            <p className="section-title">Approval-Before-Write Gate</p>
            <p style={{ margin: "0 0 16px", color: "var(--ink-soft)", fontSize: "0.95rem" }}>
              Only approved findings mutate the patient's longitudinal record. Negated conditions are filtered out from active diagnoses.
            </p>

            <div className="actions" style={{ marginTop: 0 }}>
              <button
                className="button button--primary"
                type="button"
                onClick={commitToPatient}
              >
                ✓ Approve & Commit to Ram Bahadur Shrestha
              </button>
              {committedEntryId ? (
                <Link
                  className="button button--secondary"
                  href="/patients/patient_ram"
                >
                  View in Patient Timeline →
                </Link>
              ) : null}
            </div>

            {commitMessage ? (
              <p style={{ marginTop: 12, fontWeight: 700, color: committedEntryId ? "var(--ok)" : "var(--danger)" }}>
                {commitMessage}
              </p>
            ) : null}
          </div>
        </section>
      ) : null}
    </DashboardShell>
  );
}
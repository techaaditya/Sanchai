"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";

const PRESET_TOKENS = [
  {
    token: "7599a9303572da76",
    patientName: "राम बहादुर श्रेष्ठ (Ram Bahadur)",
    bloodGroup: "B+",
    severity: "Penicillin Allergy",
  },
  {
    token: "30573e87fc4c2aa2",
    patientName: "सीता कार्की (Sita Karki)",
    bloodGroup: "A+",
    severity: "Sulfa Allergy · Chronic Hypertension",
  },
  {
    token: "351db8ee7a56111f",
    patientName: "माया तामाङ (Maya Tamang)",
    bloodGroup: "O+",
    severity: "No Known Drug Allergies",
  },
];

export default function ScanPage() {
  const router = useRouter();
  const [tokenInput, setTokenInput] = useState("");
  const [isSimulating, setIsSimulating] = useState(false);

  const handleScan = (tokenToScan: string) => {
    let clean = tokenToScan.trim();
    if (clean.startsWith("sanchai://p/")) {
      clean = clean.replace("sanchai://p/", "");
    }
    if (!clean) return;

    setIsSimulating(true);
    setTimeout(() => {
      router.push(`/emergency/${clean}`);
    }, 600);
  };

  return (
    <DashboardShell>
      <section className="panel panel--paper">
        <div className="panel__inner">
          <span className="eyebrow">Emergency QR Scanner</span>
          <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.8rem)" }}>
            Emergency QR Lookup
          </h1>
          <p className="lede">
            Scan or simulate emergency responder QR reads. Resolves cryptographically bound
            emergency tokens directly to offline-first blood groups, verified allergies, and active conditions.
          </p>

          <div className="metrics" style={{ marginTop: 24 }}>
            <article className="metric metric--positive">
              <span className="metric__label">Scanner Engine</span>
              <div className="metric__value">Segno Optical / High-Contrast</div>
            </article>
            <article className="metric metric--neutral">
              <span className="metric__label">Format</span>
              <div className="metric__value">sanchai://p/[token]</div>
            </article>
            <article className="metric metric--warning">
              <span className="metric__label">Offline Ready</span>
              <div className="metric__value">Zero Cloud Latency</div>
            </article>
          </div>
        </div>
      </section>

      {/* Viewfinder and Token Input */}
      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">Optical Scanner Viewfinder</p>
        <div className="scanner-viewfinder">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "0.88rem", color: "var(--ink)", fontWeight: 700, letterSpacing: "0.04em" }}>
              {isSimulating ? "⚡ DECODING OPTICAL HEALTH PAYLOAD..." : "ALIGN QR CODE WITHIN SENSOR TARGET"}
            </span>
            <span className="tag tag--committed">
              <span className="model-chip__dot" style={{ display: "inline-block", width: 6, height: 6, marginRight: 6 }} />
              Sensor Active
            </span>
          </div>

          <div className="scanner-viewport-box">
            {/* 4 Optical Corner Reticles */}
            <div className="scanner-corner scanner-corner--tl" />
            <div className="scanner-corner scanner-corner--tr" />
            <div className="scanner-corner scanner-corner--bl" />
            <div className="scanner-corner scanner-corner--br" />

            {/* Animated Laser Sweep Line */}
            <div className="scanner-laser" />

            <div style={{ padding: "8px 0" }}>
              <p style={{ margin: 0, fontSize: "1.15rem", fontWeight: 700, color: "var(--ink)", letterSpacing: "0.04em" }}>
                [ ⛶ OPTICAL CAMERA SENSOR ]
              </p>
              <p style={{ margin: "6px 0 0", fontSize: "0.85rem", color: "var(--ink-soft)" }}>
                High-contrast Segno QR reader for ambulance triage desks & ER responders
              </p>
            </div>
          </div>

          {/* Quick Input Box */}
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
            <input
              type="text"
              placeholder="Paste token or sanchai://p/[token]..."
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              className="scanner-input"
            />
            <button
              className="button button--primary"
              type="button"
              onClick={() => handleScan(tokenInput)}
              disabled={isSimulating}
            >
              {isSimulating ? "Decoding..." : "Scan & Open Emergency Card →"}
            </button>
          </div>
        </div>
      </section>

      {/* Preset Patient Scans */}
      <section className="timeline-card" style={{ marginTop: 24 }}>
        <p className="section-title">One-Click Emergency Demo Cards</p>
        <div className="timeline">
          {PRESET_TOKENS.map((preset) => (
            <article
              key={preset.token}
              className="timeline-item"
              style={{ cursor: "pointer", transition: "all 0.15s ease" }}
              onClick={() => handleScan(preset.token)}
            >
              <div className="timeline-item__top">
                <span className="timeline-item__label" style={{ fontSize: "1.05rem" }}>
                  {preset.patientName}
                </span>
                <span className="tag tag--committed">
                  Blood {preset.bloodGroup}
                </span>
              </div>
              <p className="timeline-item__summary">
                Critical flag: <strong>{preset.severity}</strong> · Token: <code>{preset.token}</code>
              </p>
            </article>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
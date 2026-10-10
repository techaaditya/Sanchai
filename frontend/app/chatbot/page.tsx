"use client";

import { useState, useEffect, useRef, useTransition, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { DashboardShell } from "@/components/dashboard-shell";
import {
  fetchChatbotPatients,
  fetchChatbotContext,
  postChatbotMessage,
  type ChatbotPatient,
  type ChatbotResponse,
} from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  safetyAlerts?: string[];
  attachmentName?: string;
  attachmentMeta?: ChatbotResponse["attachment"];
  timestamp: string;
};

const DEFAULT_PROMPTS = [
  "📋 Generate a Pre-Visit Doctor Summary for my upcoming appointment",
  "⚠️ Can I take Amoxicillin or beta-lactam antibiotics with my allergy?",
  "🔬 Explain my recent CBC and Widal test results in simple Nepali",
  "💊 What is the prescribed dosage schedule for Cetamol and Cifran?",
];

function ChatbotContent() {
  const searchParams = useSearchParams();
  const initialPatientParam = searchParams.get("patient") || "patient_ram";

  const [patients, setPatients] = useState<ChatbotPatient[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string>(initialPatientParam);
  const [activeContext, setActiveContext] = useState<Record<string, unknown> | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [inputMessage, setInputMessage] = useState("");
  const [isPending, startTransition] = useTransition();
  const [messages, setMessages] = useState<Message[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load available patients list
  useEffect(() => {
    async function loadPatients() {
      const data = await fetchChatbotPatients();
      if (data && data.length > 0) {
        setPatients(data);
      }
    }
    loadPatients();
  }, []);

  // Load patient EHR context when selection changes
  useEffect(() => {
    if (!selectedPatientId) return;
    async function loadContext() {
      const ctx = await fetchChatbotContext(selectedPatientId);
      if (ctx) {
        setActiveContext(ctx);
      }
    }
    loadContext();
  }, [selectedPatientId]);

  // Set initial welcome message
  useEffect(() => {
    const currentPatient = patients.find((p) => p.id === selectedPatientId);
    const patientName = currentPatient ? currentPatient.name : "Ram Bahadur Shrestha";
    const allergies = currentPatient?.allergies || ["Penicillin"];

    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: `### नमस्ते! म SanchAI (सञ्चै एआई) हुँ।\n\nम **${patientName}** को सम्पूर्ण स्वास्थ्य विवरण (EHR Ledger) सँग जोडिएको छु।\n\n**म तपाईंलाई कसरी सहयोग गर्न सक्छु?**\n- 📋 **Pre-visit Doctor Summary:** अस्पताल वा डाक्टरलाई भेट्नुअघि आवश्यक स्वास्थ्य सारांश तयार गर्न।\n- ⚠️ **Allergy & Safety Checks:** नयाँ औषधि लिनुअघि ज्ञात एलर्जी (${allergies.join(", ") || "None"}) सँग जाँच गर्न।\n- 📄 **Multimodal Attachment Interpretation:** डाक्टरको प्रेस्क्रिप्सन फोटो, क्लिनिक टिपोट वा ल्याब रिपोर्ट PDF अपलोड गरेर अर्थ बुझ्न।\n- 🔬 **Lab Test Explanations:** रगत, पिसाब तथा अन्य जाँचको रिपोर्ट सरल नेपाली वा अंग्रेजीमा बुझ्न।`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  }, [selectedPatientId, patients]);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isPending]);

  const handleSendMessage = (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text && !selectedFile) return;

    const userMessageId = `user_${Date.now()}`;
    const userMsg: Message = {
      id: userMessageId,
      role: "user",
      content: text || `[Uploaded Document: ${selectedFile?.name}]`,
      attachmentName: selectedFile?.name,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage("");

    const fileToUpload = selectedFile;
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

    startTransition(async () => {
      const formData = new FormData();
      formData.append("message", text || "Please analyze this attached clinical record.");
      if (selectedPatientId) {
        formData.append("patient_id", selectedPatientId);
      }

      // Append conversation history
      const historyPayload = messages.slice(-4).map((m) => ({
        role: m.role,
        content: m.content,
      }));
      formData.append("history", JSON.stringify(historyPayload));

      if (fileToUpload) {
        formData.append("file", fileToUpload);
      }

      const res = await postChatbotMessage(formData);
      if (res) {
        const assistantMsg: Message = {
          id: `asst_${Date.now()}`,
          role: "assistant",
          content: res.reply,
          safetyAlerts: res.safety_alerts,
          attachmentMeta: res.attachment,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } else {
        const fallbackMsg: Message = {
          id: `asst_err_${Date.now()}`,
          role: "assistant",
          content: "माफ गर्नुहोस्, अहिले जवाफ प्राप्त गर्न सकिएन। कृपया केही समयपछि पुनः प्रयास गर्नुहोस्।",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, fallbackMsg]);
      }
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const currentPatient = patients.find((p) => p.id === selectedPatientId);

  return (
    <DashboardShell>
      {/* Top Banner */}
      <section className="panel panel--paper">
        <div className="panel__inner">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
            <div style={{ display: "flex", gap: 16, alignItems: "flex-start", flexWrap: "wrap" }}>
              <img
                src="/logo512.svg"
                alt="SanchAI Assistant"
                width={52}
                height={52}
                style={{
                  borderRadius: 14,
                  background: "#ffffff",
                  padding: 6,
                  border: "1.5px solid rgba(17, 193, 105, 0.28)",
                  boxShadow: "0 4px 14px rgba(17, 193, 105, 0.16)",
                  flexShrink: 0,
                  marginTop: 4,
                }}
              />
              <div>
                <span className="eyebrow">
                  <span className="model-chip__dot" style={{ display: "inline-block", width: 6, height: 6, marginRight: 6 }} />
                  Grounded EHR Intelligence · SanchAI
                </span>
                <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.8rem)" }}>
                  SanchAI Clinical Assistant
                </h1>
                <p className="lede">
                  Longitudinal record-grounded AI assistant powered by <code>gemma4:31b-cloud</code>. Ingests prescription photos, lab PDFs, cross-checks allergies, and generates doctor pre-visit briefings.
                </p>
              </div>
            </div>

            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              {currentPatient ? (
                <Link className="button button--secondary" href={`/patients/${currentPatient.id}`}>
                  View Patient Ledger →
                </Link>
              ) : null}
            </div>
          </div>
        </div>
      </section>

      {/* Main Chat Shell */}
      <section style={{ marginTop: 24 }}>
        <div className="chat-shell">
          {/* Header Bar: Patient Selector & Live Safety Strip */}
          <div className="chat-header-bar">
            <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
              <label htmlFor="patient-select" style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--ink-soft)" }}>
                Active Patient Record:
              </label>
              <select
                id="patient-select"
                className="chat-patient-select"
                value={selectedPatientId}
                onChange={(e) => setSelectedPatientId(e.target.value)}
              >
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.sanchai_id}) · {p.blood_group || "N/A"}
                  </option>
                ))}
              </select>
            </div>

            {/* Safety Indicators */}
            {currentPatient && (
              <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                <span className="tag tag--neutral" style={{ background: "rgba(0,0,0,0.05)" }}>
                  🩸 {currentPatient.blood_group || "Unknown"}
                </span>
                {currentPatient.allergies.length > 0 ? (
                  <span className="tag" style={{ background: "#ffebee", color: "#c62828", border: "1px solid #ffcdd2" }}>
                    ⚠️ Allergy: {currentPatient.allergies.join(", ")}
                  </span>
                ) : (
                  <span className="tag tag--committed">✓ No Known Allergies</span>
                )}
                {currentPatient.conditions.length > 0 && (
                  <span className="tag tag--review">
                    🩺 {currentPatient.conditions.slice(0, 2).join(", ")}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Messages Area */}
          <div className="chat-messages-scroll">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-msg ${msg.role === "user" ? "chat-msg--user" : "chat-msg--assistant"}`}
              >
                <div
                  className={`chat-bubble ${msg.role === "user" ? "chat-bubble--user" : "chat-bubble--assistant"}`}
                >
                  {/* Attachment Pill (if present in user message) */}
                  {msg.attachmentName && (
                    <div style={{ marginBottom: 10, display: "inline-flex", alignItems: "center", gap: 6, background: "rgba(255,255,255,0.2)", padding: "4px 10px", borderRadius: 8, fontSize: "0.82rem" }}>
                      📎 Attachment: <strong>{msg.attachmentName}</strong>
                    </div>
                  )}

                  {/* Safety Contraindication Alert Box */}
                  {msg.safetyAlerts && msg.safetyAlerts.length > 0 && (
                    <div className="safety-alert-box">
                      {msg.safetyAlerts.map((alert, idx) => (
                        <div key={idx}>{alert}</div>
                      ))}
                    </div>
                  )}

                  {/* Parsed Concepts Badge (if attachment was parsed) */}
                  {msg.attachmentMeta && msg.attachmentMeta.concepts && msg.attachmentMeta.concepts.length > 0 && (
                    <div style={{ margin: "8px 0 12px", padding: "10px 14px", background: "var(--panel-muted)", borderRadius: 12, border: "1px solid var(--line)" }}>
                      <p style={{ margin: "0 0 6px", fontSize: "0.8rem", fontWeight: 700, color: "var(--ink-soft)" }}>
                        🔍 Ingestion Pipeline Detected {msg.attachmentMeta.concepts.length} Clinical Entities from {msg.attachmentMeta.filename}:
                      </p>
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                        {msg.attachmentMeta.concepts.slice(0, 6).map((c, i) => (
                          <span
                            key={i}
                            className={`tag tag--tier${c.tier || 1}`}
                            style={{ fontSize: "0.76rem", padding: "2px 8px" }}
                          >
                            {c.canonical_en} ({c.canonical_np}) · {c.type}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Message Markdown Body */}
                  <div
                    style={{ whiteSpace: "pre-wrap" }}
                    dangerouslySetInnerHTML={{
                      __html: formatMarkdown(msg.content),
                    }}
                  />

                  <div
                    style={{
                      marginTop: 8,
                      fontSize: "0.72rem",
                      textAlign: msg.role === "user" ? "right" : "left",
                      color: msg.role === "user" ? "rgba(255,255,255,0.6)" : "var(--ink-soft)",
                    }}
                  >
                    {msg.timestamp}
                  </div>
                </div>
              </div>
            ))}

            {isPending && (
              <div className="chat-msg chat-msg--assistant">
                <div className="chat-bubble chat-bubble--assistant" style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span className="model-chip__dot" style={{ animation: "pulse 1s infinite" }} />
                  <span style={{ fontSize: "0.9rem", color: "var(--ink-soft)" }}>
                    SanchAI is consulting the patient ledger with <code>gemma4:31b-cloud</code>...
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts Bar */}
          <div style={{ padding: "8px 20px", background: "rgba(246, 241, 234, 0.6)", borderTop: "1px solid var(--line)", display: "flex", gap: 8, overflowX: "auto" }}>
            {DEFAULT_PROMPTS.map((promptText, i) => (
              <button
                key={i}
                type="button"
                className="chat-quick-prompt"
                onClick={() => handleSendMessage(promptText)}
                disabled={isPending}
              >
                {promptText}
              </button>
            ))}
          </div>

          {/* Attachment Preview (if staged) */}
          {selectedFile && (
            <div style={{ padding: "8px 24px", background: "var(--accent-soft)", display: "flex", alignItems: "center", justifyContent: "space-between", borderTop: "1px solid rgba(200, 107, 28, 0.2)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.85rem", color: "var(--accent)" }}>
                <span>📎 Staged for Analysis:</span>
                <strong>{selectedFile.name}</strong>
                <span>({(selectedFile.size / 1024).toFixed(1)} KB)</span>
              </div>
              <button
                type="button"
                onClick={() => {
                  setSelectedFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }}
                style={{ background: "none", border: "none", cursor: "pointer", color: "var(--danger)", fontWeight: 700 }}
              >
                ✕ Cancel
              </button>
            </div>
          )}

          {/* Input Row */}
          <div className="chat-input-wrapper">
            <div className="chat-input-row">
              {/* File Attachment Button */}
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: "none" }}
                accept=".pdf,image/png,image/jpeg,image/webp,.txt"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setSelectedFile(e.target.files[0]);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="button button--secondary"
                style={{ padding: "10px 14px", borderRadius: 14 }}
                title="Attach Prescription Photo, Clinic Note, or Lab Report PDF"
                disabled={isPending}
              >
                📎 Attach
              </button>

              {/* Text Input Area */}
              <textarea
                className="chat-textarea"
                placeholder={
                  selectedFile
                    ? `Ask SanchAI about ${selectedFile.name} (e.g. "What medications are in this prescription?")...`
                    : "Ask SanchAI anything (e.g. 'Can I take Cetamol with my ongoing medications?', 'Generate pre-visit summary')..."
                }
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={isPending}
              />

              {/* Send Button */}
              <button
                type="button"
                className="button button--primary"
                onClick={() => handleSendMessage()}
                disabled={isPending || (!inputMessage.trim() && !selectedFile)}
                style={{ borderRadius: 14, padding: "12px 20px" }}
              >
                {isPending ? "Sending..." : "Send →"}
              </button>
            </div>
          </div>
        </div>
      </section>
    </DashboardShell>
  );
}

// Lightweight Markdown formatter for safe HTML rendering
function formatMarkdown(text: string): string {
  if (!text) return "";
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Headings
  html = html.replace(/^### (.*$)/gim, '<h3 style="margin: 12px 0 6px; font-size: 1.15rem; font-weight: 700;">$1</h3>');
  html = html.replace(/^#### (.*$)/gim, '<h4 style="margin: 10px 0 4px; font-size: 1rem; font-weight: 700;">$1</h4>');

  // Bold & Italic
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");

  // Inline Code
  html = html.replace(/`([^`]+)`/g, '<code style="background: rgba(0,0,0,0.06); padding: 2px 6px; border-radius: 4px; font-size: 0.88em;">$1</code>');

  // Blockquotes
  html = html.replace(/^> (.*$)/gim, '<blockquote style="margin: 8px 0; padding-left: 12px; border-left: 3px solid var(--accent); color: var(--ink-soft);">$1</blockquote>');

  // Bullet Lists
  html = html.replace(/^\- (.*$)/gim, '<li style="margin-left: 18px; margin-bottom: 4px;">$1</li>');

  return html;
}

export default function ChatbotPage() {
  return (
    <Suspense fallback={<div className="shell">Loading SanchAI Clinical Assistant...</div>}>
      <ChatbotContent />
    </Suspense>
  );
}

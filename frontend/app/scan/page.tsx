"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { DashboardShell } from "@/components/dashboard-shell";
import { decodeQrImage, getApiBaseUrl, type QrDecodeResult } from "@/lib/api";

const PRESET_TOKENS = [
  {
    token: "7599a9303572da76",
    patientName: "राम बहादुर श्रेष्ठ (Ram Bahadur Shrestha)",
    bloodGroup: "B+",
    severity: "Penicillin Allergy · Hypertension",
    patientId: "patient_ram",
  },
  {
    token: "1b49993d76ea222a",
    patientName: "सीता कार्की (Sita Karki)",
    bloodGroup: "A+",
    severity: "Sulfa Allergy · Type 2 Diabetes",
    patientId: "patient_sita",
  },
  {
    token: "564ef1d79ed130ee",
    patientName: "माया तामाङ (Maya Tamang)",
    bloodGroup: "O+",
    severity: "No Known Drug Allergies · Asthma",
    patientId: "patient_maya",
  },
];

export default function ScanPage() {
  const router = useRouter();

  // Mode selection
  const [activeTab, setActiveTab] = useState<"camera" | "upload" | "manual">("camera");

  // Camera state
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isScanningFrame, setIsScanningFrame] = useState(false);

  // File upload state
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDecodingFile, setIsDecodingFile] = useState(false);
  const [decodeError, setDecodeError] = useState<string | null>(null);

  // Manual token state
  const [tokenInput, setTokenInput] = useState("");
  const [isNavigating, setIsNavigating] = useState(false);

  // Detected status
  const [detectedResult, setDetectedResult] = useState<QrDecodeResult | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const scanIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Clean navigation helper
  const navigateToEmergency = useCallback(
    (rawTokenOrUri: string) => {
      let clean = rawTokenOrUri.trim();
      if (clean.startsWith("sanchai://p/")) {
        clean = clean.replace("sanchai://p/", "");
      }
      if (!clean) return;

      setIsNavigating(true);
      // Brief pause to allow user to see success confirmation
      setTimeout(() => {
        router.push(`/emergency/${clean}`);
      }, 700);
    },
    [router]
  );

  // Stop camera stream safely
  const stopCamera = useCallback(() => {
    if (scanIntervalRef.current) {
      clearInterval(scanIntervalRef.current);
      scanIntervalRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    setIsScanningFrame(false);
  }, []);

  // Frame processing from live video
  const processVideoFrame = useCallback(async () => {
    if (!videoRef.current || videoRef.current.readyState < 2) return;

    const video = videoRef.current;

    // 1. Try Browser native BarcodeDetector if available (instant 0ms)
    if (typeof window !== "undefined" && "BarcodeDetector" in window) {
      try {
        const BarcodeDetectorClass = (window as any).BarcodeDetector;
        const detector = new BarcodeDetectorClass({ formats: ["qr_code"] });
        const barcodes = await detector.detect(video);
        if (barcodes && barcodes.length > 0) {
          const raw = barcodes[0].rawValue;
          if (raw) {
            stopCamera();
            setDetectedResult({
              success: true,
              raw_text: raw,
              token: raw.replace("sanchai://p/", ""),
              emergency_path: `/emergency/${raw.replace("sanchai://p/", "")}`,
            });
            navigateToEmergency(raw);
            return;
          }
        }
      } catch {
        // Fallback to canvas snapshot
      }
    }

    // 2. Offscreen Canvas Snapshot fallback to OpenCV decode endpoint
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) return;
      setIsScanningFrame(true);
      try {
        const result = await decodeQrImage(blob);
        if (result && result.success && result.token) {
          stopCamera();
          setDetectedResult(result);
          navigateToEmergency(result.token);
        }
      } catch {
        // Ignore single frame failure
      } finally {
        setIsScanningFrame(false);
      }
    }, "image/jpeg", 0.85);
  }, [stopCamera, navigateToEmergency]);

  // Start camera stream
  const startCamera = async () => {
    setCameraError(null);
    setDecodeError(null);
    setDetectedResult(null);

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setCameraError("Camera API is not supported on this browser or connection. Please use file upload or demo cards.");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });

      mediaStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setIsCameraActive(true);

      // Begin interval frame scanner
      scanIntervalRef.current = setInterval(() => {
        processVideoFrame();
      }, 550);
    } catch (err: any) {
      stopCamera();
      if (err?.name === "NotAllowedError" || err?.name === "PermissionDeniedError") {
        setCameraError("Camera access was blocked by your browser. Please allow camera permissions or upload a QR image.");
      } else {
        setCameraError(`Unable to start camera: ${err?.message || "Device not found"}. Use file upload or demo cards.`);
      }
    }
  };

  // Handle uploaded image file
  const handleFileUpload = async (file: File) => {
    if (!file) return;
    setUploadedFile(file);
    setIsDecodingFile(true);
    setDecodeError(null);
    setDetectedResult(null);

    try {
      const res = await decodeQrImage(file);
      if (res && res.success && res.token) {
        setDetectedResult(res);
        navigateToEmergency(res.token);
      } else {
        setDecodeError("No valid QR code was detected in this image. Please upload a clear photo or screenshot of a Sanchai QR card.");
      }
    } catch {
      setDecodeError("Could not process image file. Please try another image or use one-click demo cards.");
    } finally {
      setIsDecodingFile(false);
    }
  };

  // Clean up camera on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return (
    <DashboardShell>
      {/* Top Banner */}
      <section className="panel panel--paper">
        <div className="panel__inner">
          <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 12 }}>
            <img
              src="/logo512.svg"
              alt="Sanchai QR Logo"
              width={46}
              height={46}
              style={{
                borderRadius: 12,
                background: "#ffffff",
                padding: 5,
                border: "1.5px solid rgba(17, 193, 105, 0.28)",
                boxShadow: "0 2px 10px rgba(17, 193, 105, 0.16)",
                flexShrink: 0,
              }}
            />
            <div>
              <span className="eyebrow" style={{ margin: 0 }}>Emergency QR Scanner & Decoder</span>
              <div style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--ink)", marginTop: 2 }}>
                Sanchai Optical Triage Token Engine
              </div>
            </div>
          </div>

          <h1 className="title" style={{ fontSize: "clamp(2rem, 4vw, 3.8rem)" }}>
            Emergency QR Scanner
          </h1>
          <p className="lede">
            Fully functional optical triage scanner. Use your device camera, upload a saved QR photo,
            or click any verified patient card to resolve blood group, allergies, and active conditions offline in &lt; 1s.
          </p>

          <div className="metrics" style={{ marginTop: 24 }}>
            <article className="metric metric--positive">
              <span className="metric__label">Decoder Engine</span>
              <div className="metric__value">OpenCV + Native BarcodeDetector</div>
            </article>
            <article className="metric metric--neutral">
              <span className="metric__label">Standard Format</span>
              <div className="metric__value">sanchai://p/[token]</div>
            </article>
            <article className="metric metric--warning">
              <span className="metric__label">Offline Triage</span>
              <div className="metric__value">&lt; 1s Paramedic View</div>
            </article>
          </div>
        </div>
      </section>

      {/* Main Scanner Card */}
      <section className="timeline-card" style={{ marginTop: 24 }}>
        {/* Navigation Mode Tabs */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 16 }}>
          <p className="section-title" style={{ margin: 0 }}>
            Optical Scanner Modes
          </p>

          <div style={{ display: "flex", gap: 6, background: "var(--panel-muted)", padding: 4, borderRadius: 12, border: "1px solid var(--line)" }}>
            <button
              type="button"
              onClick={() => {
                stopCamera();
                setActiveTab("camera");
              }}
              className={`button ${activeTab === "camera" ? "button--primary" : "button--secondary"}`}
              style={{ padding: "6px 14px", fontSize: "0.84rem", borderRadius: 8 }}
            >
              📷 Live Camera
            </button>
            <button
              type="button"
              onClick={() => {
                stopCamera();
                setActiveTab("upload");
              }}
              className={`button ${activeTab === "upload" ? "button--primary" : "button--secondary"}`}
              style={{ padding: "6px 14px", fontSize: "0.84rem", borderRadius: 8 }}
            >
              📁 Upload QR Image
            </button>
            <button
              type="button"
              onClick={() => {
                stopCamera();
                setActiveTab("manual");
              }}
              className={`button ${activeTab === "manual" ? "button--primary" : "button--secondary"}`}
              style={{ padding: "6px 14px", fontSize: "0.84rem", borderRadius: 8 }}
            >
              ⌨️ Enter Token
            </button>
          </div>
        </div>

        {/* Success Detection Alert */}
        {detectedResult && (
          <div style={{ marginBottom: 18, padding: "14px 18px", borderRadius: 14, background: "#e8f6ed", border: "1.5px solid #1f8a5b", color: "#145939", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
            <div>
              <span style={{ fontWeight: 800, fontSize: "1rem" }}>
                ✓ QR Code Successfully Detected & Decoded!
              </span>
              <p style={{ margin: "4px 0 0", fontSize: "0.88rem" }}>
                Token: <code>{detectedResult.token}</code> {detectedResult.patient_name ? `· Patient: ${detectedResult.patient_name}` : ""} {detectedResult.blood_group ? `· Blood: ${detectedResult.blood_group}` : ""}
              </p>
            </div>
            <span className="tag tag--committed" style={{ fontSize: "0.85rem" }}>
              Opening Emergency Record...
            </span>
          </div>
        )}

        {/* Scanner Viewfinder Box */}
        <div className="scanner-viewfinder">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <span style={{ fontSize: "0.86rem", color: "var(--ink)", fontWeight: 700, letterSpacing: "0.04em" }}>
              {isNavigating
                ? "⚡ OPENING CONFIRMED EMERGENCY HEALTH CARD..."
                : isScanningFrame || isDecodingFile
                ? "🔍 DECODING OPTICAL HEALTH PAYLOAD..."
                : isCameraActive
                ? "🎯 SENSOR ACTIVE · POINT AT ANY SANCHAI QR CODE"
                : "READY · SELECT SCANNING METHOD BELOW"}
            </span>
            <span className={isCameraActive ? "tag tag--committed" : "tag tag--neutral"}>
              <span className="model-chip__dot" style={{ display: "inline-block", width: 6, height: 6, marginRight: 6 }} />
              {isCameraActive ? "Camera Streaming" : "Sensor Standby"}
            </span>
          </div>

          {/* Central Viewport */}
          <div className="scanner-viewport-box" style={{ minHeight: 240, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", position: "relative", overflow: "hidden" }}>
            {/* 4 Optical Reticle Corners */}
            <div className="scanner-corner scanner-corner--tl" />
            <div className="scanner-corner scanner-corner--tr" />
            <div className="scanner-corner scanner-corner--bl" />
            <div className="scanner-corner scanner-corner--br" />

            {/* Laser Line Animation (when scanning) */}
            {(isCameraActive || isScanningFrame || isDecodingFile) && (
              <div className="scanner-laser" />
            )}

            {/* TAB 1: LIVE CAMERA STREAM */}
            {activeTab === "camera" && (
              <div style={{ width: "100%", height: "100%", textAlign: "center" }}>
                <video
                  ref={videoRef}
                  playsInline
                  autoPlay
                  muted
                  style={{
                    display: isCameraActive ? "block" : "none",
                    width: "100%",
                    maxHeight: 260,
                    borderRadius: 14,
                    objectFit: "cover",
                    background: "#000",
                  }}
                />

                {!isCameraActive && (
                  <div style={{ padding: "20px 10px" }}>
                    <p style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "var(--ink)" }}>
                      [ 📷 Optical Camera Scanner ]
                    </p>
                    <p style={{ margin: "8px 0 18px", fontSize: "0.86rem", color: "var(--ink-soft)" }}>
                      Use your webcam or mobile camera to scan physical QR badges, A4 doctor summaries, or another screen.
                    </p>
                    <button
                      type="button"
                      className="button button--primary"
                      onClick={startCamera}
                      style={{ padding: "10px 22px", borderRadius: 12 }}
                    >
                      Turn On Camera & Start Scanning →
                    </button>
                  </div>
                )}

                {isCameraActive && (
                  <div style={{ marginTop: 12, display: "flex", gap: 10, justifyContent: "center" }}>
                    <button
                      type="button"
                      className="button button--secondary"
                      onClick={stopCamera}
                      style={{ fontSize: "0.85rem", padding: "6px 14px" }}
                    >
                      ⏹ Stop Camera
                    </button>
                  </div>
                )}

                {cameraError && (
                  <div style={{ marginTop: 12, padding: "8px 14px", background: "#fdecec", borderRadius: 10, color: "#d9383a", fontSize: "0.85rem" }}>
                    {cameraError}
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: UPLOAD QR IMAGE */}
            {activeTab === "upload" && (
              <div style={{ width: "100%", padding: "16px 10px", textAlign: "center" }}>
                <input
                  type="file"
                  ref={fileInputRef}
                  style={{ display: "none" }}
                  accept="image/png,image/jpeg,image/webp,image/jpg"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileUpload(e.target.files[0]);
                    }
                  }}
                />

                <p style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "var(--ink)" }}>
                  [ 📁 Image File Decoder ]
                </p>
                <p style={{ margin: "8px 0 16px", fontSize: "0.86rem", color: "var(--ink-soft)" }}>
                  Select or drag-and-drop any QR code image, badge screenshot, or downloaded <code>qr.png</code>.
                </p>

                <div
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                      handleFileUpload(e.dataTransfer.files[0]);
                    }
                  }}
                  style={{
                    border: "2px dashed var(--accent)",
                    borderRadius: 14,
                    padding: "20px 16px",
                    background: "rgba(200, 107, 28, 0.05)",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                >
                  <p style={{ margin: 0, fontWeight: 700, color: "var(--accent)", fontSize: "0.95rem" }}>
                    {uploadedFile ? `Uploaded: ${uploadedFile.name}` : "Click to Browse or Drag Image Here"}
                  </p>
                  <span style={{ fontSize: "0.78rem", color: "var(--ink-soft)" }}>
                    Supports PNG, JPG, JPEG, and WebP
                  </span>
                </div>

                {isDecodingFile && (
                  <p style={{ marginTop: 12, color: "var(--accent)", fontSize: "0.88rem", fontWeight: 700 }}>
                    ⚡ Analyzing optical QR matrix with OpenCV detector...
                  </p>
                )}

                {decodeError && (
                  <div style={{ marginTop: 12, padding: "8px 14px", background: "#fdecec", borderRadius: 10, color: "#d9383a", fontSize: "0.85rem" }}>
                    {decodeError}
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: ENTER TOKEN DIRECTLY */}
            {activeTab === "manual" && (
              <div style={{ width: "100%", padding: "16px 10px", textAlign: "center" }}>
                <p style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "var(--ink)" }}>
                  [ ⌨️ Manual Token Entry ]
                </p>
                <p style={{ margin: "8px 0 16px", fontSize: "0.86rem", color: "var(--ink-soft)" }}>
                  Enter the 16-character hexadecimal token or full URI string.
                </p>

                <div style={{ display: "flex", gap: 10, maxWidth: 360, margin: "0 auto", flexWrap: "wrap", justifyContent: "center" }}>
                  <input
                    type="text"
                    placeholder="e.g. 7599a9303572da76"
                    value={tokenInput}
                    onChange={(e) => setTokenInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") navigateToEmergency(tokenInput);
                    }}
                    className="scanner-input"
                    style={{ flex: 1, minWidth: 200 }}
                  />
                  <button
                    type="button"
                    className="button button--primary"
                    onClick={() => navigateToEmergency(tokenInput)}
                    disabled={isNavigating || !tokenInput.trim()}
                    style={{ borderRadius: 12 }}
                  >
                    Open Card →
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Offscreen Canvas for Frame Capture */}
          <canvas ref={canvasRef} style={{ display: "none" }} />

          {/* Direct Input Bar at Bottom of Viewfinder */}
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center", marginTop: 8 }}>
            <input
              type="text"
              placeholder="Or paste token: e.g. 7599a9303572da76 or sanchai://p/..."
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") navigateToEmergency(tokenInput);
              }}
              className="scanner-input"
            />
            <button
              className="button button--primary"
              type="button"
              onClick={() => navigateToEmergency(tokenInput)}
              disabled={isNavigating || !tokenInput.trim()}
            >
              {isNavigating ? "Opening Card..." : "Resolve Emergency Card →"}
            </button>
          </div>
        </div>
      </section>

      {/* Preset Patient Demo Scans */}
      <section className="timeline-card" style={{ marginTop: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 12 }}>
          <div>
            <p className="section-title" style={{ margin: 0 }}>
              One-Click Emergency Demo Cards
            </p>
            <p style={{ margin: "4px 0 0", color: "var(--ink-soft)", fontSize: "0.85rem" }}>
              Click any verified patient to simulate an instantaneous optical QR scanner read.
            </p>
          </div>
          <span className="tag tag--committed">3 Seeded Clinical Patients</span>
        </div>

        <div className="timeline">
          {PRESET_TOKENS.map((preset) => (
            <article
              key={preset.token}
              className="timeline-item"
              style={{ cursor: "pointer", transition: "all 0.18s ease" }}
              onClick={() => navigateToEmergency(preset.token)}
            >
              <div className="timeline-item__top">
                <span className="timeline-item__label" style={{ fontSize: "1.05rem" }}>
                  {preset.patientName}
                </span>
                <span className="tag tag--neutral" style={{ fontWeight: 800 }}>
                  Blood {preset.bloodGroup}
                </span>
              </div>
              <p className="timeline-item__summary">
                Critical flag: <strong>{preset.severity}</strong> · Token: <code>{preset.token}</code>
              </p>
              <div style={{ marginTop: 8, display: "flex", gap: 12, alignItems: "center" }}>
                <span style={{ fontSize: "0.82rem", color: "var(--accent)", fontWeight: 700 }}>
                  Click to Simulate Optical Read →
                </span>
                <Link
                  href={`/patients/${preset.patientId}`}
                  onClick={(e) => e.stopPropagation()}
                  style={{ fontSize: "0.82rem", color: "var(--ink-soft)", textDecoration: "underline" }}
                >
                  View Patient Ledger
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
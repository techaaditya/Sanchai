"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function NavHeader() {
  const pathname = usePathname();

  const links = [
    { href: "/", label: "Home", badge: null },
    { href: "/intake", label: "Intake", badge: "Live" },
    { href: "/chatbot", label: "SanchAI", badge: "AI" },
    { href: "/patients/patient_ram", label: "Patients", badge: null },
    { href: "/scan", label: "QR Scanner", badge: null },
    { href: "/evidence", label: "Evidence", badge: "96.7%" },
  ];

  return (
    <header className="nav-header">
      <div className="nav-header__inner">
        <Link href="/" className="nav-header__brand" title="Sanchai (सञ्चै) Home">
          <div className="brand-logo-container">
            <img
              src="/logo512.svg"
              alt="Sanchai Logo"
              className="brand-logo-img"
              width={34}
              height={34}
            />
          </div>
          <div className="brand-text">
            <span className="brand-name">Sanchai</span>
            <span className="brand-sub">सञ्चै · Clinical Health Ledger</span>
          </div>
        </Link>

        <nav className="nav-header__links">
          {links.map((link) => {
            const isActive =
              link.href === "/"
                ? pathname === "/"
                : pathname?.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href as any}
                className={`nav-link ${isActive ? "nav-link--active" : ""}`}
              >
                <span>{link.label}</span>
                {link.badge ? (
                  <span className="nav-link__badge">{link.badge}</span>
                ) : null}
              </Link>
            );
          })}
        </nav>

        <div className="nav-header__meta">
          <div
            className="model-chip"
            title="Cloud: gemma4:31b-cloud (Ollama Cloud) | Edge Fallback: gemma4:e2b-it-qat (Local Ollama)"
          >
            <span className="model-chip__dot"></span>
            <span className="model-chip__name">gemma4:31b-cloud</span>
            <span className="model-chip__fallback-tag">offline fallback</span>
          </div>
        </div>
      </div>
    </header>
  );
}

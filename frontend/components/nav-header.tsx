"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function NavHeader() {
  const pathname = usePathname();

  const links = [
    { href: "/", label: "Home", badge: null },
    { href: "/intake", label: "Intake Studio", badge: "Live" },
    { href: "/chatbot", label: "SanchAI", badge: "AI" },
    { href: "/patients/patient_ram", label: "Patient Record", badge: null },
    { href: "/scan", label: "QR Scanner", badge: null },
    { href: "/evidence", label: "NepClinBench Evidence", badge: "96.7%" },
  ];

  return (
    <header className="nav-header">
      <div className="nav-header__inner">
        <Link href="/" className="nav-header__brand">
          <span className="brand-logo">स</span>
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
          <span className="model-chip" title="Active Model">
            <span className="model-chip__dot"></span>
            gemma4:31b-cloud
          </span>
        </div>
      </div>
    </header>
  );
}

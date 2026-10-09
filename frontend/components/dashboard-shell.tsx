import type { ReactNode } from "react";

export function DashboardShell({ children }: { children: ReactNode }) {
  return <main className="shell">{children}</main>;
}
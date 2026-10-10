"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { getApiBaseUrl } from "@/lib/api";

type ApprovalActionsProps = {
  entryId: string;
};

export function ApprovalActions({ entryId }: ApprovalActionsProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [message, setMessage] = useState<string | null>(null);
  const [committed, setCommitted] = useState(false);

  const commitRecord = () => {
    startTransition(async () => {
      setMessage(null);

      try {
        const response = await fetch(`${getApiBaseUrl()}/api/v1/entries/${entryId}/commit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) {
          throw new Error(`Commit failed with status ${response.status}`);
        }

        setCommitted(true);
        setMessage("Record committed successfully.");
        router.refresh();
      } catch {
        setMessage("Could not commit the record right now.");
      }
    });
  };

  return (
    <>
      <div className="actions">
        <button className="button button--primary" type="button" onClick={commitRecord} disabled={isPending || committed}>
          {committed ? "Committed" : isPending ? "Committing..." : "Commit to record"}
        </button>
        <button className="button button--secondary" type="button" disabled={isPending}>
          Send back for correction
        </button>
      </div>
      {message ? <p className="footer-note">{message}</p> : null}
    </>
  );
}
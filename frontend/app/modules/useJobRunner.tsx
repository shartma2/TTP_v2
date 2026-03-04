"use client";

import { useEffect, useRef, useState } from "react";

export function useJobRunner() {
  const [output, setOutput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const pollTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (pollTimeout.current) {
        clearTimeout(pollTimeout.current);
        pollTimeout.current = null;
      }
    };
  }, []);

  const run = async (module: string, payload: any) => {
    if (loading) return;

    setOutput("");
    setJobId(null);

    try {
      setLoading(true);

      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ module, payload }),
      });

      const created = await response.json();
      const jid = (created?.jobId ?? created?.job_id) as string | undefined;
      if (!jid) throw new Error("Job ID not returned");

      setJobId(jid);
      setOutput("Job queued. Waiting for result...");

      const poll = async () => {
        try {
          const res = await fetch(`/api/jobs/${jid}`);
          const job = await res.json();
          const status = job?.status as string | undefined;

          if (status === "done") {
            setOutput(renderResult(job?.result));
            setLoading(false);
            return;
          }

          if (status === "failed") {
            setOutput(`Job failed: ${job?.error ?? "Unknown error"}`);
            setLoading(false);
            return;
          }

          pollTimeout.current = setTimeout(poll, 1000);
        } catch {
          pollTimeout.current = setTimeout(poll, 1500);
        }
      };

      await poll();
    } catch {
      setOutput("Failed to create or poll job.");
      setLoading(false);
    }
  };

  return { output, loading, jobId, run, setOutput };
}

function renderResult(result: any): string {
  if (!result) return "No result.";
  if (result.response) {
    if (typeof result.response === "string") return result.response;
    return JSON.stringify(result.response, null, 2);
  }
  return JSON.stringify(result, null, 2);
}
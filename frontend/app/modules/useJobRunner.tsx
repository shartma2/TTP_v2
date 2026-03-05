"use client";

import { useEffect, useRef, useState } from "react";
import { JobStatus, JobResponse } from "@/app/types";

export function useJobRunner() {
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

  const run = async (module: string, payload: any): Promise<{ jid: string; job: JobResponse } | null> => {
    if (loading) return null;

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

      const poll = async (): Promise<{ jid: string; job: JobResponse }> => {
        try {
          const res = await fetch(`/api/jobs/${jid}`);
          const job = (await res.json()) as JobResponse;
          const status = job?.status;

          if (status === "done" || status === "failed") {
            setLoading(false);
            return { jid, job };
          }
          return await new Promise((resolve) => {
            pollTimeout.current = setTimeout(async () => resolve(await poll()), 1000);
          });
        } catch {
          return await new Promise((resolve) => {
            pollTimeout.current = setTimeout(async () => resolve(await poll()), 1500);
          });
        }
      };

      return await poll();
    } catch {
      setLoading(false);
      return null;
    }
  };

  return { loading, jobId, run };
}


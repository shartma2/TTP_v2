"use client";

import { useEffect, useRef, useState } from "react";
import { Job } from "@/app/types";

export function useJobRunner() {
  const [loading, setLoading] = useState<boolean>(false);
  const [jobId, setJobId] = useState<string | null>(null);

  const pollIdsRef = useRef<Set<string>>(new Set())
  const pollTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isPolling = useRef<boolean>(false);
  const onUpdateRef = useRef<((job: Job) => void) | null>(null);

  useEffect(() => {
    return () => {
      if (pollTimeout.current) {
        clearTimeout(pollTimeout.current);
        pollTimeout.current = null;
      }
    };
  }, []);

  const run = async (module: string, payload: any): Promise<string | null> => {
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
      return jid;
    } catch {
      return null;
    } finally {
      setLoading(false);
    }
  };

  const setPollIds = (ids: string[]) => {
    pollIdsRef.current = new Set(ids.filter(Boolean));
  };

  const addPollIds = (ids: string[]) => {
    const s = pollIdsRef.current;
    for (const id of ids) if (id) s.add(id);
  };

  const startPolling = (onUpdate: (job: Job) => void, intervalMs = 1000) => {

    if (isPolling.current) return;

    isPolling.current = true;

    onUpdateRef.current = onUpdate;

    const isTerminal = (status?: string) => status === "done" || status === "failed";

    const tick = async () => {
      if (!isPolling.current) return;

      const ids = Array.from(pollIdsRef.current);
      if (ids.length === 0) {
        isPolling.current = false;
        return;
      }

      const results = await Promise.allSettled(
        ids.map(async (id) => {
          const res = await fetch(`/api/jobs/${id}`);
          const job = (await res.json()) as Job;
          onUpdateRef.current?.(job);
          return job;
        })
      );

      for (const r of results) {
        if (r.status !== "fulfilled") continue;
        const job = r.value;
        const id = (job.jobId) as string | undefined;
        if (!id) continue;
        if (isTerminal(job.status)) pollIdsRef.current.delete(id);
      }

      pollTimeout.current = setTimeout(() => {
        tick().catch(() => {
          if (!isPolling.current) return;
          pollTimeout.current = setTimeout(() => {
            tick().catch(() => { });
          }, Math.max(1500, intervalMs));
        });
      }, intervalMs);
    };
    void tick();
  };

  const stopPolling = () => {
    isPolling.current = false;
    if (pollTimeout.current) {
      clearTimeout(pollTimeout.current);
      pollTimeout.current = null;
    }
  };

  return { loading, jobId, run, setPollIds, addPollIds, startPolling, stopPolling };
}
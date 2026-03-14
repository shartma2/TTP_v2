"use client";

import { useEffect, useState } from "react";
import { renderResult } from "@/app//util/renderResult";
import { shortenJobId } from "../util/shortenJobId";
import ModuleCardSpec from "./ModuleCardSpec";

type ResultDisplayCardProps = {
  title: string;
  description?: string;
  selectedJobId: string | null;
};

export default function ResultDisplayCard({ title, description, selectedJobId }: ResultDisplayCardProps) {
  const [jobId, setJobId] = useState<string>(selectedJobId ?? "");
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState<string>("");

  useEffect(() => {
    setJobId(selectedJobId ?? "");
  }, [selectedJobId]);

  const load = async () => {
    if (!jobId.trim()) {
      setOutput("Please select a job in the sidebar (or paste a Job ID).");
      return;
    }

    try {
      setLoading(true);
      setOutput("");

      const res = await fetch(`/api/jobs/${jobId.trim()}`);
      const job = await res.json();

      const status = job?.status as string | undefined;
      if (status === "failed") {
        setOutput(`Job failed: ${job?.error ?? "Unknown error"}`);
        return;
      }

      if (status !== "done") {
        setOutput(`Job status: ${status ?? "unknown"}`);
        return;
      }

      setOutput(renderResult(job?.result));
    } catch {
      setOutput("Failed to load job.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModuleCardSpec
      title={title}
      description={description}
      footer={
        <div
          className="min-h-[6rem] w-full rounded-2xl border border-white/10 bg-gray-950/60 p-4 text-sm text-gray-200 shadow-inner backdrop-blur-xl"
          aria-live="polite"
        >
          {output || "Output will appear here."}
        </div>
      }
    >
      <div className="mb-4 rounded-2xl border border-white/10 bg-gray-950/40 px-4 py-3 text-sm text-gray-300">
        <span className="font-medium text-gray-200">Source Job ID:</span>{" "}
        {jobId ? (
          <span title={jobId} className="font-mono text-gray-100">
            {shortenJobId(jobId)}
          </span>
        ) : (
          <span className="text-gray-400">None selected</span>
        )}
      </div>

      <button
        type="button"
        onClick={load}
        disabled={loading}
        className="w-full rounded-2xl bg-white/10 px-6 py-3 text-lg font-medium tracking-wide transition hover:bg-white/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 disabled:opacity-60"
      >
        {loading ? "Loading..." : "Load"}
      </button>
    </ModuleCardSpec>
  );
}


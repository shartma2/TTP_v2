"use client";

import { useEffect, useRef, useState } from "react";
import { useJobRunner } from "../util/jobRunner";
import ModuleCardSpec from "./ModuleCardSpec";

type RefineModuleCardProps = {
  title: string;
  description?: string;
  selectedJobId: string | null;
  onJobQueued?: () => void;
};

export default function RefineModuleCard({
  title = "Refinement",
  description = "Refine a job.",
  selectedJobId,
  onJobQueued
}: RefineModuleCardProps) {
  const { loading, jobId, run } = useJobRunner();
  const [message, setMessage] = useState<string>("");
  const [sourceJobId, setSourceJobId] = useState<string>(selectedJobId ?? "")
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    setSourceJobId(selectedJobId ?? "");
  }, [selectedJobId]);

  const resizeInput = () => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  };


  const runModule = async () => {
    if (loading) return;

    if (!sourceJobId.trim()) {
      //Set Error Message
      return
    }

    const res = await fetch(`/api/jobs/${sourceJobId.trim()}`);
    const sourceJob = res.ok ? await res.json() : null

    const jid = await run("refine", {
      source_job_id: selectedJobId,
      message: message,
      result: sourceJob,
    });

    if (!jid) {
      //Set Error Message
      return;
    }

    onJobQueued?.();
  };

  useEffect(() => {
    resizeInput();
  }, [message]);

  return (
    <ModuleCardSpec
      title={title}
      description={description}
    >
      <div className="mb-3 rounded-2xl border border-white/10 bg-gray-950/40 px-4 py-3 text-sm text-gray-300">
        <span className="font-medium text-gray-200">Selected job:</span>{" "}
        {sourceJobId || "None"}
      </div>

      <textarea
        ref={inputRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onInput={resizeInput}
        placeholder="Type your refinement instructons..."
        rows={1}
        className="mb-4 w-full resize-none overflow-hidden rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-100 outline-none placeholder:text-gray-400 focus:border-purple-400"
      />

      <button
        type="button"
        onClick={runModule}
        disabled={loading}
        className="w-full rounded-2xl bg-white/10 px-6 py-3 text-lg font-medium tracking-wide transition hover:bg-white/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 disabled:opacity-60"
      >
        {loading ? "Queuing..." : "Run"}
      </button>

      {loading && jobId && <p className="mt-3 text-xs text-gray-400">Job ID: {jobId}</p>}
    </ModuleCardSpec>
  );
}
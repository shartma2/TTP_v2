"use client";

import { useEffect, useState } from "react";
import ModuleCardSpec from "./ModuleCardSpec";
import { useJobRunner } from "./useJobRunner";

type LoopModuleCardProps = {
  title: string;
  module: string;
  description?: string;
  selectedJobId: string | null;
  sourceJobLabel?: string;
};

export default function LoopModuleCard({
  title,
  module,
  description,
  selectedJobId,
  sourceJobLabel,
}: LoopModuleCardProps) {
  const [sourceJobId, setSourceJobId] = useState<string>(selectedJobId ?? "");
  const [note, setNote] = useState<string>(""); // optional second input (example)
  const { output, loading, jobId, run, setOutput } = useJobRunner();

  useEffect(() => {
    setSourceJobId(selectedJobId ?? "");
  }, [selectedJobId]);

  const runDerived = () => {
    if (!sourceJobId.trim()) {
      setOutput("Please select a source job in the sidebar (or paste a Job ID).");
      return;
    }
    run(module, { sourceJobId, note });
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
      <label className="mb-2 block text-sm font-medium text-gray-200" htmlFor={`${module}-sourceJob`}>
        {sourceJobLabel ?? "Source Job ID"}
      </label>
      <input
        id={`${module}-sourceJob`}
        value={sourceJobId}
        onChange={(e) => setSourceJobId(e.target.value)}
        placeholder="Click a job in the sidebar or paste Job ID..."
        className="mb-4 w-full rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-100 outline-none placeholder:text-gray-400 focus:border-purple-400"
      />

      <label className="mb-2 block text-sm font-medium text-gray-200" htmlFor={`${module}-note`}>
        Options (example)
      </label>
      <input
        id={`${module}-note`}
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Optional parameter..."
        className="mb-4 w-full rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-100 outline-none placeholder:text-gray-400 focus:border-purple-400"
      />

      <button
        type="button"
        onClick={runDerived}
        disabled={loading}
        className="w-full rounded-2xl bg-white/10 px-6 py-3 text-lg font-medium tracking-wide transition hover:bg-white/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 disabled:opacity-60"
      >
        {loading ? "Running..." : "Run"}
      </button>

      {loading && jobId && <p className="mt-3 text-xs text-gray-400">Job ID: {jobId}</p>}
    </ModuleCardSpec>
  );
}
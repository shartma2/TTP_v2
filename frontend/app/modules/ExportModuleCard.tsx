"use client";

import { useEffect, useMemo, useState } from "react";
import ModuleCardSpec from "./ModuleCardSpec";
import { useJobRunner } from "./useJobRunner";

type ExportModuleCardProps = {
  title?: string;
  description?: string;
  selectedJobId: string | null;
  sourceJobLabel?: string;
};

type ExportFormat = ".json" | ".txt";

export default function ExportModuleCard({
  title = "Export",
  description = "Export a finished job to a file.",
  selectedJobId,
  sourceJobLabel,
}: ExportModuleCardProps) {
  const [sourceJobId, setSourceJobId] = useState<string>(selectedJobId ?? "");
  const [format, setFormat] = useState<ExportFormat>(".json");

  // For export we want a short status line, not a big result box
  const [statusText, setStatusText] = useState<string>("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  const { loading, jobId, run, setOutput } = useJobRunner();

  useEffect(() => {
    setSourceJobId(selectedJobId ?? "");
  }, [selectedJobId]);

  const payload = useMemo(() => {
    return {
      sourceJobId: sourceJobId || null,
      format,
    };
  }, [sourceJobId, format]);

  const runExport = async () => {
    if (loading) return;

    setStatusText("");
    setFileName(null);
    setDownloadUrl(null);

    if (!sourceJobId.trim()) {
      setStatusText("Please select a source job in the sidebar (or paste a Job ID).");
      return;
    }

    try {
      await run("export", payload);

      const jid = jobId; 
      const resolvedJobId =
        jid ?? null;

      if (!resolvedJobId) {
        setStatusText("Export finished. (No job id available to fetch file metadata.)");
        return;
      }

      const res = await fetch(`/api/jobs/${resolvedJobId}`);
      const job = await res.json();

      if (job?.status === "failed") {
        setStatusText(`Export failed: ${job?.error ?? "Unknown error"}`);
        return;
      }

      const result = job?.result ?? {};
      const name =
        result?.fileName ??
        result?.filename ??
        result?.name ??
        null;

      const url =
        result?.url ??
        result?.downloadUrl ??
        (name ? `/api/jobs/${resolvedJobId}/download` : null);

      if (name) {
        setFileName(String(name));
        setDownloadUrl(url ? String(url) : null);
        setStatusText(`Ready: ${name}`);
      } else {
        setStatusText("Export finished, but no file name returned.");
      }
    } catch {
      setStatusText("Failed to create or poll export job.");
    } finally {
      setOutput("");
    }
  };

  const canDownload = Boolean(fileName && downloadUrl);

  return (
    <ModuleCardSpec
      title={title}
      description={description}
      footer={
        <div className="flex items-center gap-3">
          <div
            className="flex-1 rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-200 shadow-inner backdrop-blur-xl"
            aria-live="polite"
          >
            {statusText || "No export yet."}
          </div>

          <a
            href={downloadUrl ?? "#"}
            download={fileName ?? undefined}
            aria-disabled={!canDownload}
            onClick={(e) => {
              if (!canDownload) e.preventDefault();
            }}
            className={`rounded-2xl px-4 py-3 text-sm font-medium transition
              ${canDownload ? "bg-white/10 hover:bg-white/20" : "bg-white/5 opacity-50 cursor-not-allowed"}`}
          >
            Download
          </a>
        </div>
      }
    >
      <label className="mb-2 block text-sm font-medium text-gray-200" htmlFor="export-sourceJob">
        {sourceJobLabel ?? "Source Job ID"}
      </label>
      <input
        id="export-sourceJob"
        value={sourceJobId}
        onChange={(e) => setSourceJobId(e.target.value)}
        placeholder="Click a job in the sidebar or paste Job ID..."
        className="mb-4 w-full rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-100 outline-none placeholder:text-gray-400 focus:border-purple-400"
      />

      
      <label className="mb-2 block text-sm font-medium text-gray-200" htmlFor="export-format">
        Format
      </label>
      <select
        id="export-format"
        value={format}
        onChange={(e) => setFormat(e.target.value as ExportFormat)}
        className="mb-4 w-full rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-100 outline-none focus:border-purple-400"
      >
        <option value=".json">.json</option>
        <option value=".txt">.txt</option>
      </select>

      <button
        type="button"
        onClick={runExport}
        disabled={loading}
        className="w-full rounded-2xl bg-white/10 px-6 py-3 text-lg font-medium tracking-wide transition hover:bg-white/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 disabled:opacity-60"
      >
        {loading ? "Running..." : "Run"}
      </button>

      {loading && jobId && <p className="mt-3 text-xs text-gray-400">Job ID: {jobId}</p>}
    </ModuleCardSpec>
  );
}
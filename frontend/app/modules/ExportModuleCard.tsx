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

type ExportJobResult = {
  fileName: string;
  contentType: string;
  sizeBytes: number;
  dataBase64: string;
};

export default function ExportModuleCard({
  title = "Export",
  description = "Export a finished job to a file.",
  selectedJobId,
  sourceJobLabel,
}: ExportModuleCardProps) {
  const [sourceJobId, setSourceJobId] = useState<string>(selectedJobId ?? "");
  const [format, setFormat] = useState<ExportFormat>(".json");

  const [error, setError] = useState<string>("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  const { loading, jobId, run } = useJobRunner();

  useEffect(() => {
    setSourceJobId(selectedJobId ?? "");
  }, [selectedJobId]);

  const reset = () => {
    setError("");
    setFileName(null);
    setFileSize(null);
    if (downloadUrl) {
      URL.revokeObjectURL(downloadUrl);
      setDownloadUrl(null);
    }
  };

  useEffect(() => {
    return () => {
      if (downloadUrl) URL.revokeObjectURL(downloadUrl);
    };
  }, []);

  const runExport = async () => {
    if (loading) return;

    reset();

    if (!sourceJobId.trim()) {
      setError("Please select a source job from the sidebar or paste a Job ID.")
      return;
    }

    const resp = await run("export", { sourceJobId: sourceJobId.trim(), format });

    if (!resp) {
      setError("Failed to create or poll job.")
      return;
    }

    /*   const job = resp.job;
       if (job.status === "failed") {
         setError(job?.error?.message ?? job?.error ?? "Unknown error");
         return;
       }
   
       const r = job.result as ExportJobResult | undefined;
       if (!r?.fileName || !r?.dataBase64) {
         setError("Export finished, but no file returned.");
         return;
       }
     */
    //dummy
    const r: ExportJobResult = {
      fileName: "report.csv",
      contentType: "text/csv",
      sizeBytes: 32,
      dataBase64: "Y29sMSxjb2wyCnZhbDEsdmFsMg==" // base64 for: col1,col2\nval1,val2
    };
    const blob = base64ToBlob(r.dataBase64, r.contentType || guessContentType(format));
    const url = URL.createObjectURL(blob);

    setFileName(r.fileName);
    setFileSize(String(typeof r.sizeBytes === "number" ? r.sizeBytes : blob.size));
    setDownloadUrl(url);
  };

  const canDownload = useMemo(() => Boolean(downloadUrl && fileName), [downloadUrl, fileName]);

  return (
    <ModuleCardSpec title={title} description={description}>
      <label className="mb-2 block text-sm font-medium text-gray-200" htmlFor="export-sourceJob">
        Source Job ID
      </label>
      <input
        id="export-sourceJob"
        value={sourceJobId}
        onChange={(e) => setSourceJobId(e.target.value)}
        disabled={loading}
        className="mb-4 w-full rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-100 outline-none placeholder:text-gray-400 focus:border-purple-400 disabled:opacity-60"
      />

      <label className="mb-2 block text-sm font-medium text-gray-200" htmlFor="export-format">
        Format
      </label>
      <select
        id="export-format"
        value={format}
        onChange={(e) => setFormat(e.target.value as ExportFormat)}
        disabled={loading}
        className="mb-4 w-full rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-100 outline-none focus:border-purple-400 disabled:opacity-60"
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

      <div className="mt-6 flex items-center gap-3">
        <div className="flex-1 rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-200 shadow-inner backdrop-blur-xl">
          {error
            ? `Error: ${error}`
            : fileName
              ? `Ready: ${fileName}${fileSize ? ` · ${formatBytes(Number(fileSize))}` : ""}`
              : "No export yet."}
        </div>

        <a
          href={downloadUrl ?? "#"}
          download={fileName ?? undefined}
          onClick={(e) => {
            if (!canDownload) e.preventDefault();
          }}
          className={`rounded-2xl px-4 py-3 text-sm font-medium transition ${canDownload ? "bg-white/10 hover:bg-white/20" : "bg-white/5 opacity-50 cursor-not-allowed"
            }`}
        >
          Download
        </a>
      </div>
    </ModuleCardSpec>
  );
}

function guessContentType(format: ExportFormat) {
  return format === ".json" ? "application/json" : "text/plain; charset=utf-8";
}

function base64ToBlob(b64: string, contentType: string) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type: contentType });
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  const mb = kb / 1024;
  return `${mb.toFixed(1)} MB`;
}
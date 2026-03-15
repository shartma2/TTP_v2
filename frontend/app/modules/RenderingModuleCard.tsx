"use client";

import { useEffect, useMemo, useState } from "react";
import ModuleCardSpec from "./ModuleCardSpec";
import { useJobRunner } from "../util/jobRunner";
import { shortenJobId } from "../util/shortenJobId";
import { openDiagramWindow } from "../util/renderDiagramWindow";
import type { Job, RenderJobResult } from "@/app/types";


type RenderingModuleCardProps = {
    title?: string;
    description?: string;
    selectedJobId: string | null;
    jobs: Job[];
    onJobQueued: () => void;
};

export default function RenderingModuleCard({
    title = "Rendering",
    description = "Render a process model from a finished pipeline job.",
    selectedJobId,
    jobs,
    onJobQueued,
}: RenderingModuleCardProps) {
    const { loading, run } = useJobRunner();
    const [sourceJobId, setSourceJobId] = useState<string>(selectedJobId ?? "");
    const [exportJobId, setExportJobId] = useState<string | null>(null);
    const [error, setError] = useState<string>("");
    const [fileName, setFileName] = useState<string | null>(null);
    const [fileSize, setFileSize] = useState<number | null>(null);
    const [svgData, setSvgData] = useState<any>(null);
    const [downloadUrl, setDownloadUrl] = useState<string | null>(null);


    useEffect(() => {
        setSourceJobId(selectedJobId ?? "");
    }, [selectedJobId]);

    const resetResult = () => {
        setError("");
        setFileName(null);
        setFileSize(null);
        setSvgData(null);
        if (downloadUrl) {
            URL.revokeObjectURL(downloadUrl);
            setDownloadUrl(null);
        }
    };

    useEffect(() => {
        return () => {
            if (downloadUrl) URL.revokeObjectURL(downloadUrl);
        };
    }, [downloadUrl]);

    const exportJob = useMemo(() => {
        if (!exportJobId) return null;
        return jobs.find((j) => (j.jobId ?? (j as any).job_id) === exportJobId) ?? null;
    }, [jobs, exportJobId]);

    const exportStatus = (exportJob?.status ?? "").toLowerCase();

    useEffect(() => {
        if (!exportJobId) return;
        if (!exportJob) return;

        if (exportStatus === "failed") {
            const msg = exportJob?.error?.message ?? exportJob?.error ?? "Unknown error";
            setError(String(msg));
            return;
        }

        if (exportStatus !== "done") return;

        const r = (exportJob?.result) as RenderJobResult | undefined;
        if (!r?.fileName || !r?.dataBase64) {
            setError("Export finished, but no file returned.");
            return;
        }

        if (fileName === r.fileName && downloadUrl) return;

        resetResult();

        const blob = base64ToBlob(r.dataBase64, r.contentType);
        const url = URL.createObjectURL(blob);

        setFileName(r.fileName);
        setFileSize(typeof r.sizeBytes === "number" ? r.sizeBytes : blob.size);
        setDownloadUrl(url);
        setSvgData((r as any).svg ?? null)
    }, [exportJobId, exportJob, exportStatus]);

    const canDownload = useMemo(() => Boolean(downloadUrl && fileName), [downloadUrl, fileName]);
    const exportActive = exportStatus === "queued" || exportStatus === "running";
    const runDisabled = loading || exportActive;

    const runModule = async () => {
        if (runDisabled) return;

        setError("");
        resetResult();

        if (!sourceJobId.trim()) {
            setError("Please select a source job from the sidebar or paste a Job ID.");
            return;
        }

        setExportJobId(null);

        const res = await fetch(`/api/jobs/${sourceJobId.trim()}`);

        const jid = await run("rendering", {
            source_job_id: sourceJobId.trim(),
            result: res.ok ? await res.json() : null,
        });

        if (!jid) {
            setError("Failed to create rendering job.");
            return;
        }

        setExportJobId(jid);
        onJobQueued();
    };

    const statusLine = useMemo(() => {
        if (error) return `Error: ${error}`;
        if (exportActive) return `Export ${exportStatus}...`;
        if (fileName) return `Ready: ${fileName}${typeof fileSize === "number" ? ` · ${formatBytes(fileSize)}` : ""}`;
        if (exportJobId && exportStatus === "done") return "Rendering done.";
        return "No render yet.";
    }, [error, exportActive, exportStatus, fileName, fileSize, exportJobId]);

    const showDiagram = () => {
        if (!svgData) return;
        openDiagramWindow(svgData);
    };


    return (
        <ModuleCardSpec title={title} description={description}>
            <div className="mb-4 rounded-2xl border border-white/10 bg-gray-950/40 px-4 py-3 text-sm text-gray-300">
                <span className="font-medium text-gray-200">Source Job ID:</span>{" "}
                {sourceJobId ? (
                    <span title={sourceJobId} className="font-mono text-gray-100">
                        {shortenJobId(sourceJobId)}
                    </span>
                ) : (
                    <span className="text-gray-400">None selected</span>
                )}
            </div>

            <button
                type="button"
                onClick={runModule}
                disabled={runDisabled}
                className="w-full rounded-2xl bg-white/10 px-6 py-3 text-lg font-medium tracking-wide transition hover:bg-white/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 disabled:opacity-60"
            >
                {loading ? "Queuing..." : exportActive ? "Running..." : "Run"}
            </button>

            {exportJobId && (
                <p className="mt-3 text-xs text-gray-400">
                    Render Job ID: {exportJobId}
                </p>
            )}

            <div className="mt-6 flex items-center gap-3">
                <div className="flex-1 rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-200 shadow-inner backdrop-blur-xl">
                    {statusLine}
                </div>
                <button
                    type="button"
                    onClick={showDiagram}
                    disabled={!svgData}
                    className={`rounded-2xl px-4 py-3 text-sm font-medium transition ${svgData ? "bg-white/10 hover:bg-white/20" : "bg-white/5 opacity-50 cursor-not-allowed"
                        }`}
                >
                    Show Diagram
                </button>
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
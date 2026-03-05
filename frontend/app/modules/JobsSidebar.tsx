"use client";

import { useEffect, useMemo } from "react";
import type { Job } from "@/app/types";
import { useJobRunner } from "./useJobRunner";


export default function JobsSidebar({
    jobs,
    loading,
    error,
    onReload,
    selectedJobId,
    onSelectJob,
    onJobUpdate,
}: {
    jobs: Job[];
    loading: boolean;
    error: string;
    onReload: () => void;
    selectedJobId: string | null;
    onSelectJob: (id: string) => void;
    onJobUpdate: (job: Job) => void;
}) {
    const { startPolling, stopPolling, setPollIds } = useJobRunner();

    const updatedAtOf = (j: Job) =>
        j.finishedAt ?? j.startedAt ?? j.createdAt;

    const sorted = useMemo(() => {
        if (!Array.isArray(jobs)) return [];

        return [...jobs]
            .filter((j) => j.jobId)
            .sort((a, b) => {
                const ta = Date.parse(updatedAtOf(a) || "");
                const tb = Date.parse(updatedAtOf(b) || "");
                if (Number.isNaN(ta) || Number.isNaN(tb)) return 0;
                return tb - ta;
            });
    }, [jobs]);

    useEffect(() => {
        const activeIds = sorted
            .filter((j) => {
                const s = (j.status || "").toLowerCase();
                return s === "queued" || s === "running";
            })
            .map((j) => j.jobId);

        setPollIds(activeIds);

        if (activeIds.length === 0) {
            stopPolling();
            return;
        }

        startPolling(onJobUpdate, 1000);

    }, [sorted, setPollIds, startPolling, stopPolling, onJobUpdate]);

    return (
        <aside className="h-[calc(100vh-2rem)] w-full rounded-3xl border border-white/10 bg-white/5 p-5 text-white shadow-2xl shadow-black/50 backdrop-blur-2xl">
            <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-semibold tracking-tight">Jobs</h3>
                <button
                    type="button"
                    onClick={onReload}
                    disabled={loading}
                    className="rounded-xl bg-white/10 px-3 py-1 text-xs font-medium hover:bg-white/20 disabled:opacity-60"
                >
                    {loading ? "Loading..." : "Reload"}
                </button>
            </div>

            {error && (
                <div className="mb-3 rounded-2xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
                    {error}
                </div>
            )}

            <div className="space-y-2">
                {sorted.length === 0 ? (
                    <div className="rounded-2xl border border-white/10 bg-gray-950/40 p-4 text-sm text-gray-300">
                        No jobs loaded.
                    </div>
                ) : (
                    sorted.map((j) => {
                        const updatedAt = updatedAtOf(j);

                        return (
                            <button
                                key={j.jobId}
                                type="button"
                                onClick={() => onSelectJob(j.jobId)}
                                className={`w-full text-left rounded-2xl border px-4 py-3 transition
                                ${selectedJobId === j.jobId ? "border-purple-400/50 bg-purple-500/10" : "border-white/10 bg-gray-950/40 hover:bg-gray-900/60"}
                                `}
                            >
                                <div className="flex items-center justify-between gap-3">
                                    <div className="min-w-0">
                                        <div className="truncate text-sm font-medium text-gray-100">
                                            {j.module ?? "job"} <span className="text-gray-500">·</span>{" "}
                                        </div>
                                        <div className="truncate text-xs text-gray-400">{j.jobId}</div>
                                    </div>

                                    <span
                                        className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-semibold ${badge(
                                            j.status
                                        )}`}
                                    >
                                        {j.status}
                                    </span>
                                </div>

                                {(updatedAt || j.createdAt) && (
                                    <div className="mt-2 text-xs text-gray-500">
                                        {updatedAt
                                            ? `updated: ${fmt(updatedAt)}`
                                            : `created: ${fmt(j.createdAt!)}`}
                                    </div>
                                )}
                            </button>
                        );
                    })
                )}
            </div>
        </aside>
    );
}

function fmt(iso: string) {
    const d = new Date(iso);
    return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
}

function badge(status: string) {
    const s = (status || "").toLowerCase();
    if (s === "running") return "border-blue-500/30 bg-blue-500/15 text-blue-200";
    if (s === "queued") return "border-gray-500/30 bg-gray-500/15 text-gray-200";
    if (s === "done") return "border-green-500/30 bg-green-500/15 text-green-200";
    if (s === "failed") return "border-red-500/30 bg-red-500/15 text-red-200";
    return "border-white/15 bg-white/10 text-gray-200";
}
"use client";

import { useCallback, useEffect, useState } from "react";
import type { Job } from "@/app/types";
import JobsSidebar from "./modules/JobsSidebar";

import StandardModuleCard from "./modules/StandardModuleCard";
import ResultDisplayCard from "./modules/ResultModuleCard";
import RefineModuleCard from "./modules/RefineModule"
import ExportModuleCard from "./modules/ExportModuleCard";

type ModuleConfig =
  | { kind: "standard"; title: string; module: string; description?: string }
  | { kind: "refine"; title: string; description?: string; sourceJobLabel?: string }
  | { kind: "export"; title: string; description?: string }
  | { kind: "display"; title: string; description?: string };

const SIDEBAR_W = "clamp(280px,30vw,420px)";

export default function Home() {
  const modules: ModuleConfig[] = [
    {
      kind: "standard",
      title: "Chain-of-Thought",
      module: "cot",
      description: "Send a message to the CoT module.",
    },
    {
      kind: "standard",
      title: "Pipeline Module",
      module: "pipeline",
      description: "Execute a predefined pipeline of tasks.",
    },
    {
      kind: "refine",
      title: "Human-In-The-Loop Features",
      description: "Execute refinement features."
    },
    {
      kind: "export",
      title: "Export",
      description: "Export a Job to a file"
    },
    {
      kind: "display",
      title: "Result Display",
      description: "Inspect the results of previously run jobs."
    },
  ];

  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [jobsError, setJobsError] = useState<string>("");
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const reloadJobs = useCallback(async () => {
    try {
      setJobsError("");
      setJobsLoading(true);

      const res = await fetch("/api/jobs", { method: "GET" });
      const data = await res.json();

      const list: Job[] = Array.isArray(data) ? (data as Job[]) : [];

      setJobs(list);
    } catch {
      setJobsError("Could not load jobs.");
    } finally {
      setJobsLoading(false);
    }
  }, []);

  const onJobUpdate = useCallback((updated: Job) => {
    const id = updated.jobId;
    if (!id) return;

    setJobs((prev) => {
      const idx = prev.findIndex((j) => j.jobId === id);
      if (idx === -1) return prev;
      const copy = [...prev];
      copy[idx] = { ...copy[idx], ...updated };
      return copy;
    });
  }, []);

  const onJobQueued = useCallback(() => {
    void reloadJobs();
  }, [reloadJobs]);

  useEffect(() => {
    void reloadJobs();
  }, [reloadJobs]);

  return (
    <main
      className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white"
      style={{ ["--sidebar-w" as any]: SIDEBAR_W }}
    >
      {/* SIDEBAR */}
      <aside
        className="w-full border-b border-white/10 bg-white/5 backdrop-blur-2xl
                 lg:fixed lg:inset-y-0 lg:left-0 lg:z-40 lg:border-b-0 lg:border-r
                 lg:w-[var(--sidebar-w)]"
      >
        <JobsSidebar
          jobs={jobs}
          loading={jobsLoading}
          error={jobsError}
          onReload={reloadJobs}
          selectedJobId={selectedJobId}
          onSelectJob={setSelectedJobId}
          onJobUpdate={onJobUpdate}
        />
      </aside>

      {/* CONTENT */}
      <section
        className="p-6 lg:ml-[var(--sidebar-w)]
                 lg:min-h-screen lg:border-l lg:border-white/10
                 lg:[box-shadow:inset_3px_0_0_rgba(168,85,247,0.35)]"
      >
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {modules.map((m) => {
            if (m.kind === "standard") {
              return (
                <StandardModuleCard
                  key={m.module}
                  title={m.title}
                  module={m.module}
                  description={m.description}
                  onJobQueued={onJobQueued}
                />
              );
            }
            if (m.kind === "refine") {
              return (
                <RefineModuleCard
                  key={m.title}
                  title={m.title}
                  description={m.description}
                  selectedJobId={selectedJobId}
                  onJobQueued={onJobQueued}
                />
              );
            }
            if (m.kind === "export") {
              return (
                <ExportModuleCard
                  key={m.title}
                  title={m.title}
                  description={m.description}
                  selectedJobId={selectedJobId}
                  jobs={jobs}
                  onJobQueued={onJobQueued}
                />
              );
            }
            return (
              <ResultDisplayCard
                key={m.title}
                title={m.title}
                description={m.description}
                selectedJobId={selectedJobId}
              />
            );
          })}
        </div>
      </section>
    </main>
  );
}
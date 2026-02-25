"use client";

import { useCallback, useEffect, useState } from "react";
import JobsSidebar from "./modules/JobsSidebar";
import ModuleCard from "./modules/ModuleCard";

type Job = {
    job_id: string;
    status: "queued" | "running" | "done" | "failed" | string;
    module?: string | null;
    created_at?: string | null;
    started_at?: string | null;
    finished_at?: string | null;
};

const SIDEBAR_W = "clamp(280px,30vw,420px)";

export default function Home() {
  const modules = [
    {
      title: "Chain-of-Thought",
      module: "cot",
      description: "Send a message to the CoT module.",
    },
    {
      title: "Pipeline Module",
      module: "pipeline",
      description: "Execute a predefined pipeline of tasks.",
    },
  ];

  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [jobsError, setJobsError] = useState<string>("");

  const reloadJobs = useCallback(async () => {
    try {
      setJobsError("");
      setJobsLoading(true);

      const res = await fetch("/api/jobs", { method: "GET" });
      const data = await res.json();

      // supports: { jobs: [...] } or [...]
      const list: Job[] = Array.isArray(data)
        ? data
        : Array.isArray(data?.jobs)
          ? data.jobs
          : [];

      setJobs(list);
    } catch {
      setJobsError("Could not load jobs.");
    } finally {
      setJobsLoading(false);
    }
  }, []);

  // Optional initial load (NOT polling)
  useEffect(() => {
    reloadJobs();
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
        />
      </aside>

      {/* CONTENT (pushed right on lg+ so it never goes under the fixed sidebar) */}
      <section
        className="p-6 lg:ml-[var(--sidebar-w)]
                 lg:min-h-screen lg:border-l lg:border-white/10
                 lg:[box-shadow:inset_3px_0_0_rgba(168,85,247,0.35)]"
      >
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {modules.map((m) => (
            <ModuleCard
              key={m.module}
              title={m.title}
              module={m.module}
              description={m.description}
            />
          ))}
        </div>
      </section>
    </main>
  );
}
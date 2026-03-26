"use client";

import { useCallback, useEffect, useState } from "react";
import type { Job, TutorialStep } from "@/app/types";
import JobsSidebar from "./modules/JobsSidebar";

import DescriptionCard from "./modules/DescriptionCard";
import StandardModuleCard from "./modules/StandardModuleCard";
import ResultDisplayCard from "./modules/ResultModuleCard";
import RefineModuleCard from "./modules/RefineModuleCard"
import ExportModuleCard from "./modules/ExportModuleCard";
import RenderingModuleCard from "./modules/RenderingModuleCard";

type ModuleConfig =
  | { kind: "description"; title: string; description?: string; steps: TutorialStep[]; }
  | { kind: "standard"; title: string; module: string; description?: string }
  | { kind: "refine"; title: string; description?: string; sourceJobLabel?: string }
  | { kind: "export"; title: string; description?: string }
  | { kind: "rendering"; title: string; description?: string }
  | { kind: "result"; title: string; description?: string };

const SIDEBAR_W = "clamp(280px,30vw,420px)";

export default function Home() {
  const modules: ModuleConfig[] = [
    {
      kind: "description",
      title: "Tutorial Display",
      description: "This card gives a short Overview of this web-app.",
      steps: [
        {
          name: "Choose Processing Module",
          description: "Select how your process description should be handled. The Pipeline module applies a structured, predefined sequence of transformations, while the Chain-of-Thought (CoT) module follows a step-by-step reasoning approach to incrementally build the model."
        },
        {
          name: "View the Result",
          description: "After execution, inspect the generated output by selecting a done job from the job overview. You can view the raw structured result  using the Result Display or use the Rendering Module to generate a graphical representation of the model."
        },
        {
          name: "Refine the Model",
          description: "If adjustments are needed, use the Refinement module to modify the generated model. This allows you to iteratively improve structure and semantics by updating or extending the existing result based on additional input. Right now you can rename subjects, messages and states."
        },
        {
          name: "Export the Result",
          description: "Once satisfied, use the Export module to download the generated model. Multiple output formats are available, enabling further use or integration into other tools."
        },
      ],
    },

    {
      kind: "standard",
      title: "Chain-of-Thought Module",
      module: "cot",
      description: "Generate a PASS Model using Chain-of-Thought reasoning.",
    },
    {
      kind: "standard",
      title: "Pipeline Module",
      module: "pipeline",
      description: "Generate a PASS Model using a predefined pipeline of tasks.",
    },
    {
      kind: "result",
      title: "Result Display",
      description: "Inspect the raw results of run jobs."
    },
    {
      kind: "rendering",
      title: "Rendering Module",
      description: "Render a visual representation of the PASS model."
    },
    {
      kind: "refine",
      title: "Refinement Module",
      description: "Execute predefined refinement features. Currently available: Rename Subject, Rename Message, Rename State"
    },
    {
      kind: "export",
      title: "Export Module",
      description: "Export a Job to a choosen file format."
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

      {/* Modules */}
      <section
        className="p-6 lg:ml-[var(--sidebar-w)]
                 lg:min-h-screen lg:border-l lg:border-white/10
                 lg:[box-shadow:inset_3px_0_0_rgba(168,85,247,0.35)]"
      >
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-2">
          {modules.map((m) => {
            if (m.kind === "description") {
              return (
                <div className="sm:col-span-2 lg:col-span-2">
                <DescriptionCard
                  key={m.title}
                  title={m.title}
                  description={m.description}
                  steps={m.steps}
                />
                </div>
              );
            }
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
            if (m.kind === "result") {
              return (
                <ResultDisplayCard
                  key={m.title}
                  title={m.title}
                  description={m.description}
                  selectedJobId={selectedJobId}
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
            if (m.kind === "rendering") {
              return (
                <RenderingModuleCard
                  key={m.title}
                  title={m.title}
                  description={m.description}
                  selectedJobId={selectedJobId}
                  jobs={jobs}
                  onJobQueued={onJobQueued}
                />
              );
            }
            return null;
          })}
        </div>
      </section>
    </main>
  );
}
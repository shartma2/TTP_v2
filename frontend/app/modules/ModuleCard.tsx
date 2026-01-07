"use client";

import { useEffect, useRef, useState } from "react";

type ModuleCardProps = {
  title: string;
  module: string;
  description?: string;
};

export default function ModuleCard({ title, module, description }: ModuleCardProps) {
  const [message, setMessage] = useState<string>("");
  const [output, setOutput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const pollTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  const runModule = async () => {
    if (loading) return;
    // reset previous state
    setOutput("");
    setJobId(null);

    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          module,
          payload: { message },
        }),
      });

      const created = await response.json();
      const jid = created?.jobId as string | undefined;
      if (!jid) {
        throw new Error("Job ID not returned");
      }
      setJobId(jid);
      setOutput("Job queued. Waiting for result...");

      const poll = async () => {
        try {
          const res = await fetch(`http://localhost:8000/jobs/${jid}`);
          const job = await res.json();
          const status = job?.status as string | undefined;

          if (status === "done") {
            const result = job?.result;
            const display =
              result && "response" in result
                ? String((result as any).response)
                : typeof result === "string"
                ? result
                : "No valid response found.";
            setOutput(display);
            setLoading(false);
            return;
          }

          if (status === "failed") {
            setOutput(`Job failed: ${job?.error ?? "Unknown error"}`);
            setLoading(false);
            return;
          }

          // still running or queued, continue polling
          pollTimeout.current = setTimeout(poll, 1000);
        } catch (e) {
          // transient error; back off slightly and continue
          pollTimeout.current = setTimeout(poll, 1500);
        }
      };

      // start polling
      await poll();
    } catch (err) {
      setOutput("Failed to create or poll job.");
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (pollTimeout.current) {
        clearTimeout(pollTimeout.current);
        pollTimeout.current = null;
      }
    };
  }, []);

  return (
    <section className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-8 text-white shadow-2xl shadow-black/50 backdrop-blur-2xl">
      <h2 className="mb-2 text-xl font-semibold tracking-tight">{title}</h2>
      {description && (
        <p className="mb-4 text-sm text-gray-300">{description}</p>
      )}
      <label className="mb-3 block text-sm font-medium text-gray-200" htmlFor={`${module}-input`}>
        Input
      </label>
      <input
        id={`${module}-input`}
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
        className="mb-4 w-full rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-100 outline-none placeholder:text-gray-400 focus:border-purple-400"
      />
      <button
        type="button"
        onClick={runModule}
        disabled={loading}
        className="w-full rounded-2xl bg-white/10 px-6 py-3 text-lg font-medium tracking-wide transition hover:bg-white/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 disabled:opacity-60"
      >
        {loading ? "Running..." : "Run"}
      </button>
      {loading && jobId && (
        <p className="mt-3 text-xs text-gray-400">Job ID: {jobId}</p>
      )}
      <div
        className="mt-6 min-h-[6rem] w-full rounded-2xl border border-white/10 bg-gray-950/60 p-4 text-sm text-gray-200 shadow-inner backdrop-blur-xl"
        aria-live="polite"
      >
        {output || "Output will appear here."}
      </div>
    </section>
  );
}
"use client";

import { useEffect, useRef, useState } from "react";
import { useJobRunner } from "./useJobRunner";
import ModuleCardSpec from "./ModuleCardSpec";

type StandardModuleCardProps = {
  title: string;
  module: string;
  description?: string;
};

export default function StandardModuleCard({ title, module, description }: StandardModuleCardProps) {
  const [message, setMessage] = useState<string>("");
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const { output, loading, jobId, run } = useJobRunner();

  const resizeInput = () => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  };

  useEffect(() => {
    resizeInput();
  }, [message]);

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
      <label className="mb-3 block text-sm font-medium text-gray-200" htmlFor={`${module}-input`}>
        Input
      </label>

      <textarea
        id={`${module}-input`}
        ref={inputRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onInput={resizeInput}
        placeholder="Type your message..."
        rows={1}
        className="mb-4 w-full resize-none overflow-hidden rounded-2xl border border-white/10 bg-gray-950/60 px-4 py-3 text-sm text-gray-100 outline-none placeholder:text-gray-400 focus:border-purple-400"
      />

      <button
        type="button"
        onClick={() => run(module, { message })}
        disabled={loading}
        className="w-full rounded-2xl bg-white/10 px-6 py-3 text-lg font-medium tracking-wide transition hover:bg-white/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 disabled:opacity-60"
      >
        {loading ? "Running..." : "Run"}
      </button>

      {loading && jobId && <p className="mt-3 text-xs text-gray-400">Job ID: {jobId}</p>}
    </ModuleCardSpec>
  );
}
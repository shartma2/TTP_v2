"use client";

import { useState } from "react";

export default function Home() {
  const [output, setOutput] = useState<string>("");

  const handleClick = async (module: string, payload?: Record<string, any>) => {
    const response = await fetch("http://localhost:8000/jobs", {
      method: "POST",
      headers: {
      "Content-Type": "application/json",
      },
      body: JSON.stringify({
      module,
      payload,
      }),
    });
    const data = await response.json();
    setOutput(JSON.stringify(data, null, 2));
    };

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 p-6">
      <section className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-8 text-white shadow-2xl shadow-black/50 backdrop-blur-2xl">
        <h1 className="mb-6 text-center text-2xl font-semibold tracking-tight">
          Your First Home Page
        </h1>
        <button
          type="button"
          onClick={() => handleClick("cot", { message: "This is a test message. Just tell me u received the message and the instructions." })}
          className="w-full rounded-2xl bg-white/10 px-6 py-3 text-lg font-medium tracking-wide transition hover:bg-white/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950"
        >
          Click Here
        </button>
        <div
          className="mt-6 min-h-[6rem] w-full rounded-2xl border border-white/10 bg-gray-950/60 p-4 text-sm text-gray-200 shadow-inner backdrop-blur-xl"
          aria-live="polite"
        >
          {output || "Console output will appear here."}
        </div>
      </section>
    </main>
  );
}

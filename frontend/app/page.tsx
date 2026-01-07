"use client";

import ModuleCard from "./modules/ModuleCard";

export default function Home() {
  const modules = [
    {
      title: "Chain-of-Thought",
      module: "cot",
      description: "Send a message to the CoT module.",
    },
    // Add more modules here as needed
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 p-6">
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
    </main>
  );
}

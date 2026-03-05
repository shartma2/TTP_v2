"use client";

import React from "react";

type ModuleCardSpecProps = {
    title: string;
    description?: string;
    children: React.ReactNode;
    footer?: React.ReactNode;
};

export default function ModuleCardSpec({ title, description, children, footer }: ModuleCardSpecProps) {
    return (
        <section className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-8 text-white shadow-2xl shadow-black/50 backdrop-blur-2xl">
            <h2 className="mb-2 text-xl font-semibold tracking-tight">{title}</h2>
            {description && <p className="mb-4 text-sm text-gray-300">{description}</p>}
            {children}
            {footer && <div className="mt-6">{footer}</div>}
        </section>
    );
}
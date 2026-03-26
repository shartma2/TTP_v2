"use client";

import { useMemo, useState } from "react";
import ModuleCardSpec from "./ModuleCardSpec";
import { TutorialStep } from "../types";


type DescriptionCardProps = {
    title: string;
    description?: string;
    steps: TutorialStep[];
};

export default function DescriptionCard({ title, description, steps }: DescriptionCardProps) {
    const [stepIndex, setStepIndex] = useState(0);

    const safeSteps = useMemo(
        () =>
            steps.length > 0
                ? steps
                : [{ name: "No steps available", description: "There is no tutorial content yet." }],
        [steps]
    );

    const currentStep = safeSteps[stepIndex];
    const isFirstStep = stepIndex === 0;
    const isLastStep = stepIndex === safeSteps.length - 1;

    return (
        <ModuleCardSpec title={title} description={description}>
            <div className="flex flex-col gap-4">
                <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-white/40">
                        Tutorial Step {stepIndex + 1} / {safeSteps.length}
                    </p>
                    <h3 className="mt-1 text-lg font-semibold text-white">
                        {currentStep.name}
                    </h3>
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-inner backdrop-blur-xl">
                    <div className="relative overflow-hidden rounded-xl">
                        <div className="absolute inset-y-0 left-0 w-2 bg-white/10" />
                        <div className="absolute inset-y-0 left-5 w-px bg-white/10" />

                        <div className="pl-8 pr-2">
                            <p className="whitespace-pre-line text-sm leading-7 text-white/80">
                                {currentStep.description}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center justify-between gap-3 pt-2">
                    <button
                        type="button"
                        onClick={() => setStepIndex((prev) => Math.max(prev - 1, 0))}
                        disabled={isFirstStep}
                        className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                        Previous
                    </button>

                    <span className="text-sm text-white/50">
                        {stepIndex + 1} of {safeSteps.length}
                    </span>

                    <button
                        type="button"
                        onClick={() =>
                            setStepIndex((prev) => Math.min(prev + 1, safeSteps.length - 1))
                        }
                        disabled={isLastStep}
                        className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                        Next
                    </button>
                </div>
            </div>
        </ModuleCardSpec>
    );
}
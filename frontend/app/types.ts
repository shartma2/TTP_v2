export type Job = {
    job_id: string;
    status: "queued" | "running" | "done" | "failed" | string;
    module?: string | null;
    created_at?: string | null;
    started_at?: string | null;
    finished_at?: string | null;
};

export type JobUI = {
    jobId: string;
    status: string;
    module?: string;
    createdAt?: string;
    updatedAt?: string;
};


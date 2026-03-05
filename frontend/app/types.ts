export type JobStatus = "queued" | "running" | "done" | "failed" | string;

export type Job = {
    jobId: string;
    status: JobStatus;
    module?: string | null;
    createdAt?: string | null;
    startedAt?: string | null;
    finishedAt?: string | null;
};

export type JobUI = {
    jobId: string;
    status: string;
    module?: string;
    createdAt?: string;
    updatedAt?: string;
};

export type JobResponse = {
    jobId?: string;
    status?: JobStatus;
    module?: string;
    result?: any;
    error?: any;
}


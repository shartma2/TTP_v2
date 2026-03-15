export type JobStatus = "queued" | "running" | "done" | "failed" | string;

export type Job = {
    jobId: string;
    status: JobStatus;
    module?: string | null;

    createdAt?: string | null;
    startedAt?: string | null;

    finishedAt?: string | null;

    result?: any;
    error?: any;
};

export type ExportJobResult = {
  fileName: string;
  contentType: string;
  sizeBytes: number;
  dataBase64: string;
};

export type ExportFormat = ".json" | ".txt" | ".owl";

export type RenderSvgData = {
  sid: string;
  sbd: unknown[];
  [key: string]: unknown;
};

export type RenderJobResult = {
  fileName: string;
  contentType: string;
  sizeBytes: number;
  dataBase64: string;
  svg: RenderSvgData;
};

/*
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
*/

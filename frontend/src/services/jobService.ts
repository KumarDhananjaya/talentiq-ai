import api from "./api";
import type { CreateJobData, Job, JobMatchListResponse } from "../types/job";

export const getJobs = async (): Promise<Job[]> => {
  const response = await api.get<Job[]>("/jobs/");
  return response.data;
};

export const getJob = async (jobId: number): Promise<Job> => {
  const response = await api.get<Job>(`/jobs/${jobId}`);
  return response.data;
};

export const createJob = async (job: CreateJobData): Promise<Job> => {
  const response = await api.post<Job>("/jobs/", job);
  return response.data;
};

export const deleteJob = async (jobId: number): Promise<void> => {
  await api.delete(`/jobs/${jobId}`);
};

export const getJobMatches = async (
  jobId: number,
  minScore = 0,
  limit = 50,
): Promise<JobMatchListResponse> => {
  const response = await api.get<JobMatchListResponse>(
    `/jobs/${jobId}/matches`,
    {
      params: {
        min_score: minScore,
        limit,
      },
    },
  );
  return response.data;
};

export const recalculateJobMatches = async (
  jobId: number,
): Promise<JobMatchListResponse> => {
  const response = await api.post<JobMatchListResponse>(
    `/jobs/${jobId}/matches/recalculate`,
  );
  return response.data;
};
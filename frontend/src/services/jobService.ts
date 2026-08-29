import api from "./api";
import type { Job } from "../types/job";

export const getJobs = async (): Promise<Job[]> => {
  const response = await api.get<Job[]>("/jobs/");
  return response.data;
};

export const getJob = async (
  jobId: number
): Promise<Job> => {
  const response = await api.get<Job>(
    `/jobs/${jobId}`
  );

  return response.data;
};
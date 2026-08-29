import api from "./api";
import type { Candidate } from "../types/candidate";

export interface CreateCandidateData {
  full_name: string;
  email: string;
  phone?: string;
  resume_text?: string;
  skills?: string;
  experience_years?: number;
}

export const getCandidates = async (): Promise<Candidate[]> => {
  const response = await api.get<Candidate[]>("/candidates/");
  return response.data;
};

export const getCandidate = async (
  candidateId: number
): Promise<Candidate> => {
  const response = await api.get<Candidate>(
    `/candidates/${candidateId}`
  );

  return response.data;
};

export const createCandidate = async (
  candidate: CreateCandidateData
): Promise<Candidate> => {
  const response = await api.post<Candidate>(
    "/candidates/",
    candidate
  );

  return response.data;
};

export const uploadCandidateResume = async (
  candidateId: number,
  file: File,
) => {
  const formData = new FormData();

  formData.append("file", file, file.name);

  console.log("FormData file:", formData.get("file"));

  const response = await api.post(
    `/candidates/${candidateId}/resume`,
    formData,
  );

  return response.data;
};
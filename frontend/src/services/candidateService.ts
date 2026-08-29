import api from "./api";
import type { Candidate } from "../types/candidate";

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
export interface Job {
  id: number;
  title: string;
  company: string;
  description: string;
  required_skills?: string | null;
  minimum_experience?: number | null;
  created_at?: string;
}

export interface CreateJobData {
  title: string;
  company: string;
  description: string;
  required_skills?: string;
  minimum_experience?: number;
}

export interface JobMatch {
  candidate_id: number;
  job_id: number;
  candidate_name?: string | null;
  candidate_email?: string | null;
  overall_score: number;
  skill_score: number;
  experience_score: number;
  semantic_score: number;
  matched_skills: string[];
  missing_skills: string[];
  experience_status: string;
  match_level: string;
  explanation: string;
}

export interface JobMatchListResponse {
  job_id: number;
  total_matches: number;
  matches: JobMatch[];
}
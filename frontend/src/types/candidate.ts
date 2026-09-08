export interface CandidateExperience {
  id?: number;
  company?: string | null;
  role?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  is_current?: boolean;
  description?: string | null;
}

export interface Candidate {
  id: number;
  full_name: string;
  email: string;
  phone?: string | null;
  resume_text?: string | null;
  skills?: string[] | string | null;
  experience_years?: number | null;
  experiences?: CandidateExperience[];
  created_at?: string;
}
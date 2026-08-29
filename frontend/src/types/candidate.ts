export interface Candidate {
  id: number;
  full_name: string;
  email: string;
  phone?: string | null;
  resume_text?: string | null;
  skills?: string | null;
  experience_years?: number | null;
  created_at?: string;
}
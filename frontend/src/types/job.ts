export interface Job {
  id: number;
  title: string;
  company: string;
  description: string;
  required_skills?: string | null;
  minimum_experience?: number | null;
  created_at?: string;
}
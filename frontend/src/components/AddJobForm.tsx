import { useState } from "react";
import { createJob } from "../services/jobService";
import type { CreateJobData, Job } from "../types/job";
import { X, Briefcase, Sparkles, Building, Clock, Wrench } from "lucide-react";

interface AddJobFormProps {
  onJobCreated: (job: Job) => void;
  onCancel: () => void;
}

export default function AddJobForm({ onJobCreated, onCancel }: AddJobFormProps) {
  const [form, setForm] = useState<CreateJobData>({
    title: "",
    company: "",
    description: "",
    required_skills: "",
    minimum_experience: undefined,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]:
        name === "minimum_experience"
          ? value === ""
            ? undefined
            : Number(value)
          : value,
    }));
  };

  const handleSubmit = async (event: React.SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!form.title.trim() || !form.company.trim() || !form.description.trim()) {
      setError("Please fill in all required fields (Title, Company, Description).");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const payload: CreateJobData = {
        title: form.title.trim(),
        company: form.company.trim(),
        description: form.description.trim(),
        required_skills: form.required_skills?.trim() || undefined,
        minimum_experience:
          form.minimum_experience !== undefined && !isNaN(form.minimum_experience)
            ? Number(form.minimum_experience)
            : undefined,
      };

      const newJob = await createJob(payload);
      onJobCreated(newJob);
    } catch (err: unknown) {
      console.error(err);
      setError("Failed to create job posting. Please check your inputs and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl sm:p-8">
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gray-900 text-white">
            <Briefcase size={20} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Post a New Job</h2>
            <p className="mt-0.5 text-xs text-gray-500">
              Define the requirements to automatically calculate semantic candidate matches.
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={onCancel}
          aria-label="Close"
          className="rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-900 focus:outline-none"
        >
          <X size={18} />
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-3.5 text-xs text-red-800">
          <p className="font-semibold">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title & Company Grid */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label
              htmlFor="job_title"
              className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-gray-700"
            >
              <Sparkles size={14} className="text-gray-400" />
              Job Title <span className="text-red-500">*</span>
            </label>
            <input
              id="job_title"
              required
              name="title"
              value={form.title}
              onChange={handleChange}
              placeholder="e.g. Senior Backend Engineer"
              className="w-full rounded-xl border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-900 transition focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
            />
          </div>

          <div>
            <label
              htmlFor="job_company"
              className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-gray-700"
            >
              <Building size={14} className="text-gray-400" />
              Company <span className="text-red-500">*</span>
            </label>
            <input
              id="job_company"
              required
              name="company"
              value={form.company}
              onChange={handleChange}
              placeholder="e.g. Acme Tech"
              className="w-full rounded-xl border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-900 transition focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
            />
          </div>
        </div>

        {/* Experience & Skills Grid */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="sm:col-span-1">
            <label
              htmlFor="minimum_experience"
              className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-gray-700"
            >
              <Clock size={14} className="text-gray-400" />
              Min. Experience (Yrs)
            </label>
            <input
              id="minimum_experience"
              type="number"
              min="0"
              step="0.5"
              name="minimum_experience"
              value={form.minimum_experience ?? ""}
              onChange={handleChange}
              placeholder="e.g. 3"
              className="w-full rounded-xl border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-900 transition focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
            />
          </div>

          <div className="sm:col-span-2">
            <label
              htmlFor="required_skills"
              className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-gray-700"
            >
              <Wrench size={14} className="text-gray-400" />
              Required Skills (comma-separated)
            </label>
            <input
              id="required_skills"
              name="required_skills"
              value={form.required_skills}
              onChange={handleChange}
              placeholder="e.g. Python, FastAPI, PostgreSQL, Docker"
              className="w-full rounded-xl border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-900 transition focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
            />
          </div>
        </div>

        {/* Job Description */}
        <div>
          <label
            htmlFor="job_description"
            className="mb-1.5 block text-xs font-semibold text-gray-700"
          >
            Job Description & Responsibilities <span className="text-red-500">*</span>
          </label>
          <textarea
            id="job_description"
            required
            rows={5}
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="Paste or write the key responsibilities, qualifications, and role summary..."
            className="w-full rounded-xl border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-900 transition focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
          />
        </div>

        {/* Actions */}
        <div className="mt-6 flex flex-col-reverse justify-end gap-3 pt-4 border-t border-gray-100 sm:flex-row">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-xs font-semibold text-gray-700 transition hover:bg-gray-50 focus:outline-none disabled:opacity-50 sm:w-auto"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gray-900 px-5 py-2.5 text-xs font-semibold text-white transition hover:bg-gray-800 focus:outline-none disabled:opacity-70 sm:w-auto shadow-sm"
          >
            {loading ? (
              <>
                <svg
                  className="h-3.5 w-3.5 animate-spin text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Creating Job & Embedding...
              </>
            ) : (
              "Publish Job"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

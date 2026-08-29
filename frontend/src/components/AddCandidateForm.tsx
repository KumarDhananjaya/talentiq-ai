import { useState } from "react";
import { createCandidate } from "../services/candidateService";
import type { CreateCandidateData } from "../services/candidateService";

interface AddCandidateFormProps {
  onCandidateCreated: () => void;
  onCancel: () => void;
}

export default function AddCandidateForm({
  onCandidateCreated,
  onCancel,
}: AddCandidateFormProps) {
  const [form, setForm] = useState<CreateCandidateData>({
    full_name: "",
    email: "",
    phone: "",
    resume_text: "",
    skills: "",
    experience_years: undefined,
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
        name === "experience_years"
          ? value === ""
            ? undefined
            : Number(value)
          : value,
    }));
  };

  const handleSubmit = async (event: React.SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");
      await createCandidate(form);
      onCandidateCreated();
    } catch (err) {
      console.error(err);
      setError("Failed to create candidate. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-3xl rounded-2xl border border-gray-200 bg-white p-6 shadow-xl sm:p-8">
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Add Candidate</h2>
          <p className="mt-1.5 text-sm text-gray-500">
            Add a new candidate to the TalentIQ talent pool.
          </p>
        </div>
        <button
          type="button"
          onClick={onCancel}
          aria-label="Close"
          className="rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mb-6 flex items-center gap-3 rounded-xl bg-red-50 p-4 text-sm text-red-800 border border-red-100">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-red-500 shrink-0"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" x2="12" y1="8" y2="12" />
            <line x1="12" x2="12.01" y1="16" y2="16" />
          </svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6 flex flex-col h-full">
        {/* Form Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {/* Full Name */}
          <div>
            <label
              htmlFor="full_name"
              className="mb-1.5 block text-sm font-semibold text-gray-700"
            >
              Full Name <span className="text-red-500">*</span>
            </label>
            <input
              id="full_name"
              required
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
              placeholder="Alex Johnson"
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 transition-all placeholder:text-gray-400 focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
            />
          </div>

          {/* Email */}
          <div>
            <label
              htmlFor="email"
              className="mb-1.5 block text-sm font-semibold text-gray-700"
            >
              Email <span className="text-red-500">*</span>
            </label>
            <input
              id="email"
              required
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="alex@example.com"
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 transition-all placeholder:text-gray-400 focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
            />
          </div>

          {/* Phone */}
          <div>
            <div className="mb-1.5 flex justify-between items-baseline">
              <label
                htmlFor="phone"
                className="block text-sm font-semibold text-gray-700"
              >
                Phone
              </label>
              <span className="text-xs text-gray-400">Optional</span>
            </div>
            <input
              id="phone"
              type="tel"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              placeholder="+61 412 345 678"
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 transition-all placeholder:text-gray-400 focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
            />
          </div>

          {/* Experience */}
          <div>
            <div className="mb-1.5 flex justify-between items-baseline">
              <label
                htmlFor="experience_years"
                className="block text-sm font-semibold text-gray-700"
              >
                Experience (years)
              </label>
              <span className="text-xs text-gray-400">Optional</span>
            </div>
            <input
              id="experience_years"
              type="number"
              min="0"
              name="experience_years"
              value={form.experience_years ?? ""}
              onChange={handleChange}
              placeholder="e.g. 3"
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 transition-all placeholder:text-gray-400 focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
            />
          </div>
        </div>

        {/* Skills */}
        <div>
          <div className="mb-1.5 flex justify-between items-baseline">
            <label
              htmlFor="skills"
              className="block text-sm font-semibold text-gray-700"
            >
              Skills
            </label>
            <span className="text-xs text-gray-400">Optional</span>
          </div>
          <input
            id="skills"
            name="skills"
            value={form.skills}
            onChange={handleChange}
            placeholder="Python, FastAPI, Machine Learning..."
            className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 transition-all placeholder:text-gray-400 focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
          />
        </div>

        {/* Resume */}
        <div>
          <div className="mb-1.5 flex justify-between items-baseline">
            <label
              htmlFor="resume_text"
              className="block text-sm font-semibold text-gray-700"
            >
              Resume Text
            </label>
            <span className="text-xs text-gray-400">Optional</span>
          </div>
          <textarea
            id="resume_text"
            name="resume_text"
            value={form.resume_text}
            onChange={handleChange}
            rows={5}
            placeholder="Paste the candidate's resume or cover letter here..."
            className="w-full resize-y rounded-xl border border-gray-300 bg-white px-4 py-3 text-sm text-gray-900 transition-all placeholder:text-gray-400 focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900"
          />
        </div>

        {/* Actions */}
        <div className="mt-4 flex flex-col-reverse justify-end gap-3 sm:flex-row pt-4 border-t border-gray-100">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="w-full rounded-xl border border-gray-300 bg-white px-5 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 disabled:opacity-50 sm:w-auto"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gray-900 px-5 py-2.5 text-sm font-semibold text-white transition-all hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70 sm:w-auto"
          >
            {loading ? (
              <>
                <svg
                  className="h-4 w-4 animate-spin text-white"
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
                Creating...
              </>
            ) : (
              "Create Candidate"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

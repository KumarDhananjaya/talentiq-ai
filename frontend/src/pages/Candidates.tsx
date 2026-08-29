import { useEffect, useMemo, useState } from "react";
import { getCandidates } from "../services/candidateService";
import type { Candidate } from "../types/candidate";
import AddCandidateForm from "../components/AddCandidateForm";

function Candidates() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    const loadCandidates = async () => {
      try {
        setLoading(true);
        setError("");

        const data = await getCandidates();

        setCandidates(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load candidates.");
      } finally {
        setLoading(false);
      }
    };

    loadCandidates();
  }, []);

  const filteredCandidates = useMemo(() => {
    const searchTerm = search.toLowerCase().trim();

    if (!searchTerm) {
      return candidates;
    }

    return candidates.filter((candidate) => {
      const name = candidate.full_name?.toLowerCase() ?? "";
      const email = candidate.email?.toLowerCase() ?? "";
      const skills = candidate.skills?.toLowerCase() ?? "";

      return (
        name.includes(searchTerm) ||
        email.includes(searchTerm) ||
        skills.includes(searchTerm)
      );
    });
  }, [candidates, search]);

  const totalCandidates = candidates.length;

  const averageExperience =
    totalCandidates > 0
      ? candidates.reduce(
          (sum, candidate) => sum + (candidate.experience_years ?? 0),
          0,
        ) / totalCandidates
      : 0;

  const candidatesWithSkills = candidates.filter(
    (candidate) => candidate.skills && candidate.skills.trim().length > 0,
  ).length;

  if (loading) {
    return (
      <div>
        <h1 className="text-3xl font-bold">Candidates</h1>

        <p className="mt-4 text-gray-500">Loading candidates...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1 className="text-3xl font-bold">Candidates</h1>

        <p className="mt-4 text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Candidates</h1>
          <p className="mt-2 text-gray-600">
            Manage and analyze your talent pool.
          </p>
           
        </div>

        <button
          type="button"
          onClick={() => setShowAddForm(true)}
          className="rounded-lg bg-black px-4 py-2 font-medium text-white transition hover:bg-gray-800"
        >
          + Add Candidate
        </button>
        {showAddForm && (
          <AddCandidateForm
            onCandidateCreated={() => {
              setShowAddForm(false);
              window.location.reload();
            }}
            onCancel={() => setShowAddForm(false)}
          />
        )}
      </div>

      {/* Statistics */}

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">Total Candidates</p>

          <p className="mt-2 text-3xl font-bold">{totalCandidates}</p>
        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Average Experience
          </p>

          <p className="mt-2 text-3xl font-bold">
            {averageExperience.toFixed(1)} years
          </p>
        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Candidates With Skills
          </p>

          <p className="mt-2 text-3xl font-bold">{candidatesWithSkills}</p>
        </div>
      </div>

      {/* Search */}

      <div className="rounded-xl border bg-white p-4 shadow-sm">
        <input
          type="text"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search by name, email or skills..."
          className="w-full rounded-lg border px-4 py-3 outline-none transition focus:border-black"
        />
      </div>

      {/* Candidate table */}

      <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold">
                  Candidate
                </th>

                <th className="px-6 py-4 text-left text-sm font-semibold">
                  Email
                </th>

                <th className="px-6 py-4 text-left text-sm font-semibold">
                  Skills
                </th>

                <th className="px-6 py-4 text-left text-sm font-semibold">
                  Experience
                </th>
              </tr>
            </thead>

            <tbody>
              {filteredCandidates.length === 0 ? (
                <tr>
                  <td
                    colSpan={4}
                    className="px-6 py-10 text-center text-gray-500"
                  >
                    {search
                      ? "No candidates match your search."
                      : "No candidates found."}
                  </td>
                </tr>
              ) : (
                filteredCandidates.map((candidate) => (
                  <tr
                    key={candidate.id}
                    className="border-b transition hover:bg-gray-50 last:border-b-0"
                  >
                    <td className="px-6 py-4">
                      <div className="font-medium">{candidate.full_name}</div>

                      {candidate.phone && (
                        <div className="mt-1 text-sm text-gray-500">
                          {candidate.phone}
                        </div>
                      )}
                    </td>

                    <td className="px-6 py-4 text-gray-600">
                      {candidate.email}
                    </td>

                    <td className="px-6 py-4">
                      {candidate.skills ? (
                        <span className="rounded-full bg-gray-100 px-3 py-1 text-sm">
                          {candidate.skills}
                        </span>
                      ) : (
                        <span className="text-gray-400">Not specified</span>
                      )}
                    </td>

                    <td className="px-6 py-4 text-gray-600">
                      {candidate.experience_years ?? 0} years
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Candidates;

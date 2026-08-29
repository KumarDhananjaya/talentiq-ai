import { useEffect, useState } from "react";
import { getCandidates } from "../services/candidateService";
import type { Candidate } from "../types/candidate";

function Candidates() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadCandidates = async () => {
      try {
        setLoading(true);

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

  if (loading) {
    return (
      <div>
        <h1 className="text-3xl font-bold">Candidates</h1>

        <p className="mt-4 text-gray-500">
          Loading candidates...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1 className="text-3xl font-bold">Candidates</h1>

        <p className="mt-4 text-red-500">
          {error}
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Candidates
          </h1>

          <p className="mt-2 text-gray-600">
            Manage and analyze candidates.
          </p>
        </div>

        <button className="rounded-lg bg-black px-4 py-2 text-white">
          + Add Candidate
        </button>
      </div>

      <div className="mt-8 overflow-hidden rounded-lg border bg-white">
        <table className="w-full">
          <thead className="border-b bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold">
                Name
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
            {candidates.length === 0 ? (
              <tr>
                <td
                  colSpan={4}
                  className="px-6 py-8 text-center text-gray-500"
                >
                  No candidates found.
                </td>
              </tr>
            ) : (
              candidates.map((candidate) => (
                <tr
                  key={candidate.id}
                  className="border-b last:border-b-0"
                >
                  <td className="px-6 py-4 font-medium">
                    {candidate.full_name}
                  </td>

                  <td className="px-6 py-4 text-gray-600">
                    {candidate.email}
                  </td>

                  <td className="px-6 py-4 text-gray-600">
                    {candidate.skills || "Not specified"}
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
  );
}

export default Candidates;
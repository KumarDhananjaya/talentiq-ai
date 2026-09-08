import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getCandidates } from "../services/candidateService";
import type { Candidate } from "../types/candidate";
import AddCandidateForm from "../components/AddCandidateForm";
import {
  Users,
  Search,
  Plus,
  Briefcase,
  Mail,
  Phone,
  Calendar,
  FileText,
  X,
  ExternalLink,
  Sparkles,
  Layers,
  Award,
} from "lucide-react";

export default function Candidates() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  const loadData = async () => {
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

  useEffect(() => {
    loadData();
  }, []);

  const getSkillsArray = (skills: string[] | string | null | undefined): string[] => {
    if (!skills) return [];
    if (Array.isArray(skills)) {
      return skills.flatMap((s) => (typeof s === "string" ? s.split(",") : String(s))).map((s) => s.trim()).filter(Boolean);
    }
    return String(skills).split(",").map((s) => s.trim()).filter(Boolean);
  };

  const filteredCandidates = useMemo(() => {
    const searchTerm = search.toLowerCase().trim();
    if (!searchTerm) return candidates;

    return candidates.filter((candidate) => {
      const name = candidate.full_name?.toLowerCase() ?? "";
      const email = candidate.email?.toLowerCase() ?? "";
      const skillsStr = getSkillsArray(candidate.skills).join(" ").toLowerCase();

      return name.includes(searchTerm) || email.includes(searchTerm) || skillsStr.includes(searchTerm);
    });
  }, [candidates, search]);

  const totalCandidates = candidates.length;

  const averageExperience =
    totalCandidates > 0
      ? candidates.reduce((sum, candidate) => sum + (candidate.experience_years ?? 0), 0) / totalCandidates
      : 0;

  const candidatesWithSkills = candidates.filter(
    (candidate) => getSkillsArray(candidate.skills).length > 0
  ).length;

  const getSeniorityBadge = (years: number | null | undefined) => {
    const exp = years ?? 0;
    if (exp >= 5) {
      return (
        <span className="rounded-full bg-purple-50 border border-purple-200 px-2 py-0.5 text-[11px] font-semibold text-purple-700">
          Senior ({exp} yrs)
        </span>
      );
    }
    if (exp >= 2) {
      return (
        <span className="rounded-full bg-blue-50 border border-blue-200 px-2 py-0.5 text-[11px] font-semibold text-blue-700">
          Mid-Level ({exp} yrs)
        </span>
      );
    }
    return (
      <span className="rounded-full bg-emerald-50 border border-emerald-200 px-2 py-0.5 text-[11px] font-semibold text-emerald-700">
        Junior / Grad ({exp} yrs)
      </span>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Talent Pool</h1>
          <p className="mt-1 text-sm text-gray-500">
            Search, evaluate, and inspect candidate profiles with AI entity extraction.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowAddForm(true)}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-gray-800"
        >
          <Plus size={18} />
          Add Candidate
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Candidates</span>
            <Users size={18} className="text-gray-400" />
          </div>
          <p className="mt-3 text-3xl font-black text-gray-900">{totalCandidates}</p>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Average Experience</span>
            <Calendar size={18} className="text-gray-400" />
          </div>
          <p className="mt-3 text-3xl font-black text-gray-900">{averageExperience.toFixed(1)} <span className="text-base font-medium text-gray-500">years</span></p>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between text-gray-500">
            <span className="text-xs font-semibold uppercase tracking-wider">With AI Extracted Skills</span>
            <Sparkles size={18} className="text-amber-500" />
          </div>
          <p className="mt-3 text-3xl font-black text-gray-900">{candidatesWithSkills} <span className="text-xs text-gray-400 font-normal">/ {totalCandidates} profiles</span></p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="rounded-2xl border border-gray-200 bg-white p-3 shadow-xs">
        <div className="relative">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search candidates by name, email, or skill keywords (e.g., Python, Docker, NLP)..."
            className="w-full rounded-xl border border-gray-200 bg-gray-50/50 pl-10 pr-4 py-2.5 text-xs sm:text-sm text-gray-900 transition focus:border-gray-900 focus:bg-white focus:outline-none"
          />
        </div>
      </div>

      {/* Candidate Table / Cards */}
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="border-b border-gray-200 bg-gray-50/80 text-[11px] font-bold uppercase tracking-wider text-gray-500">
              <tr>
                <th className="px-6 py-3.5">Candidate Profile</th>
                <th className="px-6 py-3.5">Contact Details</th>
                <th className="px-6 py-3.5">Key Skills</th>
                <th className="px-6 py-3.5">Experience Tier</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-xs text-gray-400">
                    Loading candidate records...
                  </td>
                </tr>
              ) : filteredCandidates.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                    <Users className="mx-auto h-8 w-8 text-gray-300 mb-2" />
                    <p className="font-semibold text-gray-700">No candidates match your search.</p>
                    <p className="text-xs text-gray-400 mt-0.5">Try a different keyword or create a candidate.</p>
                  </td>
                </tr>
              ) : (
                filteredCandidates.map((candidate) => {
                  const skills = getSkillsArray(candidate.skills);
                  return (
                    <tr
                      key={candidate.id}
                      onClick={() => setSelectedCandidate(candidate)}
                      className="group cursor-pointer transition hover:bg-gray-50/80"
                    >
                      <td className="px-6 py-4">
                        <div className="font-bold text-gray-900">{candidate.full_name}</div>
                        <div className="text-[11px] text-gray-400">ID #{candidate.id}</div>
                      </td>

                      <td className="px-6 py-4 text-gray-600">
                        <div className="flex items-center gap-1.5 text-xs">
                          <Mail size={12} className="text-gray-400 shrink-0" />
                          <span className="truncate max-w-44">{candidate.email}</span>
                        </div>
                        {candidate.phone && (
                          <div className="flex items-center gap-1.5 text-[11px] text-gray-400 mt-1">
                            <Phone size={11} className="text-gray-400 shrink-0" />
                            <span>{candidate.phone}</span>
                          </div>
                        )}
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {skills.slice(0, 3).map((skill) => (
                            <span
                              key={skill}
                              className="rounded-md bg-gray-100 border border-gray-200 px-2 py-0.5 text-[11px] font-medium text-gray-700"
                            >
                              {skill}
                            </span>
                          ))}
                          {skills.length > 3 && (
                            <span className="rounded-md bg-gray-50 px-1.5 py-0.5 text-[10px] font-semibold text-gray-400 border border-gray-200">
                              +{skills.length - 3}
                            </span>
                          )}
                          {skills.length === 0 && (
                            <span className="text-xs text-gray-400 italic">None extracted</span>
                          )}
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        {getSeniorityBadge(candidate.experience_years)}
                      </td>

                      <td className="px-6 py-4 text-right">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedCandidate(candidate);
                          }}
                          className="inline-flex items-center gap-1 rounded-lg border border-gray-200 bg-white px-2.5 py-1 text-xs font-semibold text-gray-700 shadow-2xs hover:bg-gray-50"
                        >
                          View Resume
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Candidate Profile Drawer / Modal */}
      {selectedCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-3xl bg-white p-6 sm:p-8 shadow-2xl border border-gray-200">
            <button
              onClick={() => setSelectedCandidate(null)}
              className="absolute right-5 top-5 rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-700"
            >
              <X size={18} />
            </button>

            <div className="flex items-start gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-900 text-xl font-bold text-white shrink-0">
                {selectedCandidate.full_name?.charAt(0) || "C"}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900">{selectedCandidate.full_name}</h3>
                <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 mt-1">
                  <span className="flex items-center gap-1"><Mail size={13} /> {selectedCandidate.email}</span>
                  {selectedCandidate.phone && (
                    <span className="flex items-center gap-1"><Phone size={13} /> {selectedCandidate.phone}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Experience & Skills Section */}
            <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-gray-100 bg-gray-50/70 p-4">
                <span className="text-[11px] font-bold uppercase tracking-wider text-gray-500">
                  Total Experience
                </span>
                <p className="mt-1 text-lg font-bold text-gray-900">
                  {selectedCandidate.experience_years ?? 0} Years
                </p>
              </div>

              <div className="rounded-2xl border border-gray-100 bg-gray-50/70 p-4">
                <span className="text-[11px] font-bold uppercase tracking-wider text-gray-500">
                  Semantic Embedding
                </span>
                <p className="mt-1 text-sm font-semibold text-emerald-700 flex items-center gap-1">
                  <Sparkles size={14} /> 384-d Vectorized
                </p>
              </div>
            </div>

            {/* Skills */}
            <div className="mt-6">
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                Technical Competencies
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {getSkillsArray(selectedCandidate.skills).map((skill) => (
                  <span
                    key={skill}
                    className="rounded-lg bg-gray-900 text-white px-2.5 py-1 text-xs font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Parsed Resume Text */}
            <div className="mt-6">
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2 flex items-center gap-1.5">
                <FileText size={14} /> Parsed Resume Content
              </h4>
              <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4 text-xs font-mono text-gray-700 leading-relaxed max-h-56 overflow-y-auto whitespace-pre-wrap">
                {selectedCandidate.resume_text || "No resume content available."}
              </div>
            </div>

            {/* Footer Action */}
            <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-gray-100">
              <Link
                to="/jobs"
                onClick={() => setSelectedCandidate(null)}
                className="inline-flex items-center gap-1.5 rounded-xl bg-gray-900 px-4 py-2.5 text-xs font-bold text-white hover:bg-gray-800"
              >
                <Briefcase size={14} /> Match Against Open Roles <ExternalLink size={13} />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Add Candidate Form Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative max-h-[90vh] overflow-y-auto rounded-2xl">
            <AddCandidateForm
              onCandidateCreated={() => {
                setShowAddForm(false);
                loadData();
              }}
              onCancel={() => setShowAddForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}


import { useEffect, useState, useMemo } from "react";
import {
  getJobs,
  getJobMatches,
  recalculateJobMatches,
  deleteJob,
} from "../services/jobService";
import type { Job, JobMatch } from "../types/job";
import AddJobForm from "../components/AddJobForm";
import {
  Briefcase,
  Plus,
  RefreshCw,
  Sparkles,
  Building2,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Search,
  Filter,
  Trash2,
  Layers,
  Award,
  TrendingUp,
} from "lucide-react";

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [recalculating, setRecalculating] = useState(false);
  const [error, setError] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [minScoreFilter, setMinScoreFilter] = useState<number>(0);

  const loadMatches = async (jobId: number) => {
    try {
      setLoadingMatches(true);
      setError("");
      const response = await getJobMatches(jobId);
      setMatches(response.matches || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load candidate matches for this job.");
    } finally {
      setLoadingMatches(false);
    }
  };

  const loadJobs = async (selectJobId?: number) => {
    try {
      setLoadingJobs(true);
      setError("");
      const data = await getJobs();
      setJobs(data);

      if (data.length > 0) {
        const target = selectJobId ? data.find((j) => j.id === selectJobId) || data[0] : data[0];
        setSelectedJob(target);
        await loadMatches(target.id);
      } else {
        setSelectedJob(null);
        setMatches([]);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to load jobs list.");
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    async function init() {
      try {
        setLoadingJobs(true);
        setError("");
        const data = await getJobs();
        if (!isMounted) return;
        setJobs(data);

        if (data.length > 0) {
          const firstJob = data[0];
          setSelectedJob(firstJob);
          setLoadingMatches(true);
          const matchRes = await getJobMatches(firstJob.id);
          if (!isMounted) return;
          setMatches(matchRes.matches || []);
        }
      } catch (err) {
        if (!isMounted) return;
        console.error(err);
        setError("Failed to load jobs list.");
      } finally {
        if (isMounted) {
          setLoadingJobs(false);
          setLoadingMatches(false);
        }
      }
    }

    init();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
    loadMatches(job.id);
  };

  const handleRecalculate = async () => {
    if (!selectedJob) return;
    try {
      setRecalculating(true);
      setError("");
      const response = await recalculateJobMatches(selectedJob.id);
      setMatches(response.matches || []);
    } catch (err) {
      console.error(err);
      setError("Failed to recalculate candidate matches.");
    } finally {
      setRecalculating(false);
    }
  };

  const handleDeleteJob = async (jobId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this job posting?")) {
      return;
    }
    try {
      await deleteJob(jobId);
      const remaining = jobs.filter((j) => j.id !== jobId);
      setJobs(remaining);
      if (selectedJob?.id === jobId) {
        setSelectedJob(remaining.length > 0 ? remaining[0] : null);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to delete job.");
    }
  };

  // Filter matches based on candidate search & minimum score filter
  const filteredMatches = useMemo(() => {
    return matches.filter((match) => {
      const matchScore = match.overall_score >= minScoreFilter;
      const searchLower = searchFilter.toLowerCase().trim();
      if (!searchLower) return matchScore;

      const name = match.candidate_name?.toLowerCase() ?? "";
      const email = match.candidate_email?.toLowerCase() ?? "";
      const skills = (match.matched_skills || []).concat(match.missing_skills || []).join(" ").toLowerCase();

      return matchScore && (name.includes(searchLower) || email.includes(searchLower) || skills.includes(searchLower));
    });
  }, [matches, minScoreFilter, searchFilter]);

  // Match Level Badge Helper
  const getMatchLevelBadge = (level: string, score: number) => {
    if (score >= 85 || level.toLowerCase().includes("excellent")) {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 border border-emerald-200">
          <Sparkles size={12} /> Excellent Match
        </span>
      );
    }
    if (score >= 70 || level.toLowerCase().includes("strong")) {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700 border border-blue-200">
          <TrendingUp size={12} /> Strong Match
        </span>
      );
    }
    if (score >= 50 || level.toLowerCase().includes("moderate")) {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700 border border-amber-200">
          <Clock size={12} /> Moderate Match
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-semibold text-rose-700 border border-rose-200">
        <AlertCircle size={12} /> Weak Match
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header & Quick Action */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Job Postings & AI Matching</h1>
          <p className="mt-1 text-sm text-gray-500">
            Define requirements and view explainable multi-factor candidate match rankings.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowAddForm(true)}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
        >
          <Plus size={18} />
          Post New Job
        </button>
      </div>

      {/* Global Error Banner */}
      {error && (
        <div className="flex items-center justify-between rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <div className="flex items-center gap-2">
            <AlertCircle size={18} className="shrink-0 text-red-600" />
            <span>{error}</span>
          </div>
          <button
            onClick={() => {
              setError("");
              loadJobs();
            }}
            className="text-xs font-semibold underline hover:text-red-900"
          >
            Retry
          </button>
        </div>
      )}

      {/* Main Layout Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left Column: Jobs List (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-500">
              Open Positions ({jobs.length})
            </h2>
          </div>

          {loadingJobs ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse rounded-xl border border-gray-200 bg-white p-4 space-y-2">
                  <div className="h-4 w-2/3 bg-gray-200 rounded" />
                  <div className="h-3 w-1/2 bg-gray-100 rounded" />
                  <div className="h-3 w-3/4 bg-gray-100 rounded" />
                </div>
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className="rounded-2xl border-2 border-dashed border-gray-200 bg-white p-8 text-center">
              <Briefcase className="mx-auto h-10 w-10 text-gray-400" />
              <h3 className="mt-2 text-sm font-bold text-gray-900">No job postings</h3>
              <p className="mt-1 text-xs text-gray-500">Post your first job to begin calculating candidate matches.</p>
              <button
                type="button"
                onClick={() => setShowAddForm(true)}
                className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-gray-900 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-gray-800"
              >
                <Plus size={14} /> Create Job
              </button>
            </div>
          ) : (
            <div className="space-y-2.5 max-h-[75vh] overflow-y-auto pr-1">
              {jobs.map((job) => {
                const isSelected = selectedJob?.id === job.id;
                const skillsArray = job.required_skills
                  ? job.required_skills.split(",").map((s) => s.trim()).filter(Boolean)
                  : [];

                return (
                  <div
                    key={job.id}
                    onClick={() => handleSelectJob(job)}
                    className={`group relative cursor-pointer rounded-xl border p-4 transition-all ${
                      isSelected
                        ? "border-gray-900 bg-white shadow-md ring-1 ring-gray-900"
                        : "border-gray-200 bg-white hover:border-gray-300 hover:shadow-xs"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-gray-900 truncate text-sm sm:text-base">{job.title}</h3>
                        <p className="flex items-center gap-1.5 text-xs font-medium text-gray-500 mt-0.5">
                          <Building2 size={13} className="shrink-0 text-gray-400" />
                          <span className="truncate">{job.company}</span>
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={(e) => handleDeleteJob(job.id, e)}
                        title="Delete Job"
                        className="opacity-0 group-hover:opacity-100 rounded-md p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600 transition"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>

                    {/* Requirements Tags */}
                    <div className="mt-3 flex flex-wrap items-center gap-1.5">
                      {job.minimum_experience !== null && job.minimum_experience !== undefined && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2 py-0.5 text-[11px] font-medium text-gray-700">
                          <Clock size={11} /> {job.minimum_experience}+ yrs
                        </span>
                      )}
                      {skillsArray.slice(0, 3).map((skill) => (
                        <span
                          key={skill}
                          className="rounded-md bg-gray-50 px-2 py-0.5 text-[11px] font-medium text-gray-600 border border-gray-200"
                        >
                          {skill}
                        </span>
                      ))}
                      {skillsArray.length > 3 && (
                        <span className="text-[10px] text-gray-400 font-medium">+{skillsArray.length - 3} more</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Selected Job Details & Candidate Matches (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          {selectedJob ? (
            <>
              {/* Selected Job Header Card */}
              <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center rounded-md bg-gray-100 px-2.5 py-0.5 text-xs font-semibold text-gray-800">
                        Job #{selectedJob.id}
                      </span>
                      <h2 className="text-xl font-bold text-gray-900">{selectedJob.title}</h2>
                    </div>
                    <p className="mt-1 text-sm text-gray-600 font-medium flex items-center gap-2">
                      <span>{selectedJob.company}</span>
                      {selectedJob.minimum_experience !== null && selectedJob.minimum_experience !== undefined && (
                        <>
                          <span className="text-gray-300">•</span>
                          <span>Min. {selectedJob.minimum_experience} yrs experience</span>
                        </>
                      )}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={handleRecalculate}
                    disabled={recalculating}
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-300 bg-white px-3.5 py-2 text-xs font-semibold text-gray-700 shadow-xs transition hover:bg-gray-50 focus:outline-none disabled:opacity-50"
                  >
                    <RefreshCw size={14} className={recalculating ? "animate-spin text-gray-900" : ""} />
                    {recalculating ? "Calculating AI Matches..." : "Recalculate Matches"}
                  </button>
                </div>

                {/* Job Description Dropdown / Collapsible */}
                <div className="mt-4 pt-4 border-t border-gray-100 text-xs text-gray-600 leading-relaxed">
                  <p className="font-semibold text-gray-700 mb-1">Role Description:</p>
                  <p className="whitespace-pre-line line-clamp-3 hover:line-clamp-none transition-all">
                    {selectedJob.description}
                  </p>
                </div>

                {/* Required Skills Chips */}
                {selectedJob.required_skills && (
                  <div className="mt-3 flex flex-wrap items-center gap-1.5">
                    <span className="text-xs font-semibold text-gray-700 mr-1">Target Skills:</span>
                    {selectedJob.required_skills.split(",").map((s) => s.trim()).filter(Boolean).map((skill) => (
                      <span
                        key={skill}
                        className="rounded-full bg-gray-900 text-white px-2.5 py-0.5 text-xs font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Match Filter & Search Toolbar */}
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between rounded-xl border border-gray-200 bg-white p-3.5 shadow-xs">
                {/* Search candidate name/skill */}
                <div className="relative flex-1">
                  <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    placeholder="Filter candidate matches by name or skill..."
                    className="w-full rounded-lg border border-gray-200 pl-9 pr-3 py-1.5 text-xs text-gray-900 transition focus:border-gray-900 focus:outline-none"
                  />
                </div>

                {/* Min Score Filter */}
                <div className="flex items-center gap-2 shrink-0">
                  <Filter size={14} className="text-gray-400" />
                  <span className="text-xs font-medium text-gray-600">Min Fit:</span>
                  <select
                    value={minScoreFilter}
                    onChange={(e) => setMinScoreFilter(Number(e.target.value))}
                    aria-label="Filter candidates by minimum match score"
                    className="rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 transition focus:border-gray-900 focus:outline-none"
                  >
                    <option value={0}>All Matches (0%+)</option>
                    <option value={50}>Moderate+ (50%+)</option>
                    <option value={70}>Strong+ (70%+)</option>
                    <option value={85}>Excellent Only (85%+)</option>
                  </select>
                </div>
              </div>

              {/* Candidate Matches Section */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-700 flex items-center gap-2">
                    <Award size={16} className="text-gray-900" />
                    Ranked Candidate Matches ({filteredMatches.length})
                  </h3>
                  <span className="text-xs text-gray-400">
                    Weighted: 40% Skills • 20% Experience • 40% Semantic
                  </span>
                </div>

                {loadingMatches ? (
                  <div className="space-y-4">
                    {[1, 2].map((i) => (
                      <div key={i} className="animate-pulse rounded-2xl border border-gray-200 bg-white p-6 space-y-4">
                        <div className="flex justify-between items-center">
                          <div className="h-5 w-1/3 bg-gray-200 rounded" />
                          <div className="h-8 w-16 bg-gray-200 rounded-full" />
                        </div>
                        <div className="grid grid-cols-3 gap-3">
                          <div className="h-16 bg-gray-100 rounded-xl" />
                          <div className="h-16 bg-gray-100 rounded-xl" />
                          <div className="h-16 bg-gray-100 rounded-xl" />
                        </div>
                        <div className="h-12 bg-gray-100 rounded-xl" />
                      </div>
                    ))}
                  </div>
                ) : filteredMatches.length === 0 ? (
                  <div className="rounded-2xl border-2 border-dashed border-gray-200 bg-white p-12 text-center">
                    <Layers className="mx-auto h-12 w-12 text-gray-300" />
                    <h4 className="mt-3 text-sm font-bold text-gray-900">No candidates match the filter criteria</h4>
                    <p className="mt-1 text-xs text-gray-500 max-w-sm mx-auto">
                      {matches.length === 0
                        ? "No matches calculated yet. Click 'Recalculate Matches' to evaluate the talent pool against this role."
                        : "Try lowering the minimum fit filter or clearing the search keyword."}
                    </p>
                    {matches.length === 0 && (
                      <button
                        type="button"
                        onClick={handleRecalculate}
                        disabled={recalculating}
                        className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-gray-900 px-3.5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-gray-800"
                      >
                        <RefreshCw size={13} /> Calculate AI Matches Now
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {filteredMatches.map((match, index) => {
                      const candidateDisplayName =
                        match.candidate_name || `Candidate #${match.candidate_id}`;

                      return (
                        <div
                          key={match.candidate_id}
                          className="rounded-2xl border border-gray-200 bg-white p-5 sm:p-6 shadow-xs transition hover:shadow-md hover:border-gray-300"
                        >
                          {/* Match Top Bar: Rank, Candidate Name, Overall Score */}
                          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                            <div className="flex items-start gap-3">
                              <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gray-900 text-xs font-bold text-white shrink-0">
                                #{index + 1}
                              </span>
                              <div>
                                <div className="flex items-center gap-2">
                                  <h4 className="font-bold text-gray-900 text-base">
                                    {candidateDisplayName}
                                  </h4>
                                  {getMatchLevelBadge(match.match_level, match.overall_score)}
                                </div>
                                {match.candidate_email && (
                                  <p className="text-xs text-gray-500 mt-0.5">{match.candidate_email}</p>
                                )}
                              </div>
                            </div>

                            {/* Overall Score Meter */}
                            <div className="flex items-center gap-3 self-end sm:self-center">
                              <div className="text-right">
                                <span className="text-2xl font-black tracking-tight text-gray-900">
                                  {match.overall_score}%
                                </span>
                                <p className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">
                                  Overall Match
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* 3 Pillars Score Breakdown Cards */}
                          <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
                            <div className="rounded-xl border border-gray-100 bg-gray-50/80 p-3">
                              <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-500">
                                Skill Fit (40%)
                              </p>
                              <div className="mt-1 flex items-baseline justify-between">
                                <span className="text-lg font-bold text-gray-900">{match.skill_score}%</span>
                                <span className="text-[11px] text-gray-500">
                                  {match.matched_skills.length} /{" "}
                                  {match.matched_skills.length + match.missing_skills.length} skills
                                </span>
                              </div>
                            </div>

                            <div className="rounded-xl border border-gray-100 bg-gray-50/80 p-3">
                              <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-500">
                                Experience Fit (20%)
                              </p>
                              <div className="mt-1 flex items-baseline justify-between">
                                <span className="text-lg font-bold text-gray-900">
                                  {match.experience_score}%
                                </span>
                                <span
                                  className={`text-[11px] font-medium ${
                                    match.experience_status.toLowerCase().includes("meet")
                                      ? "text-emerald-600"
                                      : "text-amber-600"
                                  }`}
                                >
                                  {match.experience_status}
                                </span>
                              </div>
                            </div>

                            <div className="rounded-xl border border-gray-100 bg-gray-50/80 p-3">
                              <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-500">
                                Semantic Similarity (40%)
                              </p>
                              <div className="mt-1 flex items-baseline justify-between">
                                <span className="text-lg font-bold text-gray-900">
                                  {match.semantic_score}%
                                </span>
                                <span className="text-[11px] text-gray-500">Vector Cosine</span>
                              </div>
                            </div>
                          </div>

                          {/* Skills Comparison (Matched vs Missing) */}
                          <div className="mt-4 space-y-2 pt-3 border-t border-gray-100 text-xs">
                            {/* Matched Skills */}
                            {match.matched_skills.length > 0 && (
                              <div className="flex flex-wrap items-center gap-1.5">
                                <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-700 min-w-28">
                                  <CheckCircle2 size={13} className="text-emerald-500" /> Matched Skills:
                                </span>
                                {match.matched_skills.map((skill) => (
                                  <span
                                    key={skill}
                                    className="rounded-md bg-emerald-50 border border-emerald-200 px-2 py-0.5 text-[11px] font-medium text-emerald-800"
                                  >
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            )}

                            {/* Missing Skills */}
                            {match.missing_skills.length > 0 && (
                              <div className="flex flex-wrap items-center gap-1.5">
                                <span className="flex items-center gap-1 text-[11px] font-semibold text-rose-700 min-w-28">
                                  <XCircle size={13} className="text-rose-500" /> Missing Skills:
                                </span>
                                {match.missing_skills.map((skill) => (
                                  <span
                                    key={skill}
                                    className="rounded-md bg-rose-50 border border-rose-200 px-2 py-0.5 text-[11px] font-medium text-rose-800"
                                  >
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* AI Explanation Callout */}
                          {match.explanation && (
                            <div className="mt-4 rounded-xl bg-gray-50 border border-gray-200/80 p-3.5 text-xs text-gray-700 leading-relaxed flex items-start gap-2.5">
                              <Sparkles size={16} className="text-gray-900 shrink-0 mt-0.5" />
                              <div>
                                <span className="font-semibold text-gray-900 block mb-0.5">
                                  AI Match Explanation:
                                </span>
                                <p>{match.explanation}</p>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="rounded-2xl border-2 border-dashed border-gray-200 bg-white p-12 text-center">
              <Briefcase className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-3 text-base font-bold text-gray-900">Select a Job Posting</h3>
              <p className="mt-1 text-xs text-gray-500 max-w-sm mx-auto">
                Select an open position from the left sidebar to view candidates ranked by multi-pillar compatibility.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Add Job Modal Dialog */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative max-h-[90vh] overflow-y-auto rounded-2xl">
            <AddJobForm
              onJobCreated={(newJob) => {
                setShowAddForm(false);
                loadJobs(newJob.id);
              }}
              onCancel={() => setShowAddForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
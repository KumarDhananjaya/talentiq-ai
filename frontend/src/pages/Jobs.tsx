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
  Sliders,
  RotateCcw,
  CheckSquare,
  Square,
  X,
  HelpCircle,
} from "lucide-react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip as RechartsTooltip,
} from "recharts";

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

  // Dynamic Weight Sliders
  const [showWeights, setShowWeights] = useState(false);
  const [skillWeight, setSkillWeight] = useState(40);
  const [expWeight, setExpWeight] = useState(20);
  const [semWeight, setSemWeight] = useState(40);

  // Comparison State
  const [selectedForCompare, setSelectedForCompare] = useState<number[]>([]);
  const [showCompareModal, setShowCompareModal] = useState(false);

  // AI Interview Questions Modal
  const [interviewCandidate, setInterviewCandidate] = useState<JobMatch | null>(null);

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
    setSelectedForCompare([]);
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

  // Toggle candidate for comparison
  const toggleCompare = (candidateId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (selectedForCompare.includes(candidateId)) {
      setSelectedForCompare(selectedForCompare.filter((id) => id !== candidateId));
    } else {
      if (selectedForCompare.length >= 3) {
        alert("You can compare up to 3 candidates simultaneously.");
        return;
      }
      setSelectedForCompare([...selectedForCompare, candidateId]);
    }
  };

  // Dynamically re-weight and filter matches
  const processedMatches = useMemo(() => {
    const totalWeight = (skillWeight + expWeight + semWeight) || 100;
    const wSkill = skillWeight / totalWeight;
    const wExp = expWeight / totalWeight;
    const wSem = semWeight / totalWeight;

    return matches
      .map((match) => {
        const dynamicScore = Math.round(
          match.skill_score * wSkill + match.experience_score * wExp + match.semantic_score * wSem
        );
        return {
          ...match,
          computed_score: dynamicScore,
        };
      })
      .filter((match) => {
        const matchScore = match.computed_score >= minScoreFilter;
        const searchLower = searchFilter.toLowerCase().trim();
        if (!searchLower) return matchScore;

        const name = match.candidate_name?.toLowerCase() ?? "";
        const email = match.candidate_email?.toLowerCase() ?? "";
        const skills = (match.matched_skills || []).concat(match.missing_skills || []).join(" ").toLowerCase();

        return matchScore && (name.includes(searchLower) || email.includes(searchLower) || skills.includes(searchLower));
      })
      .sort((a, b) => b.computed_score - a.computed_score);
  }, [matches, skillWeight, expWeight, semWeight, minScoreFilter, searchFilter]);

  // Comparison Radar Data
  const radarComparisonData = useMemo(() => {
    const comparedMatches = matches.filter((m) => selectedForCompare.includes(m.candidate_id));
    if (comparedMatches.length === 0) return [];

    const dimensions = [
      { key: "skill_score", label: "Skill Fit" },
      { key: "experience_score", label: "Experience Compatibility" },
      { key: "semantic_score", label: "Semantic Similarity" },
      { key: "overall_score", label: "Overall Rating" },
    ];

    return dimensions.map((dim) => {
      const entry: Record<string, string | number> = { dimension: dim.label };
      comparedMatches.forEach((match) => {
        const name = match.candidate_name || `Candidate #${match.candidate_id}`;
        entry[name] = (match as any)[dim.key] ?? 0;
      });
      return entry;
    });

  }, [matches, selectedForCompare]);

  // Helper for Match Badge
  const getMatchLevelBadge = (score: number) => {
    if (score >= 85) {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 border border-emerald-200">
          <Sparkles size={12} /> Excellent Match
        </span>
      );
    }
    if (score >= 70) {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700 border border-blue-200">
          <TrendingUp size={12} /> Strong Match
        </span>
      );
    }
    if (score >= 50) {
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

  const RADAR_COLORS = ["#10b981", "#3b82f6", "#8b5cf6"];

  return (
    <div className="space-y-6">
      {/* Header & Post Job */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Job Matching & AI Ranking</h1>
          <p className="mt-1 text-sm text-gray-500">
            Define requirements, tune matching weights, and review multi-factor candidate fits.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setShowWeights(!showWeights)}
            className={`inline-flex items-center gap-1.5 rounded-xl border px-3.5 py-2.5 text-xs font-semibold shadow-xs transition ${
              showWeights ? "border-gray-900 bg-gray-900 text-white" : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
            }`}
          >
            <Sliders size={15} />
            {showWeights ? "Hide Weight Controls" : "Adjust AI Weights"}
          </button>

          <button
            type="button"
            onClick={() => setShowAddForm(true)}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-gray-900 px-4 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-gray-800"
          >
            <Plus size={16} />
            Post New Job
          </button>
        </div>
      </div>

      {/* Dynamic Recruiter Weights Tuning Card */}
      {showWeights && (
        <div className="rounded-2xl border border-gray-200 bg-linear-to-r from-gray-50 to-slate-50 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sliders size={16} className="text-gray-900" />
              <h3 className="text-sm font-bold text-gray-900">Human-In-The-Loop AI Weight Adjuster</h3>
            </div>
            <button
              onClick={() => {
                setSkillWeight(40);
                setExpWeight(20);
                setSemWeight(40);
              }}
              className="inline-flex items-center gap-1 text-xs font-medium text-gray-500 hover:text-gray-900"
            >
              <RotateCcw size={12} /> Reset to Default (40/20/40)
            </button>
          </div>

          <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
            {/* Skill Weight */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-gray-700">
                <span>Skill Match Weight</span>
                <span className="font-bold text-gray-900">{skillWeight}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={skillWeight}
                onChange={(e) => setSkillWeight(Number(e.target.value))}
                className="w-full accent-gray-900"
              />
            </div>

            {/* Experience Weight */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-gray-700">
                <span>Experience Weight</span>
                <span className="font-bold text-gray-900">{expWeight}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={expWeight}
                onChange={(e) => setExpWeight(Number(e.target.value))}
                className="w-full accent-gray-900"
              />
            </div>

            {/* Semantic Weight */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-gray-700">
                <span>Semantic Embeddings Weight</span>
                <span className="font-bold text-gray-900">{semWeight}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={semWeight}
                onChange={(e) => setSemWeight(Number(e.target.value))}
                className="w-full accent-gray-900"
              />
            </div>
          </div>
        </div>
      )}

      {/* Global Error */}
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

      {/* Main Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left Column: Job List (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500">
            Open Roles ({jobs.length})
          </h2>

          {loadingJobs ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse rounded-xl border border-gray-200 bg-white p-4 space-y-2">
                  <div className="h-4 w-2/3 bg-gray-200 rounded" />
                  <div className="h-3 w-1/2 bg-gray-100 rounded" />
                </div>
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className="rounded-2xl border-2 border-dashed border-gray-200 bg-white p-8 text-center">
              <Briefcase className="mx-auto h-10 w-10 text-gray-400" />
              <h3 className="mt-2 text-sm font-bold text-gray-900">No job postings</h3>
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
                        : "border-gray-200 bg-white hover:border-gray-300 hover:shadow-2xs"
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
                        <span className="text-[10px] text-gray-400 font-medium">+{skillsArray.length - 3}</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Job Details & Matches (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          {selectedJob ? (
            <>
              {/* Selected Job Banner */}
              <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-xs">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center rounded-md bg-gray-100 px-2.5 py-0.5 text-xs font-semibold text-gray-800">
                        Job #{selectedJob.id}
                      </span>
                      <h2 className="text-xl font-bold text-gray-900">{selectedJob.title}</h2>
                    </div>
                    <p className="mt-1 text-xs sm:text-sm text-gray-600 font-medium flex items-center gap-2">
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
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-300 bg-white px-3.5 py-2 text-xs font-semibold text-gray-700 shadow-2xs transition hover:bg-gray-50 disabled:opacity-50"
                  >
                    <RefreshCw size={14} className={recalculating ? "animate-spin text-gray-900" : ""} />
                    {recalculating ? "Evaluating Embeddings..." : "Recalculate Matches"}
                  </button>
                </div>

                {/* Description */}
                <div className="mt-4 pt-4 border-t border-gray-100 text-xs text-gray-600 leading-relaxed">
                  <p className="whitespace-pre-line line-clamp-2 hover:line-clamp-none transition-all">
                    {selectedJob.description}
                  </p>
                </div>

                {/* Skills */}
                {selectedJob.required_skills && (
                  <div className="mt-3 flex flex-wrap items-center gap-1.5">
                    <span className="text-xs font-semibold text-gray-700 mr-1">Required Skills:</span>
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

              {/* Filter & Compare Toolbar */}
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between rounded-xl border border-gray-200 bg-white p-3.5 shadow-2xs">
                <div className="relative flex-1">
                  <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    placeholder="Filter ranked matches by name or skill..."
                    className="w-full rounded-lg border border-gray-200 pl-9 pr-3 py-1.5 text-xs text-gray-900 transition focus:border-gray-900 focus:outline-none"
                  />
                </div>

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

                  {selectedForCompare.length >= 2 && (
                    <button
                      onClick={() => setShowCompareModal(true)}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white shadow-xs hover:bg-emerald-700"
                    >
                      Compare ({selectedForCompare.length})
                    </button>
                  )}
                </div>
              </div>

              {/* Candidate Matches Leaderboard */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700 flex items-center gap-2">
                    <Award size={16} className="text-gray-900" />
                    Ranked Candidates ({processedMatches.length})
                  </h3>
                  <span className="text-[11px] text-gray-400">
                    Weights: {skillWeight}% Skills • {expWeight}% Exp • {semWeight}% Semantic
                  </span>
                </div>

                {loadingMatches ? (
                  <div className="space-y-4">
                    {[1, 2].map((i) => (
                      <div key={i} className="animate-pulse rounded-2xl border border-gray-200 bg-white p-6 space-y-4">
                        <div className="h-5 w-1/3 bg-gray-200 rounded" />
                        <div className="h-16 bg-gray-100 rounded-xl" />
                      </div>
                    ))}
                  </div>
                ) : processedMatches.length === 0 ? (
                  <div className="rounded-2xl border-2 border-dashed border-gray-200 bg-white p-12 text-center">
                    <Layers className="mx-auto h-12 w-12 text-gray-300" />
                    <h4 className="mt-3 text-sm font-bold text-gray-900">No candidates match criteria</h4>
                    <p className="mt-1 text-xs text-gray-500">
                      Try recalculating matches or resetting the score filter.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {processedMatches.map((match, index) => {
                      const candidateDisplayName =
                        match.candidate_name || `Candidate #${match.candidate_id}`;
                      const isCompared = selectedForCompare.includes(match.candidate_id);

                      return (
                        <div
                          key={match.candidate_id}
                          className="rounded-2xl border border-gray-200 bg-white p-5 sm:p-6 shadow-xs transition hover:shadow-md hover:border-gray-300"
                        >
                          {/* Top Row */}
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
                                  {getMatchLevelBadge(match.computed_score)}
                                </div>
                                {match.candidate_email && (
                                  <p className="text-xs text-gray-500 mt-0.5">{match.candidate_email}</p>
                                )}
                              </div>
                            </div>

                            {/* Overall Score + Action Tools */}
                            <div className="flex items-center gap-3 self-end sm:self-center">
                              <button
                                onClick={(e) => toggleCompare(match.candidate_id, e)}
                                title="Select for side-by-side radar comparison"
                                className={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition ${
                                  isCompared
                                    ? "border-emerald-600 bg-emerald-50 text-emerald-800"
                                    : "border-gray-200 text-gray-600 hover:bg-gray-50"
                                }`}
                              >
                                {isCompared ? <CheckSquare size={14} /> : <Square size={14} />}
                                <span>Compare</span>
                              </button>

                              <div className="text-right pl-2 border-l border-gray-200">
                                <span className="text-2xl font-black tracking-tight text-gray-900">
                                  {match.computed_score}%
                                </span>
                                <p className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">
                                  Score
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* 3 Pillars Score Breakdown */}
                          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
                            <div className="rounded-xl border border-gray-100 bg-gray-50/80 p-3">
                              <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-500">
                                Skill Fit ({skillWeight}%)
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
                                Experience Fit ({expWeight}%)
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
                                Semantic Fit ({semWeight}%)
                              </p>
                              <div className="mt-1 flex items-baseline justify-between">
                                <span className="text-lg font-bold text-gray-900">
                                  {match.semantic_score}%
                                </span>
                                <span className="text-[11px] text-gray-500">Cosine 384-d</span>
                              </div>
                            </div>
                          </div>

                          {/* Matched & Missing Skills */}
                          <div className="mt-4 space-y-2 pt-3 border-t border-gray-100 text-xs">
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

                          {/* AI Explanation + Interview Generator Button */}
                          <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-gray-100">
                            {match.explanation && (
                              <p className="text-xs text-gray-600 leading-relaxed flex-1">
                                <span className="font-semibold text-gray-900 mr-1">AI Explanation:</span>
                                {match.explanation}
                              </p>
                            )}

                            <button
                              onClick={() => setInterviewCandidate(match)}
                              className="inline-flex items-center gap-1.5 rounded-xl border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs font-bold text-gray-800 hover:bg-gray-100 transition shrink-0"
                            >
                              <HelpCircle size={14} className="text-purple-600" />
                              Generate Interview Questions
                            </button>
                          </div>
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
              <h3 className="mt-3 text-base font-bold text-gray-900">Select a Job Position</h3>
              <p className="mt-1 text-xs text-gray-500 max-w-sm mx-auto">
                Select an open position from the left sidebar to inspect multi-factor candidate compatibility.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Radar Comparison Modal */}
      {showCompareModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-3xl bg-white p-6 sm:p-8 shadow-2xl border border-gray-200">
            <div className="flex items-center justify-between pb-4 border-b border-gray-100">
              <div>
                <h3 className="text-xl font-bold text-gray-900">Candidate Multi-Axis Comparison</h3>
                <p className="text-xs text-gray-500">Visualizing compatibility across Skill, Experience, and Semantic vector dimensions.</p>
              </div>
              <button
                onClick={() => setShowCompareModal(false)}
                className="rounded-full p-2 text-gray-400 hover:bg-gray-100"
              >
                <X size={18} />
              </button>
            </div>

            {/* Radar Chart */}
            <div className="h-72 w-full my-4">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarComparisonData}>
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis dataKey="dimension" tick={{ fill: "#374151", fontSize: 12, fontWeight: 600 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#9ca3af" />
                  {selectedForCompare.map((candId, idx) => {
                    const match = matches.find((m) => m.candidate_id === candId);
                    const name = match?.candidate_name || `Candidate #${candId}`;
                    return (
                      <Radar
                        key={candId}
                        name={name}
                        dataKey={name}
                        stroke={RADAR_COLORS[idx % RADAR_COLORS.length]}
                        fill={RADAR_COLORS[idx % RADAR_COLORS.length]}
                        fillOpacity={0.3}
                      />
                    );
                  })}
                  <Legend />
                  <RechartsTooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Side by Side Breakdown Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-4 border-t border-gray-100 text-xs">
              {selectedForCompare.map((candId, idx) => {
                const match = matches.find((m) => m.candidate_id === candId);
                if (!match) return null;
                return (
                  <div key={candId} className="rounded-2xl border border-gray-200 bg-gray-50/70 p-4 space-y-2">
                    <div className="flex items-center gap-2 font-bold text-gray-900">
                      <span className="h-3 w-3 rounded-full" style={{ backgroundColor: RADAR_COLORS[idx % RADAR_COLORS.length] }} />
                      <span className="truncate">{match.candidate_name || `Candidate #${candId}`}</span>
                    </div>
                    <div className="text-lg font-black text-gray-900">{match.overall_score}% <span className="text-xs font-normal text-gray-500">Overall</span></div>
                    <p className="text-[11px] text-gray-600"><b>Matched:</b> {match.matched_skills.join(", ") || "None"}</p>
                    <p className="text-[11px] text-rose-600"><b>Missing:</b> {match.missing_skills.join(", ") || "None"}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* AI Interview Questions Modal */}
      {interviewCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-3xl bg-white p-6 sm:p-8 shadow-2xl border border-gray-200">
            <div className="flex items-center justify-between pb-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100 text-purple-700">
                  <Sparkles size={18} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">AI Screening Questions</h3>
                  <p className="text-xs text-gray-500">Tailored for {interviewCandidate.candidate_name || `Candidate #${interviewCandidate.candidate_id}`} ({selectedJob?.title || "Target Role"})</p>
                </div>
              </div>
              <button
                onClick={() => setInterviewCandidate(null)}
                className="rounded-full p-2 text-gray-400 hover:bg-gray-100"
              >
                <X size={18} />
              </button>
            </div>

            {/* Generated Questions */}
            <div className="mt-5 space-y-4 text-xs">
              {interviewCandidate.missing_skills.length > 0 ? (
                <>
                  <div className="rounded-2xl border border-purple-100 bg-purple-50/50 p-4 space-y-2">
                    <span className="font-bold text-purple-900 block">
                      1. Technical Deep-Dive: {interviewCandidate.missing_skills[0].toUpperCase()}
                    </span>
                    <p className="text-gray-700 leading-relaxed">
                      "Our team relies heavily on <b>{interviewCandidate.missing_skills[0]}</b>. Can you walk us through how you would ramp up on this technology or describe any analogous frameworks you have used in production?"
                    </p>
                    <div className="text-[11px] text-purple-700 pt-1 border-t border-purple-100">
                      <b>Evaluation Tip:</b> Assess conceptual transfer from candidate's existing stack ({interviewCandidate.matched_skills.join(", ") || "Python"}).
                    </div>
                  </div>

                  {interviewCandidate.missing_skills.length > 1 && (
                    <div className="rounded-2xl border border-blue-100 bg-blue-50/50 p-4 space-y-2">
                      <span className="font-bold text-blue-900 block">
                        2. Architectural Trade-offs: {interviewCandidate.missing_skills[1].toUpperCase()}
                      </span>
                      <p className="text-gray-700 leading-relaxed">
                        "In your previous projects, how did you architect scalable solutions without <b>{interviewCandidate.missing_skills[1]}</b>, and what pitfalls did you encounter?"
                      </p>
                    </div>
                  )}
                </>
              ) : (
                <div className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-4 space-y-2">
                  <span className="font-bold text-emerald-900 block">
                    1. Advanced System Design & Best Practices
                  </span>
                  <p className="text-gray-700 leading-relaxed">
                    "You match 100% of our core tech stack ({interviewCandidate.matched_skills.join(", ")}). Describe the most complex architectural challenge you solved using these technologies."
                  </p>
                </div>
              )}

              <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4 space-y-2">
                <span className="font-bold text-gray-900 block">
                  3. Experience & Alignment Assessment
                </span>
                <p className="text-gray-700 leading-relaxed">
                  "This role requires {selectedJob?.minimum_experience || 2}+ years. How do your past responsibilities align with the high-ownership requirements of this position?"
                </p>
              </div>
            </div>


            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setInterviewCandidate(null)}
                className="rounded-xl bg-gray-900 px-4 py-2 text-xs font-bold text-white hover:bg-gray-800"
              >
                Close Questions Pack
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Job Modal */}
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
import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { getCandidates } from "../services/candidateService";
import { getJobs, getJobMatches } from "../services/jobService";
import type { Candidate } from "../types/candidate";
import type { Job, JobMatch } from "../types/job";
import {
  Users,
  Briefcase,
  Sparkles,
  TrendingUp,
  Award,
  ArrowUpRight,
  BrainCircuit,
  CheckCircle2,
  Layers,
  ArrowRight,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const PIE_COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#f43f5e"];

export default function Dashboard() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [allMatches, setAllMatches] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [candidateData, jobData] = await Promise.all([
          getCandidates(),
          getJobs(),
        ]);
        setCandidates(candidateData);
        setJobs(jobData);

        // Fetch matches for available jobs
        if (jobData.length > 0) {
          const matchPromises = jobData.slice(0, 3).map((job) =>
            getJobMatches(job.id).catch(() => ({ matches: [] }))
          );
          const results = await Promise.all(matchPromises);
          const combined = results.flatMap((r) => r.matches || []);
          setAllMatches(combined);
        }
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  // Compute Skill Frequency Data
  const topSkillsData = useMemo(() => {
    const counts: Record<string, number> = {};
    candidates.forEach((c) => {
      let skillList: string[] = [];
      if (Array.isArray(c.skills)) {
        skillList = c.skills;
      } else if (typeof c.skills === "string") {
        skillList = c.skills.split(",").map((s) => s.trim()).filter(Boolean);
      }
      skillList.forEach((s) => {
        const norm = s.trim();
        if (norm) counts[norm] = (counts[norm] || 0) + 1;
      });
    });

    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([name, count]) => ({ name, count }));
  }, [candidates]);

  // Compute Match Level Distribution
  const matchDistributionData = useMemo(() => {
    let excellent = 0;
    let strong = 0;
    let moderate = 0;
    let weak = 0;

    allMatches.forEach((m) => {
      if (m.overall_score >= 85) excellent++;
      else if (m.overall_score >= 70) strong++;
      else if (m.overall_score >= 50) moderate++;
      else weak++;
    });

    return [
      { name: "Excellent (85%+)", value: excellent || 1 },
      { name: "Strong (70-84%)", value: strong || 1 },
      { name: "Moderate (50-69%)", value: moderate || 1 },
      { name: "Weak (<50%)", value: weak || 1 },
    ];
  }, [allMatches]);

  const avgMatchScore = useMemo(() => {
    if (allMatches.length === 0) return 0;
    const total = allMatches.reduce((acc, m) => acc + m.overall_score, 0);
    return Math.round(total / allMatches.length);
  }, [allMatches]);

  const highMatchCount = useMemo(() => {
    return allMatches.filter((m) => m.overall_score >= 70).length;
  }, [allMatches]);

  return (
    <div className="space-y-8">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-linear-to-r from-gray-900 via-slate-900 to-gray-800 p-8 text-white shadow-xl">
        <div className="relative z-10 flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl space-y-2">
            <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold backdrop-blur-md">
              <Sparkles size={13} className="text-amber-300" />
              <span>USYD Capstone Portfolio Showcase</span>
            </div>
            <h1 className="text-3xl font-black tracking-tight sm:text-4xl">
              TalentIQ AI Intelligence Engine
            </h1>
            <p className="text-sm text-gray-300 leading-relaxed">
              Autonomous candidate screening, NLP entity extraction, and multi-pillar semantic matching ranking.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/jobs"
              className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-xs font-bold text-gray-900 shadow-md transition hover:bg-gray-100"
            >
              <Briefcase size={16} />
              Review AI Matches
              <ArrowRight size={14} />
            </Link>
            <Link
              to="/candidates"
              className="inline-flex items-center gap-2 rounded-xl bg-white/10 px-4 py-2.5 text-xs font-bold text-white backdrop-blur-md transition hover:bg-white/20"
            >
              <Users size={16} />
              View Talent Pool
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Stats Overview */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Metric 1 */}
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-xs transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Total Candidates
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
              <Users size={20} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-black tracking-tight text-gray-900">
              {loading ? "..." : candidates.length}
            </span>
            <span className="text-xs font-medium text-emerald-600 flex items-center">
              <TrendingUp size={12} className="mr-0.5" /> Active Pool
            </span>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-xs transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Open Positions
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600">
              <Briefcase size={20} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-black tracking-tight text-gray-900">
              {loading ? "..." : jobs.length}
            </span>
            <span className="text-xs font-medium text-purple-600">Roles Configured</span>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-xs transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              High-Fit Matches
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
              <Award size={20} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-black tracking-tight text-gray-900">
              {loading ? "..." : highMatchCount}
            </span>
            <span className="text-xs font-medium text-emerald-600">≥ 70% Overall Score</span>
          </div>
        </div>

        {/* Metric 4 */}
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-xs transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Average Match Fit
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
              <BrainCircuit size={20} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-black tracking-tight text-gray-900">
              {loading ? "..." : `${avgMatchScore}%`}
            </span>
            <span className="text-xs font-medium text-gray-500">Across Evaluated Roles</span>
          </div>
        </div>
      </div>

      {/* Analytics Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left: Top In-Demand Skills (7 cols) */}
        <div className="lg:col-span-7 rounded-2xl border border-gray-200 bg-white p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-gray-900">Talent Pool Skill Distribution</h3>
              <p className="text-xs text-gray-500">Top technical competencies identified across candidate resumes.</p>
            </div>
            <span className="rounded-lg bg-gray-100 px-2.5 py-1 text-[11px] font-semibold text-gray-700">
              NLP Normalized
            </span>
          </div>

          <div className="h-64 w-full">
            {topSkillsData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topSkillsData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis
                    dataKey="name"
                    stroke="#888888"
                    fontSize={11}
                    tickLine={false}
                    axisLine={false}
                    interval={0}
                    angle={-20}
                    textAnchor="end"
                  />
                  <YAxis stroke="#888888" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1f2937",
                      borderRadius: "0.75rem",
                      border: "none",
                      color: "#fff",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="count" fill="#111827" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-gray-400">
                Loading talent skill data...
              </div>
            )}
          </div>
        </div>

        {/* Right: Match Score Breakdown Donut (5 cols) */}
        <div className="lg:col-span-5 rounded-2xl border border-gray-200 bg-white p-6 shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-gray-900">Match Quality Breakdown</h3>
            <p className="text-xs text-gray-500">Distribution of candidate tiers across current requirements.</p>
          </div>

          <div className="h-48 w-full my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={matchDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {matchDistributionData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1f2937",
                    borderRadius: "0.75rem",
                    border: "none",
                    color: "#fff",
                    fontSize: "12px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
              <span className="text-gray-600">Excellent (85%+)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-blue-500" />
              <span className="text-gray-600">Strong (70-84%)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-amber-500" />
              <span className="text-gray-600">Moderate (50-69%)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-rose-500" />
              <span className="text-gray-600">Weak (&lt;50%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Highlights / Recent Rankings Preview */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-gray-900">Top Ranked Matches (Live AI Evaluation)</h3>
            <p className="text-xs text-gray-500">Highest compatibility matches computed with 40/20/40 weighting.</p>
          </div>
          <Link
            to="/jobs"
            className="inline-flex items-center gap-1 text-xs font-semibold text-gray-900 hover:text-gray-700"
          >
            Open Job Hub
            <ArrowUpRight size={14} />
          </Link>
        </div>

        {allMatches.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-200 p-8 text-center text-xs text-gray-400">
            No matches calculated yet. Navigate to Jobs to run AI recalculation.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {allMatches.slice(0, 3).map((match, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-gray-100 bg-gray-50/70 p-4 transition hover:bg-white hover:border-gray-200 hover:shadow-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-gray-900 truncate">
                    {match.candidate_name || `Candidate #${match.candidate_id}`}
                  </span>
                  <span className="rounded-full bg-gray-900 px-2.5 py-0.5 text-xs font-bold text-white">
                    {match.overall_score}%
                  </span>
                </div>
                <p className="text-[11px] text-gray-500 mt-1 truncate">{match.candidate_email}</p>

                <div className="mt-3 flex items-center justify-between text-[11px] text-gray-600 pt-2 border-t border-gray-200/60">
                  <span>Skill Fit: <b>{match.skill_score}%</b></span>
                  <span>Semantic: <b>{match.semantic_score}%</b></span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
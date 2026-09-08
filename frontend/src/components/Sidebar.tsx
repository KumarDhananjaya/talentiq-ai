import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  BriefcaseBusiness,
  Sparkles,
  GraduationCap,
  Activity,
} from "lucide-react";

export default function Sidebar() {
  const links = [
    {
      name: "Overview",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "Job Matching Hub",
      path: "/jobs",
      icon: BriefcaseBusiness,
    },
    {
      name: "Talent Pool",
      path: "/candidates",
      icon: Users,
    },
  ];

  return (
    <aside className="min-h-screen w-64 border-r border-gray-200 bg-white p-5 flex flex-col justify-between shadow-xs">
      <div>
        {/* Brand Header */}
        <div className="mb-8 px-2">
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gray-900 text-white shadow-md">
              <Sparkles size={20} className="text-amber-400" />
            </div>
            <div>
              <h1 className="text-lg font-black tracking-tight text-gray-900 leading-tight">
                TalentIQ AI
              </h1>
              <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                Recruitment Intelligence
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1.5">
          {links.map((link) => {
            const Icon = link.icon;

            return (
              <NavLink
                key={link.path}
                to={link.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-semibold transition ${
                    isActive
                      ? "bg-gray-900 text-white shadow-xs"
                      : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  }`
                }
              >
                <Icon size={18} />
                {link.name}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer / USYD Badge */}
      <div className="pt-6 border-t border-gray-100 space-y-3">
        {/* Backend Online Status */}
        <div className="flex items-center justify-between px-3 py-2 rounded-xl bg-gray-50 border border-gray-100 text-[11px] font-medium text-gray-600">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>API Engine</span>
          </div>
          <span className="text-emerald-700 font-bold">Online</span>
        </div>

        {/* USYD Showcase Card */}
        <div className="rounded-xl bg-linear-to-br from-slate-900 to-gray-900 p-3.5 text-white shadow-xs">
          <div className="flex items-center gap-2 text-[11px] font-bold text-amber-400">
            <GraduationCap size={15} />
            <span>USYD Portfolio</span>
          </div>
          <p className="text-[11px] text-gray-300 mt-1 leading-snug">
            Built by Kumar Dhananjaya with FastAPI & sentence-transformers.
          </p>
        </div>
      </div>
    </aside>
  );
}
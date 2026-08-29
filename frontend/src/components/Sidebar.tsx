import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  BriefcaseBusiness,
} from "lucide-react";

const Sidebar = () => {
  const links = [
    {
      name: "Dashboard",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "Candidates",
      path: "/candidates",
      icon: Users,
    },
    {
      name: "Jobs",
      path: "/jobs",
      icon: BriefcaseBusiness,
    },
  ];

  return (
    <aside className="min-h-screen w-64 border-r bg-white p-5">
      <div className="mb-10">
        <h1 className="text-2xl font-bold">
          TalentIQ AI
        </h1>

        <p className="text-sm text-gray-500">
          Recruitment Intelligence
        </p>
      </div>

      <nav className="space-y-2">
        {links.map((link) => {
          const Icon = link.icon;

          return (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-4 py-3 transition ${
                  isActive
                    ? "bg-black text-white"
                    : "text-gray-600 hover:bg-gray-100"
                }`
              }
            >
              <Icon size={20} />

              {link.name}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;
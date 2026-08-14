import { NavLink, Outlet } from "react-router-dom";
import { Activity, FileText, LayoutGrid, LogOut, ShieldCheck, Users } from "lucide-react";
import { useAuth } from "./AuthContext";

const doctorNav = [
  { to: "/patients", label: "Patients", icon: Users },
  { to: "/reports", label: "Reports", icon: FileText },
];

const adminNav = [
  { to: "/admin", label: "Approval Queue", icon: ShieldCheck },
  { to: "/admin/doctors", label: "Doctors", icon: Users },
  { to: "/admin/patients", label: "Patients", icon: LayoutGrid },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const navItems = user?.role === "ADMIN" ? adminNav : doctorNav;

  return (
    <div className="flex min-h-screen bg-canvas">
      <aside className="flex w-56 flex-col justify-between border-r border-ink-100 bg-white px-4 py-6">
        <div>
          <div className="mb-8 flex items-center gap-2 px-2 text-ink-900">
            <Activity className="h-5 w-5 text-clinical-600" strokeWidth={2.25} />
            <span className="font-mono text-xs font-medium tracking-wide">NEUROSCAN</span>
          </div>
          <nav className="flex flex-col gap-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/admin"}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    isActive ? "bg-clinical-100 text-clinical-800" : "text-ink-500 hover:bg-ink-100 hover:text-ink-900"
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="flex flex-col gap-2 border-t border-ink-100 pt-4">
          <div className="px-2 text-xs text-ink-500">
            Signed in as <span className="font-medium text-ink-700">{user?.username}</span>
            <div className="mt-0.5 uppercase tracking-wide text-ink-300">{user?.role}</div>
          </div>
          <button
            onClick={() => logout()}
            className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-ink-500 hover:bg-ink-100 hover:text-ink-900"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-5xl px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

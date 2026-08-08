import { NavLink } from "react-router-dom";
import { useAuth } from "../lib/auth";

export default function Nav() {
  const { username, logout } = useAuth();

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-md text-sm font-medium ${
      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
    }`;

  return (
    <nav className="border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl flex items-center justify-between px-4 py-3">
        <div className="font-semibold text-slate-900">PHC MSDS Tracker — Al Shifa Laboratory</div>
        <div className="flex items-center gap-2">
          <NavLink to="/registry" className={linkClass}>Registry</NavLink>
          <NavLink to="/daily" className={linkClass}>Daily Due-List</NavLink>
          <NavLink to="/print" className={linkClass}>Print Pack</NavLink>
          <NavLink to="/drafting" className={linkClass}>AI Drafting</NavLink>
          {username && (
            <span className="ml-4 text-sm text-slate-500">
              {username} · <button className="underline" onClick={logout}>logout</button>
            </span>
          )}
        </div>
      </div>
    </nav>
  );
}

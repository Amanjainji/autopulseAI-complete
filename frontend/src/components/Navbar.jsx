import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import AvatarBtn from "./AvatarBtn.jsx";
import { getSession, clearSession } from "../lib/session.js";

export default function Navbar(){
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [session, setSession] = useState(()=> getSession());

  useEffect(()=>{
    const sync = ()=> setSession(getSession());
    window.addEventListener("autopulse:session", sync);
    const timer = setInterval(sync, 1500);
    return ()=>{
      window.removeEventListener("autopulse:session", sync);
      clearInterval(timer);
    };
  },[]);

  const links = useMemo(()=>{
    if(session?.role === "admin"){
      return [
        { to: "/admin", label: "Admin Console" },
        { to: "/admin/profile", label: "Admin Profile" },
        { to: "/dashboard", label: "Driver View" }
      ];
    }
    return [
      { to: "/dashboard", label: "Dashboard" },
      { to: "/service", label: "Service" },
      { to: "/profile", label: "Profile" }
    ];
  },[session]);

  const signOut = ()=>{
    clearSession();
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <header className="w-full border-b border-white/10 bg-[rgba(8,10,13,0.72)]/90 backdrop-blur-2xl">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="h-9 w-9 rounded-full bg-gradient-to-br from-[var(--accent)]/60 to-transparent flex items-center justify-center text-black font-semibold">AP</div>
              <div>
                <p className="text-xl font-semibold tracking-tight text-white accent-underline">AutoPulse AI</p>
                <p className="text-xs uppercase tracking-[0.35em] text-white/40">Predictive Mobility Command Center</p>
              </div>
            </div>
            <span className="hidden lg:inline-flex badge-accent">Automotive Intelligence</span>
          </div>
          <nav className="hidden md:flex items-center gap-1 text-sm text-white/85">
            {links.map(link => {
              const active = pathname.startsWith(link.to);
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`relative px-3 py-2 rounded-lg transition ${active ? "text-white" : "text-white/70 hover:text-white"}`}
                >
                  {link.label}
                  {active && (
                    <span className="absolute inset-x-2 -bottom-[6px] h-[2px] rounded-full bg-[var(--accent)]" />
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          {session ? (
            <button className="btn-ghost text-sm !px-4" onClick={signOut}>Sign Out</button>
          ) : (
            <button
              className="btn-ghost text-sm !px-4"
              onClick={()=>navigate('/login')}
            >
              Sign In
            </button>
          )}
          <AvatarBtn />
        </div>
      </div>
    </header>
  );
}

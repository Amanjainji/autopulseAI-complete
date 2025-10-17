import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { getSession } from "../lib/session.js";

const USER_LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: "⌂" },
  { to: "/service", label: "Service", icon: "⚙" },
  { to: "/profile", label: "Profile", icon: "☺" }
];

const ADMIN_LINKS = [
  { to: "/admin", label: "Admin", icon: "⚡" }
];

export default function Sidebar(){
  const { pathname } = useLocation();
  const [session, setSession] = useState(()=> getSession());

  useEffect(()=>{
    const sync = ()=> setSession(getSession());
    window.addEventListener("autopulse:session", sync);
    return ()=> window.removeEventListener("autopulse:session", sync);
  },[]);

  const links = useMemo(()=>{
    if(session?.role === "admin") return ADMIN_LINKS;
    return USER_LINKS;
  },[session]);

  return (
    <aside className="hidden md:flex w-24 flex-col justify-between border-r border-white/10 bg-[rgba(6,8,11,0.8)]/90 backdrop-blur-xl">
      <div className="pt-8 pb-6 flex flex-col items-center gap-6">
        <div className="h-24 w-[2px] rounded-full bg-gradient-to-b from-[var(--accent)]/60 to-transparent" />
        <nav className="flex flex-col gap-4">
          {links.map(link => {
            const active = pathname.startsWith(link.to);
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`group relative flex flex-col items-center gap-2 text-xs tracking-[0.3em] uppercase ${active ? "text-white" : "text-white/50 hover:text-white"}`}
              >
                <span className={`flex h-12 w-12 items-center justify-center rounded-2xl border transition ${active ? "border-[var(--accent)]/70 bg-[var(--accent-soft)]" : "border-white/10 bg-white/5 group-hover:border-white/20"}`}>
                  <span className="text-lg">{link.icon}</span>
                </span>
                <span className="text-[0.55rem]">{link.label}</span>
                {active && <span className="absolute -left-5 h-12 w-[3px] rounded-full bg-[var(--accent)]" />}
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="pb-8 flex flex-col items-center gap-2 text-[10px] text-white/30 tracking-[0.35em] uppercase">
        <span>Auto</span>
        <span>Pulse</span>
      </div>
    </aside>
  );
}

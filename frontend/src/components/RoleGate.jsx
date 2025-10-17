import { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { getSession } from "../lib/session.js";

export default function RoleGate({ allow = [], children }){
  const location = useLocation();
  const [session, setSession] = useState(()=> getSession());

  useEffect(()=>{
    const sync = ()=> setSession(getSession());
    window.addEventListener("autopulse:session", sync);
    return ()=> window.removeEventListener("autopulse:session", sync);
  },[]);

  if(!session){
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if(allow.length > 0 && !allow.includes(session.role)){
    const fallback = session.role === "admin" ? "/admin" : "/dashboard";
    return <Navigate to={fallback} replace />;
  }

  return children;
}

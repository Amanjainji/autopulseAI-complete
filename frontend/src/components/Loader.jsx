import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const LETTERS = ["A","u","t","o","p","u","l","s","e"];

export default function Loader(){
  const navigate = useNavigate();

  useEffect(()=>{
    let target = "/login";
    try{
      const rawSession = localStorage.getItem("autopulse.session");
      if(rawSession){
        const parsed = JSON.parse(rawSession);
        target = parsed?.role === "admin" ? "/admin" : "/dashboard";
      }else{
        const token = localStorage.getItem("token");
        if(token === "admin-session") target = "/admin";
        else if(token) target = "/dashboard";
      }
    }catch{
      target = "/login";
    }
    const timer = setTimeout(()=> navigate(target), 2400);
    return ()=> clearTimeout(timer);
  },[navigate]);

  return (
    <div className="loader-screen">
      <div className="loader-wrapper" aria-hidden="true">
        {LETTERS.map((letter, idx)=>(
          <span key={letter + idx} className="loader-letter">{letter}</span>
        ))}
        <div className="loader" />
      </div>
    </div>
  );
}

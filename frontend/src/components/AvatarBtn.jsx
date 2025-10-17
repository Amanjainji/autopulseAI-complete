import { useNavigate } from "react-router-dom";
export default function AvatarBtn(){
  const navigate = useNavigate();
  return (
    <div className="flex items-center gap-2 cursor-pointer" onClick={()=>navigate("/profile")}>
      <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-slate-700 to-slate-900 border border-subtle flex items-center justify-center">
        <span className="text-white font-medium">A</span>
      </div>
      <div className="hidden md:block text-sm text-white/90">Aman Jain</div>
    </div>
  );
}

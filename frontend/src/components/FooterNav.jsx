import { Link } from "react-router-dom";
export default function FooterNav(){
  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-[rgba(255,255,255,0.02)] px-4 py-2 rounded-full border border-subtle flex gap-4 shadow-lg z-40">
      <Link to="/dashboard" className="text-white/80">Home</Link>
      <Link to="/service" className="text-white/80">Service</Link>
      <Link to="/profile" className="text-white/80">Profile</Link>
    </div>
  );
}

import React, { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import api from "../lib/api.js";

export default function ChatWidget({ customer }){
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState([{from:"bot", text:"Hello! I can help with bookings or vehicle health."}]);
  const [text, setText] = useState("");
  const bottomRef = useRef(null);
  const resolvedCustomer = useMemo(()=>{
    if(customer) return customer;
    try{
      const cached = sessionStorage.getItem("autopulse.primaryCustomer");
      return cached ? JSON.parse(cached) : null;
    }catch{
      return null;
    }
  },[customer]);
  const activeUserId = resolvedCustomer?.id || "CUST-001";

  const send = async (event)=>{
    if(event)
      event.preventDefault();
    const message = text.trim();
    if(!message) return;
    setMsgs(m=>[...m,{from:"user",text: message}]);
    const payload = { user_id: activeUserId, message };
    setText("");
    try{
      const res = await api.post("/api/agents/chat", payload);
      const reply = res.data?.reply || "Okay — I will get back to you.";
      setMsgs(m=>[...m,{from:"bot",text:reply}]);
    }catch{
      setMsgs(m=>[...m,{from:"bot",text:"(offline) Unable to contact agent."}]);
    }
  };

  useEffect(()=>{
    if(bottomRef.current){
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  },[msgs]);

  return (
    <div className="fixed right-6 bottom-6 z-50">
      <motion.button
        whileTap={{ scale: 0.95 }}
        onClick={()=>setOpen(o=>!o)}
        className="w-14 h-14 rounded-full bg-[var(--accent)] text-black flex items-center justify-center shadow-lg"
      >
        💬
      </motion.button>
      {open && (
        <motion.div
          initial={{opacity:0, y:20}}
          animate={{opacity:1, y:0}}
          className="mt-3 w-80 rounded-2xl border border-white/10 bg-[rgba(15,18,26,0.92)] backdrop-blur-md shadow-2xl p-4"
        >
          {resolvedCustomer && (
            <div className="mb-2 text-xs uppercase tracking-[0.35em] text-white/50">
              Concierge for {resolvedCustomer.name}
            </div>
          )}
          <div className="max-h-56 overflow-y-auto mb-3 pr-1 space-y-2">
            {msgs.map((m, idx)=>(
              <div
                key={idx}
                className={`${m.from==="bot" ? "text-white/90" : "text-white"} ${m.from==="bot" ? "text-sm" : "text-sm font-medium"}`}
              >
                <div
                  className={`${m.from==="bot" ? "bg-white/10" : "bg-[rgba(0,180,255,0.18)] text-cyan-100"} inline-block max-w-full px-3 py-2 rounded-xl shadow-sm`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
          <form className="flex gap-2" onSubmit={send}>
            <input
              value={text}
              onChange={(e)=>setText(e.target.value)}
              onKeyDown={(e)=>{
                if(e.key === "Enter" && !e.shiftKey){
                  e.preventDefault();
                  send();
                }
              }}
              className="flex-1 input"
              placeholder="Ask about your vehicle..."
            />
            <button type="submit" className="btn-primary flex-shrink-0 px-4 whitespace-nowrap">Send</button>
          </form>
        </motion.div>
      )}
    </div>
  );
}

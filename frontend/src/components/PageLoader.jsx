import React from "react";
import { motion } from "framer-motion";

export default function PageLoader({ label = "Preparing workspace..." }){
  return (
    <div className="absolute inset-0 z-40 flex items-center justify-center bg-[rgba(8,12,20,0.92)] backdrop-blur-sm">
      <motion.div
        className="flex flex-col items-center gap-4 text-white"
        initial={{ opacity: 0, scale: 0.92 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <motion.span
          className="h-12 w-12 rounded-full border-2 border-white/15 border-t-[var(--accent)]"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.1, ease: "linear", repeat: Infinity }}
        />
        <div className="text-sm uppercase tracking-[0.28em] text-white/60">Loading</div>
        <p className="text-base font-medium text-white/80">{label}</p>
      </motion.div>
    </div>
  );
}

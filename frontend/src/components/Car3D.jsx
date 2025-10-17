import React, { useEffect, useRef } from "react";

export default function Car3D(){
  const canvasRef = useRef(null);

  useEffect(()=>{
    const canvas = canvasRef.current;
    if(!canvas) return undefined;
    const ctx = canvas.getContext("2d");
    let frameId;

    const draw = (time)=>{
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      const dpr = window.devicePixelRatio || 1;

      if(canvas.width !== width * dpr || canvas.height !== height * dpr){
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }else{
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }

      ctx.clearRect(0, 0, width, height);

      const bg = ctx.createLinearGradient(0, 0, width, height);
      bg.addColorStop(0, "rgba(0, 180, 255, 0.22)");
      bg.addColorStop(1, "rgba(6, 10, 18, 0.92)");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, width, height);

      const t = time * 0.0015;
      const pulse = 0.35 + 0.45 * Math.sin(t * 1.4) ** 2;

      const scanY = ((time * 0.05) % (height + 120)) - 120;
      const scanGrad = ctx.createLinearGradient(0, scanY, 0, scanY + 90);
      scanGrad.addColorStop(0, "rgba(0, 180, 255, 0)");
      scanGrad.addColorStop(0.5, "rgba(0, 180, 255, 0.24)");
      scanGrad.addColorStop(1, "rgba(0, 180, 255, 0)");
      ctx.fillStyle = scanGrad;
      ctx.fillRect(0, scanY, width, 90);

      ctx.lineJoin = "round";
      ctx.lineCap = "round";
      ctx.lineWidth = 2;
      ctx.strokeStyle = `rgba(255,255,255,${0.28 + pulse * 0.35})`;

      ctx.beginPath();
      ctx.moveTo(width * 0.18, height * 0.65);
      ctx.quadraticCurveTo(width * 0.24, height * 0.45, width * 0.36, height * 0.38);
      ctx.quadraticCurveTo(width * 0.5, height * 0.28, width * 0.64, height * 0.38);
      ctx.quadraticCurveTo(width * 0.76, height * 0.45, width * 0.82, height * 0.65);
      ctx.quadraticCurveTo(width * 0.78, height * 0.78, width * 0.64, height * 0.82);
      ctx.lineTo(width * 0.36, height * 0.82);
      ctx.quadraticCurveTo(width * 0.22, height * 0.78, width * 0.18, height * 0.65);
      ctx.closePath();

      const bodyGrad = ctx.createLinearGradient(width * 0.3, height * 0.34, width * 0.72, height * 0.84);
      bodyGrad.addColorStop(0, `rgba(0, 201, 255, ${0.24 + pulse * 0.4})`);
      bodyGrad.addColorStop(1, "rgba(255, 255, 255, 0.08)");
      ctx.fillStyle = bodyGrad;
      ctx.fill();
      ctx.stroke();

      ctx.lineWidth = 1.2;
      ctx.strokeStyle = `rgba(255,255,255,${0.22 + pulse * 0.25})`;
      ctx.beginPath();
      ctx.moveTo(width * 0.32, height * 0.52);
      ctx.lineTo(width * 0.68, height * 0.52);
      ctx.moveTo(width * 0.36, height * 0.68);
      ctx.lineTo(width * 0.64, height * 0.68);
      ctx.stroke();

      const wheels = [
        [width * 0.3, height * 0.8],
        [width * 0.7, height * 0.8],
        [width * 0.32, height * 0.44],
        [width * 0.68, height * 0.44]
      ];
      wheels.forEach(([x, y], index)=>{
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(t * 1.8 + index * 0.9);
        ctx.strokeStyle = "rgba(0, 255, 224, 0.45)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(0, 0, 16, 0, Math.PI * 2);
        ctx.stroke();
        ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(0, 0, 11, 0, Math.PI * 2);
        ctx.moveTo(-11, 0);
        ctx.lineTo(11, 0);
        ctx.moveTo(0, -11);
        ctx.lineTo(0, 11);
        ctx.stroke();
        ctx.restore();
      });

      ctx.fillStyle = "rgba(0, 255, 224, 0.24)";
      for(let i = 0; i < 12; i++){
        const phase = i / 12;
        const px = width * (0.12 + 0.76 * phase);
        const py = height * (0.22 + 0.08 * Math.sin(t * 1.6 + phase * 6));
        ctx.globalAlpha = 0.25 + 0.3 * Math.sin(t * 2 + i);
        ctx.fillRect(px, py, 22, 2);
      }
      ctx.globalAlpha = 1;

      const telemetryPulse = ctx.createRadialGradient(width * 0.5, height * 0.3, 0, width * 0.5, height * 0.3, 140);
      telemetryPulse.addColorStop(0, `rgba(0, 180, 255, ${pulse * 0.28})`);
      telemetryPulse.addColorStop(1, "rgba(0, 180, 255, 0)");
      ctx.fillStyle = telemetryPulse;
      ctx.fillRect(0, 0, width, height);

      frameId = requestAnimationFrame(draw);
    };

    const handleResize = ()=>{
      cancelAnimationFrame(frameId);
      frameId = requestAnimationFrame(draw);
    };

    frameId = requestAnimationFrame(draw);
    window.addEventListener("resize", handleResize);

    return ()=>{
      cancelAnimationFrame(frameId);
      window.removeEventListener("resize", handleResize);
    };
  },[]);

  return (
    <div className="card p-3">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm text-white/80">Vehicle motion blueprint</h4>
        <span className="pill bg-white/10 text-white/60">Lightweight render</span>
      </div>
      <div className="rounded-3xl border border-white/10 bg-white/5 overflow-hidden">
        <canvas ref={canvasRef} className="w-full h-56" />
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';

export default function SVIGauge({ score = 0, size = 250 }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const steps = 60;
    const stepTime = Math.abs(Math.floor(duration / steps));
    let current = 0;
    
    const timer = setInterval(() => {
      current += (score / steps);
      if (current >= score) {
        setAnimatedScore(score);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.floor(current));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [score]);

  const radius = size * 0.4;
  const strokeWidth = size * 0.1;
  const cx = size / 2;
  const cy = size * 0.75; // Shift down for semicircle
  
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  const getRiskColor = (val) => {
    if (val <= 25) return '#22c55e'; // risk.low
    if (val <= 50) return '#eab308'; // risk.medium
    if (val <= 75) return '#ef4444'; // risk.high
    return '#7f1d1d'; // risk.critical
  };

  const getRiskLabel = (val) => {
    if (val <= 25) return 'Low Risk';
    if (val <= 50) return 'Moderate Risk';
    if (val <= 75) return 'High Risk';
    return 'Critical Risk';
  };

  const activeColor = getRiskColor(animatedScore);
  const activeLabel = getRiskLabel(animatedScore);

  return (
    <div className="flex flex-col items-center justify-center relative" style={{ width: size, height: size * 0.8 }}>
      <svg width={size} height={size * 0.8} viewBox={`0 0 ${size} ${size * 0.8}`} className="overflow-visible">
        {/* Background Arc */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Foreground Animated Arc */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke={activeColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className="svi-gauge-path"
        />
      </svg>
      
      {/* Score Text */}
      <div className="absolute flex flex-col items-center justify-end pb-4" style={{ top: 0, left: 0, right: 0, bottom: 0 }}>
        <span className="text-5xl font-bold tabular-nums" style={{ color: activeColor }}>
          {animatedScore}
        </span>
        <span className="text-sm font-semibold uppercase tracking-wider mt-1 text-slate-500">
          SVI Score
        </span>
        <span className="mt-3 px-4 py-1 rounded-full text-white font-medium text-sm shadow-sm transition-colors duration-500" style={{ backgroundColor: activeColor }}>
          {activeLabel}
        </span>
      </div>
    </div>
  );
}

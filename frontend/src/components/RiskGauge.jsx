import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';

const RiskGauge = ({ score }) => {
  // Normalize score between 0 and 100
  const normalizedScore = Math.min(Math.max(score, 0), 100);
  
  // Calculate stroke dasharray for the circular progress (circumference = 2 * pi * r)
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;
  
  let color = 'text-green-500';
  let bgColor = 'text-green-500/20';
  let Icon = ShieldCheck;
  let label = 'Safe';
  
  if (normalizedScore >= 50) {
    color = 'text-red-500';
    bgColor = 'text-red-500/20';
    Icon = ShieldAlert;
    label = 'Dangerous';
  } else if (normalizedScore >= 20) {
    color = 'text-yellow-500';
    bgColor = 'text-yellow-500/20';
    Icon = AlertTriangle;
    label = 'Suspicious';
  }

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
      <div className="relative w-48 h-48 flex items-center justify-center">
        {/* Background Circle */}
        <svg className="absolute w-full h-full transform -rotate-90">
          <circle
            cx="96"
            cy="96"
            r={radius}
            stroke="currentColor"
            strokeWidth="12"
            fill="transparent"
            className={`text-gray-200 dark:text-gray-700`}
          />
          {/* Progress Circle */}
          <motion.circle
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1, ease: "easeOut" }}
            cx="96"
            cy="96"
            r={radius}
            stroke="currentColor"
            strokeWidth="12"
            fill="transparent"
            strokeLinecap="round"
            style={{ strokeDasharray: circumference }}
            className={`${color} drop-shadow-md`}
          />
        </svg>
        
        {/* Center Content */}
        <div className="flex flex-col items-center justify-center absolute">
          <Icon className={`w-8 h-8 ${color} mb-1`} />
          <span className="text-4xl font-bold text-gray-800 dark:text-white">
            {normalizedScore}%
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">Risk</span>
        </div>
      </div>
      
      <div className={`mt-4 px-4 py-1.5 rounded-full text-sm font-semibold flex items-center gap-2 border ${color.replace('text-', 'bg-').replace('500', '100')} ${color.replace('text-', 'border-').replace('500', '200')} ${color} dark:bg-opacity-10 dark:border-opacity-20`}>
        {label}
      </div>
    </div>
  );
};

export default RiskGauge;

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

interface GameTimerProps {
  seconds: number;
  isRunning: boolean;
}

const GameTimer: React.FC<GameTimerProps> = ({ seconds, isRunning }) => {
  // Format time display
  const formatTime = (totalSeconds: number) => {
    const minutes = Math.floor(totalSeconds / 60);
    const secs = Math.floor(totalSeconds % 60);
    const milliseconds = Math.floor((totalSeconds % 1) * 100);
    
    return {
      minutes: minutes.toString().padStart(2, '0'),
      seconds: secs.toString().padStart(2, '0'),
      milliseconds: milliseconds.toString().padStart(2, '0')
    };
  };

  const time = formatTime(seconds);
  
  // Color based on time
  const getTimerColor = () => {
    if (seconds < 10) return 'from-green-400 to-green-600';
    if (seconds < 30) return 'from-yellow-400 to-yellow-600';
    if (seconds < 60) return 'from-orange-400 to-orange-600';
    return 'from-red-400 to-red-600';
  };

  // Pulse animation for urgency
  const shouldPulse = isRunning && seconds > 50;

  return (
    <motion.div
      animate={shouldPulse ? { scale: [1, 1.05, 1] } : {}}
      transition={{ duration: 1, repeat: Infinity }}
      className={`
        bg-gradient-to-r ${getTimerColor()} 
        rounded-xl p-4 shadow-lg min-w-[200px]
      `}
    >
      <div className="flex items-center justify-center gap-3">
        <Clock className="w-6 h-6 text-white" />
        <div className="flex items-baseline text-white font-mono">
          <span className="text-3xl font-bold">{time.minutes}</span>
          <span className="text-3xl font-bold animate-pulse">:</span>
          <span className="text-3xl font-bold">{time.seconds}</span>
          <span className="text-xl ml-1 opacity-75">.{time.milliseconds}</span>
        </div>
      </div>
      
      {/* Progress bar */}
      <div className="mt-2 h-1 bg-white/20 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-white/60"
          initial={{ width: '0%' }}
          animate={{ width: `${Math.min((seconds / 120) * 100, 100)}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
      
      {/* Status text */}
      <div className="text-center text-white/90 text-xs mt-1">
        {isRunning ? 'Tiempo corriendo...' : 'Detenido'}
      </div>
    </motion.div>
  );
};

export default GameTimer;
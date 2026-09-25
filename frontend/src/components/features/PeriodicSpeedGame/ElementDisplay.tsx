'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Atom, Info } from 'lucide-react';

interface Element {
  number: number;
  symbol: string;
  name: string;
  category?: string;
  atomic_mass?: number;
}

interface ElementDisplayProps {
  element: Element;
  showHint: boolean;
  hint: string | null;
}

const ElementDisplay: React.FC<ElementDisplayProps> = ({ element, showHint, hint }) => {
  return (
    <div className="flex flex-col gap-4">
      {/* Main Display */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-gray-700">
          <Search className="w-6 h-6" />
          <span className="text-lg font-semibold">Encuentra este elemento:</span>
        </div>
      </div>

      {/* Element Card */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 shadow-xl"
      >
        <div className="flex items-center justify-between gap-6">
          {/* Symbol and Number */}
          <div className="flex items-center gap-6">
            <motion.div
              initial={{ rotate: -10 }}
              animate={{ rotate: 0 }}
              transition={{ type: "spring", stiffness: 200 }}
              className="bg-white/20 backdrop-blur rounded-xl p-4"
            >
              <div className="text-center">
                <div className="text-5xl font-bold text-white">
                  {element.symbol}
                </div>
                <div className="text-sm text-white/80 mt-1">
                  Z = {element.number}
                </div>
              </div>
            </motion.div>

            {/* Name and Details */}
            <div className="text-white">
              <h2 className="text-3xl font-bold mb-2">
                {element.name}
              </h2>
              {element.category && (
                <div className="flex items-center gap-2 text-white/80">
                  <Atom className="w-4 h-4" />
                  <span className="capitalize text-sm">
                    {element.category}
                  </span>
                </div>
              )}
              {element.atomic_mass && (
                <div className="text-white/70 text-sm mt-1">
                  Masa atómica: {element.atomic_mass.toFixed(3)} u
                </div>
              )}
            </div>
          </div>

          {/* Visual Indicator */}
          <motion.div
            animate={{ 
              scale: [1, 1.2, 1],
              rotate: [0, 360]
            }}
            transition={{ 
              duration: 3,
              repeat: Infinity,
              repeatType: "reverse"
            }}
            className="hidden lg:block"
          >
            <div className="w-24 h-24 bg-white/10 rounded-full flex items-center justify-center">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                <div className="w-8 h-8 bg-white/30 rounded-full animate-pulse" />
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Hint Display */}
      <AnimatePresence>
        {showHint && hint && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-4"
          >
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div>
                <div className="font-semibold text-yellow-800 mb-1">
                  💡 Pista:
                </div>
                <div className="text-yellow-700">
                  {hint}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ElementDisplay;
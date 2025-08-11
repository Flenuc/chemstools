'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

interface Element {
  number: number;
  symbol: string;
  name: string;
  atomic_mass?: number;
  category?: string;
  xpos?: number;
  ypos?: number;
  wxpos?: number;
  wypos?: number;
}

interface PeriodicTableProps {
  elements: Element[];
  onElementClick: (elementNumber: number) => void;
  disabled?: boolean;
  targetElement?: Element | null;
}

const PeriodicTable: React.FC<PeriodicTableProps> = ({
  elements,
  onElementClick,
  disabled = false,
  targetElement
}) => {
  // Category colors
  const getCategoryColor = (category: string | undefined) => {
    if (!category) return 'from-gray-400 to-gray-500';
    
    const categoryColors: { [key: string]: string } = {
      'alkali metal': 'from-red-400 to-red-500',
      'alkaline earth metal': 'from-orange-400 to-orange-500',
      'transition metal': 'from-yellow-400 to-yellow-500',
      'post-transition metal': 'from-green-400 to-green-500',
      'metalloid': 'from-teal-400 to-teal-500',
      'diatomic nonmetal': 'from-blue-400 to-blue-500',
      'polyatomic nonmetal': 'from-indigo-400 to-indigo-500',
      'noble gas': 'from-purple-400 to-purple-500',
      'lanthanide': 'from-pink-400 to-pink-500',
      'actinide': 'from-rose-400 to-rose-500',
      'unknown': 'from-gray-400 to-gray-500'
    };

    for (const [key, color] of Object.entries(categoryColors)) {
      if (category.toLowerCase().includes(key)) {
        return color;
      }
    }
    return 'from-gray-400 to-gray-500';
  };

  // Create grid positions for elements
  const elementGrid = useMemo(() => {
    const grid: (Element | null)[][] = Array(10).fill(null).map(() => Array(18).fill(null));
    
    elements.forEach(element => {
      // Use standard positions or calculate from atomic number
      let row = element.ypos || 1;
      let col = element.xpos || 1;
      
      // Adjust for wide format if needed
      if (element.wypos !== undefined && element.wxpos !== undefined) {
        row = element.wypos;
        col = element.wxpos;
      }
      
      // Place element in grid (0-indexed)
      if (row > 0 && row <= 10 && col > 0 && col <= 18) {
        grid[row - 1][col - 1] = element;
      }
    });
    
    return grid;
  }, [elements]);

  // Render single element
  const renderElement = (element: Element | null, rowIndex: number, colIndex: number) => {
    if (!element) {
      // Empty cell
      return (
        <div
          key={`empty-${rowIndex}-${colIndex}`}
          className="aspect-square"
        />
      );
    }

    const isTarget = targetElement?.number === element.number;
    const categoryColor = getCategoryColor(element.category);

    return (
      <motion.button
        key={element.number}
        whileHover={!disabled ? { scale: 1.1, zIndex: 10 } : {}}
        whileTap={!disabled ? { scale: 0.95 } : {}}
        onClick={() => !disabled && onElementClick(element.number)}
        disabled={disabled}
        className={`
          relative aspect-square rounded-lg p-1 cursor-pointer
          bg-gradient-to-br ${categoryColor}
          shadow-md hover:shadow-xl transition-all duration-200
          ${disabled ? 'cursor-not-allowed opacity-50' : ''}
          ${isTarget ? 'ring-4 ring-yellow-400 ring-offset-2 animate-pulse' : ''}
        `}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ 
          delay: (rowIndex * 18 + colIndex) * 0.005,
          type: "spring",
          stiffness: 200
        }}
      >
        <div className="w-full h-full flex flex-col items-center justify-center text-white">
          <div className="text-[0.5rem] sm:text-xs font-bold opacity-90">
            {element.number}
          </div>
          <div className="text-sm sm:text-lg md:text-xl font-bold">
            {element.symbol}
          </div>
          <div className="text-[0.4rem] sm:text-[0.5rem] opacity-80 hidden sm:block truncate max-w-full px-1">
            {element.name}
          </div>
        </div>

        {/* Hover tooltip */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 10 }}
          whileHover={{ opacity: 1, scale: 1, y: 0 }}
          className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 
                     bg-gray-900 text-white p-2 rounded-lg text-xs whitespace-nowrap
                     pointer-events-none z-50 hidden lg:block"
        >
          <div className="font-bold">{element.name}</div>
          <div className="text-gray-300">
            {element.symbol} • Z={element.number}
          </div>
          {element.atomic_mass && (
            <div className="text-gray-400">
              Masa: {element.atomic_mass.toFixed(2)}
            </div>
          )}
          <div className="text-gray-400 capitalize">
            {element.category}
          </div>
        </motion.div>
      </motion.button>
    );
  };

  return (
    <div className="w-full overflow-x-auto">
      <div className="min-w-[900px] p-4">
        {/* Main periodic table grid */}
        <div className="grid grid-cols-18 gap-1 mb-4">
          {elementGrid.slice(0, 7).map((row, rowIndex) => (
            row.map((element, colIndex) => (
              <React.Fragment key={`cell-${rowIndex}-${colIndex}`}>
                {renderElement(element, rowIndex, colIndex)}
              </React.Fragment>
            ))
          ))}
        </div>

        {/* Lanthanides and Actinides (if present) */}
        {elementGrid[7] && elementGrid[7].some(e => e !== null) && (
          <>
            <div className="h-4" /> {/* Spacer */}
            <div className="grid grid-cols-18 gap-1 mb-2">
              {elementGrid[7].map((element, colIndex) => (
                <React.Fragment key={`lan-${colIndex}`}>
                  {colIndex < 3 && <div className="aspect-square" />}
                  {colIndex >= 3 && renderElement(element, 7, colIndex)}
                </React.Fragment>
              ))}
            </div>
          </>
        )}
        
        {elementGrid[8] && elementGrid[8].some(e => e !== null) && (
          <div className="grid grid-cols-18 gap-1">
            {elementGrid[8].map((element, colIndex) => (
              <React.Fragment key={`act-${colIndex}`}>
                {colIndex < 3 && <div className="aspect-square" />}
                {colIndex >= 3 && renderElement(element, 8, colIndex)}
              </React.Fragment>
            ))}
          </div>
        )}

        {/* Legend */}
        <div className="mt-6 flex flex-wrap gap-2 justify-center">
          <div className="flex items-center gap-2 text-xs">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-red-400 to-red-500" />
            <span>Metales alcalinos</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-orange-400 to-orange-500" />
            <span>Metales alcalinotérreos</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-yellow-400 to-yellow-500" />
            <span>Metales de transición</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-blue-400 to-blue-500" />
            <span>No metales</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-purple-400 to-purple-500" />
            <span>Gases nobles</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-pink-400 to-pink-500" />
            <span>Lantánidos</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-rose-400 to-rose-500" />
            <span>Actínidos</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PeriodicTable;
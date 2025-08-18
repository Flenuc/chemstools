'use client';
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, Badge, Typography, Tooltip, Spin } from 'antd';
import { useDispatch } from 'react-redux';
import { api } from '@/services/api';
import { setElementFilter } from '@/store/filterSlice';
import { AnimatedDiv, animations, staggerContainer, staggerItem } from '@/lib/animations';
import { cn } from '@/lib/utils';

const { Title, Text, Paragraph } = Typography;

interface ElementData {
  name: string;
  symbol: string;
  number: number;
  atomic_mass: number;
  category: string;
  xpos: number;
  ypos: number;
}

const categoryColors: { [key: string]: string } = {
  "diatomic nonmetal": "#0ea5e9",
  "noble gas": "#8b5cf6",
  "alkali metal": "#f59e0b",
  "alkaline earth metal": "#84cc16",
  "metalloid": "#06b6d4",
  "transition metal": "#ec4899",
  "post-transition metal": "#6366f1",
  "lanthanide": "#f97316",
  "actinide": "#ef4444",
  "unknown": "#6b7280"
};

const categoryGradients: { [key: string]: string } = {
  "diatomic nonmetal": "from-sky-400 to-sky-600",
  "noble gas": "from-violet-400 to-violet-600",
  "alkali metal": "from-amber-400 to-amber-600",
  "alkaline earth metal": "from-lime-400 to-lime-600",
  "metalloid": "from-cyan-400 to-cyan-600",
  "transition metal": "from-pink-400 to-pink-600",
  "post-transition metal": "from-indigo-400 to-indigo-600",
  "lanthanide": "from-orange-400 to-orange-600",
  "actinide": "from-red-400 to-red-600",
  "unknown": "from-gray-400 to-gray-600"
};

// Datos mock para desarrollo
const mockElements: ElementData[] = [
  { name: "Hydrogen", symbol: "H", number: 1, atomic_mass: 1.008, category: "diatomic nonmetal", xpos: 1, ypos: 1 },
  { name: "Helium", symbol: "He", number: 2, atomic_mass: 4.003, category: "noble gas", xpos: 18, ypos: 1 },
  { name: "Lithium", symbol: "Li", number: 3, atomic_mass: 6.941, category: "alkali metal", xpos: 1, ypos: 2 },
  { name: "Beryllium", symbol: "Be", number: 4, atomic_mass: 9.012, category: "alkaline earth metal", xpos: 2, ypos: 2 },
  { name: "Boron", symbol: "B", number: 5, atomic_mass: 10.811, category: "metalloid", xpos: 13, ypos: 2 },
  { name: "Carbon", symbol: "C", number: 6, atomic_mass: 12.011, category: "diatomic nonmetal", xpos: 14, ypos: 2 },
  { name: "Nitrogen", symbol: "N", number: 7, atomic_mass: 14.007, category: "diatomic nonmetal", xpos: 15, ypos: 2 },
  { name: "Oxygen", symbol: "O", number: 8, atomic_mass: 15.999, category: "diatomic nonmetal", xpos: 16, ypos: 2 },
  { name: "Fluorine", symbol: "F", number: 9, atomic_mass: 18.998, category: "diatomic nonmetal", xpos: 17, ypos: 2 },
  { name: "Neon", symbol: "Ne", number: 10, atomic_mass: 20.180, category: "noble gas", xpos: 18, ypos: 2 },
  { name: "Sodium", symbol: "Na", number: 11, atomic_mass: 22.990, category: "alkali metal", xpos: 1, ypos: 3 },
  { name: "Magnesium", symbol: "Mg", number: 12, atomic_mass: 24.305, category: "alkaline earth metal", xpos: 2, ypos: 3 },
  { name: "Aluminum", symbol: "Al", number: 13, atomic_mass: 26.982, category: "post-transition metal", xpos: 13, ypos: 3 },
  { name: "Silicon", symbol: "Si", number: 14, atomic_mass: 28.086, category: "metalloid", xpos: 14, ypos: 3 },
  { name: "Phosphorus", symbol: "P", number: 15, atomic_mass: 30.974, category: "diatomic nonmetal", xpos: 15, ypos: 3 },
  { name: "Sulfur", symbol: "S", number: 16, atomic_mass: 32.065, category: "diatomic nonmetal", xpos: 16, ypos: 3 },
  { name: "Chlorine", symbol: "Cl", number: 17, atomic_mass: 35.453, category: "diatomic nonmetal", xpos: 17, ypos: 3 },
  { name: "Argon", symbol: "Ar", number: 18, atomic_mass: 39.948, category: "noble gas", xpos: 18, ypos: 3 },
  { name: "Potassium", symbol: "K", number: 19, atomic_mass: 39.098, category: "alkali metal", xpos: 1, ypos: 4 },
  { name: "Calcium", symbol: "Ca", number: 20, atomic_mass: 40.078, category: "alkaline earth metal", xpos: 2, ypos: 4 },
  { name: "Iron", symbol: "Fe", number: 26, atomic_mass: 55.845, category: "transition metal", xpos: 8, ypos: 4 },
  { name: "Copper", symbol: "Cu", number: 29, atomic_mass: 63.546, category: "transition metal", xpos: 11, ypos: 4 },
  { name: "Zinc", symbol: "Zn", number: 30, atomic_mass: 65.380, category: "transition metal", xpos: 12, ypos: 4 },
  { name: "Gold", symbol: "Au", number: 79, atomic_mass: 196.967, category: "transition metal", xpos: 11, ypos: 6 },
  { name: "Silver", symbol: "Ag", number: 47, atomic_mass: 107.868, category: "transition metal", xpos: 11, ypos: 5 },
];

export default function PeriodicTableEnhanced() {
  const [elements, setElements] = useState<ElementData[]>([]);
  const [selectedElement, setSelectedElement] = useState<ElementData | null>(null);
  const [hoveredElement, setHoveredElement] = useState<ElementData | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'svg'>('grid');
  const svgRef = useRef<SVGSVGElement>(null);
  const dispatch = useDispatch();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await api.get('data/periodic-table/');
        setElements(data.elements);
      } catch (error) {
        console.error("Error fetching periodic table data:", error);
        // Usar datos mock si falla la API
        setElements(mockElements);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (viewMode === 'svg' && elements.length > 0 && svgRef.current) {
      renderSVGTable();
    }
  }, [elements, viewMode]);

  const renderSVGTable = () => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const cellSize = 50;
    const margin = 5;

    const elementGroups = svg.selectAll('g')
      .data(elements)
      .join('g')
      .attr('transform', d => `translate(${(d.xpos - 1) * (cellSize + margin)}, ${(d.ypos - 1) * (cellSize + margin)})`)
      .on('click', (event, d) => handleElementClick(d))
      .on('mouseenter', (event, d) => setHoveredElement(d))
      .on('mouseleave', () => setHoveredElement(null))
      .style('cursor', 'pointer');

    elementGroups.append('rect')
      .attr('width', cellSize)
      .attr('height', cellSize)
      .attr('fill', d => categoryColors[d.category] || categoryColors.unknown)
      .attr('stroke', '#1f2937')
      .attr('stroke-width', 1.5)
      .attr('rx', 6)
      .transition()
      .duration(300)
      .attr('opacity', 0)
      .transition()
      .delay((d, i) => i * 10)
      .duration(500)
      .attr('opacity', 1);

    elementGroups.append('text')
      .attr('x', cellSize / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .style('fill', 'white')
      .style('font-weight', '500')
      .text(d => d.number);

    elementGroups.append('text')
      .attr('x', cellSize / 2)
      .attr('y', 35)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .style('fill', 'white')
      .text(d => d.symbol);
  };

  const handleElementClick = (element: ElementData) => {
    setSelectedElement(element);
    dispatch(setElementFilter(element.symbol));
  };

  const ElementCard = ({ element }: { element: ElementData }) => {
    const gradientClass = categoryGradients[element.category] || categoryGradients.unknown;
    const isSelected = selectedElement?.symbol === element.symbol;
    const isHovered = hoveredElement?.symbol === element.symbol;

    return (
      <motion.div
        layout
        initial={{ scale: 0, opacity: 0 }}
        animate={{ 
          scale: isSelected ? 1.1 : 1, 
          opacity: 1,
          zIndex: isSelected ? 10 : 1
        }}
        whileHover={{ scale: 1.05, y: -2 }}
        whileTap={{ scale: 0.95 }}
        transition={{ duration: 0.2 }}
        className={cn(
          "relative cursor-pointer rounded-lg overflow-hidden",
          "shadow-md hover:shadow-xl transition-all duration-200",
          isSelected && "ring-4 ring-primary-500 ring-offset-2"
        )}
        onClick={() => handleElementClick(element)}
        onMouseEnter={() => setHoveredElement(element)}
        onMouseLeave={() => setHoveredElement(null)}
        style={{
          gridColumn: element.xpos,
          gridRow: element.ypos
        }}
      >
        <div className={cn(
          "w-full h-full p-2 bg-gradient-to-br",
          gradientClass,
          "flex flex-col items-center justify-center text-white"
        )}>
          <span className="text-xs font-medium">{element.number}</span>
          <span className="text-xl font-bold">{element.symbol}</span>
          <span className="text-[10px] opacity-90 truncate w-full text-center">
            {element.atomic_mass.toFixed(2)}
          </span>
        </div>
        
        {(isHovered || isSelected) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 bg-black/20 pointer-events-none"
          />
        )}
      </motion.div>
    );
  };

  if (loading) {
    return (
      <AnimatedDiv animation="fadeIn" className="flex items-center justify-center h-96">
        <Spin size="large" />
      </AnimatedDiv>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con controles */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
      >
        <div>
          <Title level={2} className="!mb-2">Tabla Periódica Interactiva</Title>
          <Text className="text-gray-600">
            Explora los elementos químicos con animaciones y detalles enriquecidos
          </Text>
        </div>
        
        <div className="flex gap-2">
          <Badge count={elements.length} showZero color="blue">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setViewMode(viewMode === 'grid' ? 'svg' : 'grid')}
              className={cn(
                "px-4 py-2 rounded-lg font-medium transition-colors",
                "bg-white border border-gray-300 hover:bg-gray-50"
              )}
            >
              Vista: {viewMode === 'grid' ? 'Cuadrícula' : 'SVG'}
            </motion.button>
          </Badge>
        </div>
      </motion.div>

      <div className="flex flex-col xl:flex-row gap-6">
        {/* Tabla periódica */}
        <AnimatedDiv 
          animation="fadeInLeft" 
          className="flex-grow"
        >
          <Card className="overflow-hidden">
            {viewMode === 'grid' ? (
              <div className="overflow-x-auto">
                <motion.div 
                  variants={staggerContainer}
                  initial="hidden"
                  animate="visible"
                  className="inline-grid gap-1 p-4"
                  style={{
                    gridTemplateColumns: 'repeat(18, 3rem)',
                    gridTemplateRows: 'repeat(10, 3rem)'
                  }}
                >
                  {elements.map((element, index) => (
                    <motion.div
                      key={element.symbol}
                      variants={staggerItem}
                      custom={index}
                    >
                      <ElementCard element={element} />
                    </motion.div>
                  ))}
                </motion.div>
              </div>
            ) : (
              <div className="overflow-x-auto p-4">
                <svg ref={svgRef} width={18 * 55} height={10 * 55} />
              </div>
            )}
          </Card>
        </AnimatedDiv>

        {/* Panel de detalles */}
        <AnimatedDiv 
          animation="fadeInRight"
          className="w-full xl:w-96"
        >
          <Card 
            className="sticky top-4"
            title="Detalles del Elemento"
            extra={
              selectedElement && (
                <Badge 
                  color={categoryColors[selectedElement.category] || '#6b7280'}
                  text={selectedElement.category}
                />
              )
            }
          >
            <AnimatePresence mode="wait">
              {selectedElement ? (
                <motion.div
                  key={selectedElement.symbol}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4"
                >
                  {/* Encabezado del elemento */}
                  <div className={cn(
                    "p-6 rounded-lg bg-gradient-to-br text-white text-center",
                    categoryGradients[selectedElement.category] || categoryGradients.unknown
                  )}>
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
                    >
                      <div className="text-6xl font-bold mb-2">
                        {selectedElement.symbol}
                      </div>
                      <div className="text-2xl font-medium">
                        {selectedElement.name}
                      </div>
                      <div className="text-lg opacity-90 mt-2">
                        Número Atómico: {selectedElement.number}
                      </div>
                    </motion.div>
                  </div>

                  {/* Detalles */}
                  <motion.div 
                    className="space-y-3"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <Text strong>Masa Atómica:</Text>
                      <Text className="text-lg">{selectedElement.atomic_mass.toFixed(4)} u</Text>
                    </div>
                    
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <Text strong>Categoría:</Text>
                      <Badge 
                        color={categoryColors[selectedElement.category] || '#6b7280'}
                        text={selectedElement.category}
                        className="!px-3 !py-1"
                      />
                    </div>

                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <Text strong>Posición:</Text>
                      <Text>Grupo {selectedElement.xpos}, Período {selectedElement.ypos}</Text>
                    </div>
                  </motion.div>

                  {/* Botones de acción */}
                  <motion.div
                    className="flex gap-2"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg font-medium hover:bg-primary-600 transition-colors"
                    >
                      Ver Compuestos
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                    >
                      Más Info
                    </motion.button>
                  </motion.div>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-12 text-gray-500"
                >
                  <div className="text-6xl mb-4">⚛️</div>
                  <Paragraph className="text-lg">
                    Haz clic en un elemento para ver sus detalles
                  </Paragraph>
                  <Text className="text-sm">
                    Puedes cambiar entre vista de cuadrícula y SVG
                  </Text>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>
        </AnimatedDiv>
      </div>

      {/* Leyenda de categorías */}
      <AnimatedDiv animation="fadeInUp" delay={0.5}>
        <Card title="Categorías de Elementos" size="small">
          <motion.div 
            className="flex flex-wrap gap-2"
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
          >
            {Object.entries(categoryColors).map(([category, color], index) => (
              <motion.div
                key={category}
                variants={staggerItem}
                custom={index}
                whileHover={{ scale: 1.05 }}
                className="flex items-center gap-2 px-3 py-1 bg-gray-50 rounded-full"
              >
                <div 
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: color }}
                />
                <Text className="text-sm capitalize">{category}</Text>
              </motion.div>
            ))}
          </motion.div>
        </Card>
      </AnimatedDiv>
    </div>
  );
}

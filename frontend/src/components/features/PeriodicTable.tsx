'use client';
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import apiService from '@/services/api';

// Definimos el tipo para un elemento químico
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
  "diatomic nonmetal": "#a8d5e5",
  "noble gas": "#c0b8e0",
  "alkali metal": "#f0c0a8",
  "alkaline earth metal": "#e0e0a8",
  "metalloid": "#c8e0a8",
};

export default function PeriodicTable() {
  const [elements, setElements] = useState<ElementData[]>([]);
  const [selectedElement, setSelectedElement] = useState<ElementData | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await apiService('data/periodic-table/');
        setElements(data.elements);
      } catch (error) {
        console.error("Error fetching periodic table data:", error);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (elements.length === 0 || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Limpiar SVG anterior

    const cellSize = 50;
    const margin = 5;

    const elementGroups = svg.selectAll('g')
      .data(elements)
      .join('g')
      .attr('transform', d => `translate(${(d.xpos - 1) * (cellSize + margin)}, ${(d.ypos - 1) * (cellSize + margin)})`)
      .on('click', (event, d) => setSelectedElement(d))
      .style('cursor', 'pointer');

    elementGroups.append('rect')
      .attr('width', cellSize)
      .attr('height', cellSize)
      .attr('fill', d => categoryColors[d.category] || '#cccccc')
      .attr('stroke', '#333')
      .attr('rx', 4);

    elementGroups.append('text')
      .attr('x', cellSize / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .text(d => d.number);

    elementGroups.append('text')
      .attr('x', cellSize / 2)
      .attr('y', 35)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text(d => d.symbol);

  }, [elements]);

  return (
    <div className="flex flex-col md:flex-row gap-4">
      <div className="flex-grow">
        <svg ref={svgRef} width="100%" height="500"></svg>
      </div>
      <div className="w-full md:w-1/3 p-4 border rounded-lg bg-white shadow-sm">
        <h3 className="text-lg font-semibold">Detalles del Elemento</h3>
        {selectedElement ? (
          <div className="space-y-2 mt-2">
            <p><strong>Nombre:</strong> {selectedElement.name}</p>
            <p><strong>Símbolo:</strong> {selectedElement.symbol}</p>
            <p><strong>Número Atómico:</strong> {selectedElement.number}</p>
            <p><strong>Masa Atómica:</strong> {selectedElement.atomic_mass.toFixed(3)}</p>
            <p><strong>Categoría:</strong> {selectedElement.category}</p>
          </div>
        ) : (
          <p className="mt-2 text-black-500">Haz clic en un elemento para ver sus detalles.</p>
        )}
      </div>
    </div>
  );
}
"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import { api } from '@/services/api';
import Card from '@/components/common/Card';
import Input from '@/components/common/Input';
import Header from '@/components/core/Header';

interface GlossaryTerm {
  id: number;
  term: string;
  definition: string;
}

const GlossaryPage = () => {
  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const token = useSelector((state: RootState) => state.auth.accessToken);

  useEffect(() => {
    const fetchTerms = async () => {
      if (!token) {
        setError("Autenticación requerida.");
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const responseData = await api.get('calculators/glossary/');
        if (Array.isArray(responseData)) {
          setTerms(responseData);
        } else {
          console.error("Unexpected data format from glossary API:", responseData);
          setError('Formato de datos inesperado del servidor.');
          setTerms([]);
        }
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Error al cargar el glosario.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTerms();
  }, [token]);

  const filteredTerms = useMemo(() => {
    if (!Array.isArray(terms)) return [];
    return terms.filter(term =>
      term.term.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [terms, searchTerm]);

  return (
    <div className="container mx-auto p-4 md:p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Glosario de Términos Químicos</h1>
        <Header />
      <div className="mb-6">
        <Input
          type="text"
          placeholder="Buscar término..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          aria-label="Buscar en el glosario"
        />
      </div>

      {loading && <p>Cargando términos...</p>}
      {error && <p className="text-red-500">{error}</p>}
      
      {!loading && !error && (
        <div className="space-y-4">
          {filteredTerms.length > 0 ? (
            filteredTerms.map(term => (
              <Card key={term.id} className="transition-shadow duration-300 hover:shadow-lg">
                <h2 className="text-xl font-semibold text-blue-700">{term.term}</h2>
                <p className="mt-2 text-gray-600">{term.definition}</p>
              </Card>
            ))
          ) : (
            <p>No se encontraron términos.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default GlossaryPage;
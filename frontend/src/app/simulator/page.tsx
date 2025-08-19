"use client";
   import { useSelector } from 'react-redux';
   import { RootState } from '@/store';
   import React from 'react';
   import ReactionSimulator from '@/components/features/ReactionSimulator';
   export default function SimulatorPage() {
       const { isAuthenticated } = useSelector((state: RootState) => state.auth);
       if (!isAuthenticated) {
           return (
               <div className="min-h-screen bg-gray-100 py-8">
                   <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
                       <div className="text-center">
                           <h2 className="text-2xl font-bold text-gray-800 mb-4">Acceso Requerido</h2>
                           <p className="text-gray-600 mb-6">Debes iniciar sesión para acceder al Simulador de Reacciones Químicas.</p>
                           <a
                               href="/"
                               className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition-colors"
                           >
                               Ir al Login
                           </a>
                       </div>
                   </div>
               </div>
           );
       }
       return (
           <div className="min-h-screen bg-gray-50">
               <div className="container mx-auto py-8">
                   <ReactionSimulator />
               </div>
           </div>
       );
   }
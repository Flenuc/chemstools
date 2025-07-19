import PeriodicTable from '@/components/features/PeriodicTable';
import Header from '@/components/core/Header'; 

export default function PeriodicTablePage() {
  return (
    <main className="flex min-h-screen flex-col items-center p-6 md:p-12 bg-slate-900 text-white">
      <Header /> 
      <div className="w-full max-w-5xl">
        <h1 className="text-3xl font-bold mb-4">Tabla Periódica Interactiva</h1>
        <PeriodicTable />
      </div>
    </main>
  );
}
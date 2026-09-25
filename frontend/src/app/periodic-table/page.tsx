import PeriodicTable from '@/components/features/PeriodicTableEnhanced';

export default function PeriodicTablePage() {
  return (
    <main className="flex min-h-screen flex-col items-center p-6 md:p-12">
      <div className="w-full max-w-5xl">
        
        <PeriodicTable />
      </div>
    </main>
  );
}
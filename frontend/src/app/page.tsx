import HealthCheck from "@/components/features/HealthCheck";
import MolecularWeightCalculator from "@/components/features/MolecularWeightCalculator";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center p-12 sm:p-24 bg-gray-50">
      <div className="z-10 w-full max-w-2xl items-center justify-between font-mono text-sm lg:flex mb-8">
        <h1 className="text-4xl font-bold text-gray-800 tracking-tight">
          ChemsTools
        </h1>
        <p className="text-gray-600">Pre-Alpha 0.0.3 - Prototipo Conceptual</p>
      </div>

      <div className="w-full max-w-2xl">
        <HealthCheck />
        <MolecularWeightCalculator />
      </div>

    </main>
  );
}

import LewisStructureGenerator from "@/components/features/LewisStructureGenerator";

export default function LewisPage() {
  return (
    <main className="flex min-h-screen flex-col items-center p-6 md:p-12">
      <div className="w-full max-w-5xl">
        <LewisStructureGenerator />
      </div>
    </main>
  );
}
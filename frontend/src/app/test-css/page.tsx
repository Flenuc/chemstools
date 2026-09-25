export default function TestCSS() {
  return (
    <div style={{ padding: '2rem' }}>
      <h1 className="text-4xl font-bold mb-4">Prueba de CSS</h1>
      
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-2">Estilos inline (deberían funcionar siempre):</h2>
        <div style={{ backgroundColor: '#f3f4f6', padding: '1rem', borderRadius: '0.5rem' }}>
          Este div usa estilos inline - fondo gris
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-2">Clases de Tailwind:</h2>
        <div className="bg-gray-100 p-4 rounded-lg">
          Este div usa bg-gray-100 de Tailwind
        </div>
        <div className="bg-blue-100 p-4 rounded-lg mt-2">
          Este div usa bg-blue-100 de Tailwind
        </div>
        <div className="bg-green-100 p-4 rounded-lg mt-2">
          Este div usa bg-green-100 de Tailwind
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-2">Colores con fallback:</h2>
        <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--color-gray-100, #f3f4f6)' }}>
          Este usa variable CSS con fallback
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-2">Utilidades de Tailwind:</h2>
        <div className="flex gap-4">
          <div className="w-24 h-24 bg-red-500 rounded"></div>
          <div className="w-24 h-24 bg-yellow-500 rounded"></div>
          <div className="w-24 h-24 bg-green-500 rounded"></div>
          <div className="w-24 h-24 bg-blue-500 rounded"></div>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-2">Gradientes:</h2>
        <div className="h-24 bg-gradient-to-r from-purple-400 to-pink-600 rounded-lg"></div>
      </div>

      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-2">Texto y tipografía:</h2>
        <p className="text-xs">Texto extra pequeño</p>
        <p className="text-sm">Texto pequeño</p>
        <p className="text-base">Texto base</p>
        <p className="text-lg">Texto grande</p>
        <p className="text-xl">Texto extra grande</p>
        <p className="text-2xl">Texto 2XL</p>
      </div>
    </div>
  );
}

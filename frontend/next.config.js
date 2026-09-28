/** @type {import('next').NextConfig} */

// Exportación estática (GitHub Pages): STATIC_EXPORT=true genera HTML/JS en `out/`.
// En ese modo no hay servidor de Next.js, así que no existen rewrites, middleware ni rutas /api;
// la app llama directamente al backend definido en NEXT_PUBLIC_API_URL.
const isStaticExport = process.env.STATIC_EXPORT === 'true';
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';

const nextConfig = {
  // Desactivar StrictMode temporalmente para evitar warnings de Ant Design
  // TODO: Reactivar cuando Ant Design sea compatible con React 18 StrictMode
  reactStrictMode: false,

  ...(isStaticExport
    ? {
        output: 'export',
        basePath,
        trailingSlash: true,
        images: { unoptimized: true },
      }
    : {
        async rewrites() {
          // Detectar si estamos en Docker o desarrollo local
          const isDocker = process.env.DOCKER_ENV === 'true';
          const backendUrl = isDocker ? 'http://backend:8000' : 'http://localhost:8000';

          return [
            // Manejar rutas con trailing slash
            {
              source: '/api/:path*/',
              destination: `${backendUrl}/api/:path*/`,
            },
            // Manejar rutas sin trailing slash
            {
              source: '/api/:path*',
              destination: `${backendUrl}/api/:path*`,
            },
            // Proxy para archivos media (exports, etc.)
            {
              source: '/media/:path*',
              destination: `${backendUrl}/media/:path*`,
            },
          ];
        },
        // Permitir trailing slashes sin redirección
        skipTrailingSlashRedirect: true,
      }),
};

module.exports = nextConfig;

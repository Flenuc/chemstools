/** @type {import('next').NextConfig} */
const nextConfig = {
  // Desactivar StrictMode temporalmente para evitar warnings de Ant Design
  // TODO: Reactivar cuando Ant Design sea compatible con React 18 StrictMode
  reactStrictMode: false,
  
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
};

module.exports = nextConfig;

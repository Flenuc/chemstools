'use client';

import React from 'react';

export default function UIDemoPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            ChemsTools UI System
          </h1>
          <p className="text-lg text-gray-600">
            Sistema de componentes híbrido con Ant Design, Tailwind CSS y Framer Motion
          </p>
        </div>

        <div className="grid gap-8">
          {/* Features Section */}
          <section className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold mb-6">✨ Características Implementadas</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="p-6 bg-blue-50 rounded-lg">
                <div className="text-3xl mb-3">🎨</div>
                <h3 className="font-semibold mb-2">Ant Design Integration</h3>
                <p className="text-gray-600">
                  Componentes profesionales con tema personalizado ChemsTools
                </p>
              </div>
              <div className="p-6 bg-green-50 rounded-lg">
                <div className="text-3xl mb-3">🎭</div>
                <h3 className="font-semibold mb-2">Framer Motion</h3>
                <p className="text-gray-600">
                  Animaciones fluidas y transiciones de página elegantes
                </p>
              </div>
              <div className="p-6 bg-purple-50 rounded-lg">
                <div className="text-3xl mb-3">🧩</div>
                <h3 className="font-semibold mb-2">Sistema Híbrido</h3>
                <p className="text-gray-600">
                  Combina lo mejor de Ant Design con utilities de Tailwind
                </p>
              </div>
            </div>
          </section>

          {/* Components Overview */}
          <section className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold mb-6">🧱 Componentes Disponibles</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold text-lg mb-3">UI Base</h3>
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Button (con variantes)
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Input & TextArea
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Card & Modal
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Alert & Notifications
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Badge, Tag & Tooltip
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-3">Layout</h3>
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Container (responsive)
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Flex & Grid
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Space & Divider
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Typography
                  </li>
                </ul>
              </div>
            </div>
          </section>

          {/* Animations */}
          <section className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold mb-6">🎬 Animaciones</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <h3 className="font-semibold mb-3">Básicas</h3>
                <ul className="text-sm space-y-1 text-gray-600">
                  <li>• fadeIn / fadeOut</li>
                  <li>• fadeInUp / fadeInDown</li>
                  <li>• fadeInLeft / fadeInRight</li>
                  <li>• scaleIn / scaleInBounce</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Avanzadas</h3>
                <ul className="text-sm space-y-1 text-gray-600">
                  <li>• slideIn (todas direcciones)</li>
                  <li>• rotateIn / flipIn</li>
                  <li>• morphIn</li>
                  <li>• stagger animations</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Loading States</h3>
                <ul className="text-sm space-y-1 text-gray-600">
                  <li>• SpinLoader</li>
                  <li>• DotsLoader</li>
                  <li>• PulseLoader</li>
                  <li>• Skeleton</li>
                </ul>
              </div>
            </div>
          </section>

          {/* File Structure */}
          <section className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold mb-6">📁 Estructura de Archivos</h2>
            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm">
              <pre>{`src/
├── theme/
│   └── antd-theme.ts        # Configuración del tema
├── components/
│   └── ui/
│       └── index.tsx         # Componentes híbridos
├── lib/
│   ├── animations.tsx        # Sistema de animaciones
│   └── utils.ts              # Utilidades (cn, etc)
└── app/
    ├── layout.tsx            # Layout principal
    └── ui-demo/
        └── page.tsx          # Esta página`}</pre>
            </div>
          </section>

          {/* Usage Example */}
          <section className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold mb-6">💻 Ejemplo de Uso</h2>
            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
              <pre className="text-sm">{`import { Button, Card, Container } from '@/components/ui';
import { AnimatedDiv, hoverScale } from '@/lib/animations';

export default function MyComponent() {
  return (
    <AnimatedDiv animation="fadeInUp">
      <Container maxWidth="xl">
        <Card variant="shadow">
          <motion.div {...hoverScale}>
            <Button variant="primary">
              Click Me!
            </Button>
          </motion.div>
        </Card>
      </Container>
    </AnimatedDiv>
  );
}`}</pre>
            </div>
          </section>

          {/* Status */}
          <section className="bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg shadow-lg p-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold mb-4">✅ Sistema Completado</h2>
              <p className="text-lg mb-6">
                El sistema de UI está listo para ser utilizado en toda la aplicación ChemsTools
              </p>
              <div className="flex justify-center gap-4 flex-wrap">
                <div className="bg-white/20 backdrop-blur rounded-lg px-4 py-2">
                  <span className="font-semibold">Ant Design</span> ✓
                </div>
                <div className="bg-white/20 backdrop-blur rounded-lg px-4 py-2">
                  <span className="font-semibold">Tailwind CSS</span> ✓
                </div>
                <div className="bg-white/20 backdrop-blur rounded-lg px-4 py-2">
                  <span className="font-semibold">Framer Motion</span> ✓
                </div>
                <div className="bg-white/20 backdrop-blur rounded-lg px-4 py-2">
                  <span className="font-semibold">TypeScript</span> ✓
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

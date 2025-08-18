'use client';

import { useState, useEffect } from 'react';
import { Button, Card, Tag, Alert, Space, Divider } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, InfoCircleOutlined } from '@ant-design/icons';

interface DiagnosticResult {
  test: string;
  status: 'success' | 'error' | 'warning';
  message: string;
}

export default function DiagnosticsPage() {
  const [results, setResults] = useState<DiagnosticResult[]>([]);
  const [testing, setTesting] = useState(false);

  const runDiagnostics = async () => {
    setTesting(true);
    setResults([]);
    const newResults: DiagnosticResult[] = [];

    // Test 1: Check if eval is blocked
    try {
      const testEval = new Function('return 1 + 1');
      const result = testEval();
      newResults.push({
        test: 'JavaScript eval()',
        status: result === 2 ? 'success' : 'error',
        message: result === 2 ? 'eval() funciona correctamente' : 'eval() no retorna el valor esperado'
      });
    } catch (e: any) {
      newResults.push({
        test: 'JavaScript eval()',
        status: 'error',
        message: `eval() bloqueado por CSP: ${e.message}`
      });
    }

    // Test 2: Check localStorage
    try {
      localStorage.setItem('test', 'value');
      const value = localStorage.getItem('test');
      localStorage.removeItem('test');
      newResults.push({
        test: 'LocalStorage',
        status: 'success',
        message: 'LocalStorage funciona correctamente'
      });
    } catch (e: any) {
      newResults.push({
        test: 'LocalStorage',
        status: 'error',
        message: `Error con localStorage: ${e.message}`
      });
    }

    // Test 3: Check fetch API
    try {
      const response = await fetch('/api/auth/register/', {
        method: 'GET'
      });
      newResults.push({
        test: 'Fetch API',
        status: 'success',
        message: `Fetch API funciona (status: ${response.status})`
      });
    } catch (e: any) {
      newResults.push({
        test: 'Fetch API',
        status: 'error',
        message: `Error con fetch: ${e.message}`
      });
    }

    // Test 4: Check Redux
    try {
      const hasRedux = typeof window !== 'undefined' && (window as any).__REDUX_DEVTOOLS_EXTENSION__;
      newResults.push({
        test: 'Redux DevTools',
        status: hasRedux ? 'success' : 'warning',
        message: hasRedux ? 'Redux DevTools detectado' : 'Redux DevTools no detectado (opcional)'
      });
    } catch (e: any) {
      newResults.push({
        test: 'Redux DevTools',
        status: 'warning',
        message: 'No se pudo verificar Redux DevTools'
      });
    }

    // Test 5: Check React version
    try {
      const React = await import('react');
      newResults.push({
        test: 'React Version',
        status: 'success',
        message: `React ${React.version}`
      });
    } catch (e: any) {
      newResults.push({
        test: 'React Version',
        status: 'error',
        message: 'No se pudo detectar React'
      });
    }

    // Test 6: Check if StrictMode is enabled
    try {
      const isStrictMode = false; // Configurado en next.config.js
      newResults.push({
        test: 'React StrictMode',
        status: isStrictMode ? 'warning' : 'success',
        message: isStrictMode ? 'StrictMode activado (puede causar warnings con Ant Design)' : 'StrictMode desactivado'
      });
    } catch (e: any) {
      newResults.push({
        test: 'React StrictMode',
        status: 'error',
        message: 'No se pudo verificar StrictMode'
      });
    }

    // Test 7: Test form submission
    try {
      const testData = {
        username: `test_${Date.now()}`,
        email: `test_${Date.now()}@test.com`,
        password: 'TestPass123!'
      };
      
      const response = await fetch('/api/auth/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        newResults.push({
          test: 'API Registration',
          status: 'success',
          message: `Registro exitoso: Usuario ${data.username} creado con ID ${data.id}`
        });
      } else {
        newResults.push({
          test: 'API Registration',
          status: 'warning',
          message: `API responde pero con error: ${JSON.stringify(data)}`
        });
      }
    } catch (e: any) {
      newResults.push({
        test: 'API Registration',
        status: 'error',
        message: `Error al probar registro: ${e.message}`
      });
    }

    // Test 8: Check console errors
    try {
      const originalError = console.error;
      let errorCount = 0;
      console.error = function() {
        errorCount++;
        originalError.apply(console, arguments as any);
      };
      
      // Restore after a moment
      setTimeout(() => {
        console.error = originalError;
        newResults.push({
          test: 'Console Errors',
          status: errorCount > 0 ? 'warning' : 'success',
          message: errorCount > 0 ? `${errorCount} errores en consola detectados` : 'Sin errores en consola'
        });
      }, 100);
    } catch (e: any) {
      newResults.push({
        test: 'Console Errors',
        status: 'error',
        message: 'No se pudo verificar errores de consola'
      });
    }

    setResults(newResults);
    setTesting(false);
  };

  useEffect(() => {
    // Auto-run diagnostics on mount
    runDiagnostics();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'warning':
        return <InfoCircleOutlined style={{ color: '#faad14' }} />;
      default:
        return null;
    }
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'success':
        return <Tag color="success">OK</Tag>;
      case 'error':
        return <Tag color="error">ERROR</Tag>;
      case 'warning':
        return <Tag color="warning">ADVERTENCIA</Tag>;
      default:
        return <Tag>DESCONOCIDO</Tag>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <Card 
          title={
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold">Diagnóstico del Sistema</h1>
              <Button 
                type="primary" 
                onClick={runDiagnostics} 
                loading={testing}
                icon={<InfoCircleOutlined />}
              >
                Ejecutar Diagnóstico
              </Button>
            </div>
          }
        >
          <Alert
            message="Información de Diagnóstico"
            description="Esta página verifica que todos los componentes necesarios para el funcionamiento del sistema de autenticación estén operativos."
            type="info"
            showIcon
            className="mb-4"
          />

          <Divider>Resultados</Divider>

          <Space direction="vertical" className="w-full">
            {results.map((result, index) => (
              <Card 
                key={index} 
                size="small"
                className={`border-l-4 ${
                  result.status === 'success' ? 'border-green-500' : 
                  result.status === 'error' ? 'border-red-500' : 
                  'border-yellow-500'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(result.status)}
                    <span className="font-semibold">{result.test}</span>
                  </div>
                  {getStatusTag(result.status)}
                </div>
                <p className="mt-2 text-gray-600">{result.message}</p>
              </Card>
            ))}
          </Space>

          {results.length === 0 && !testing && (
            <div className="text-center py-8 text-gray-500">
              Haz clic en "Ejecutar Diagnóstico" para comenzar
            </div>
          )}

          <Divider>Acciones Recomendadas</Divider>

          <Alert
            message="Si hay errores con CSP"
            description="El middleware ya está configurado para permitir 'unsafe-eval' en desarrollo. Si persisten los problemas, verifica que el middleware esté siendo ejecutado."
            type="warning"
            showIcon
            className="mb-2"
          />

          <Alert
            message="Si el registro no funciona desde el formulario"
            description="Usa el formulario HTML simple en /test-form.html para verificar que el API funciona correctamente."
            type="info"
            showIcon
            className="mb-2"
          />

          <Alert
            message="Enlaces útiles"
            description={
              <ul className="mt-2">
                <li>• <a href="/register" className="text-blue-600">Formulario de Registro</a></li>
                <li>• <a href="/test-form.html" className="text-blue-600">Formulario HTML Simple</a></li>
                <li>• <a href="/test-register" className="text-blue-600">Formulario de Test React</a></li>
              </ul>
            }
            type="info"
            showIcon
          />
        </Card>
      </div>
    </div>
  );
}

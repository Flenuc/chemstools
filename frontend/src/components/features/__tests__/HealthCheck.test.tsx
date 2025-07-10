import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import HealthCheck from '../HealthCheck';

// Mock de la función fetch para evitar llamadas de red reales durante la prueba
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ status: 'ok' }),
  })
) as jest.Mock;

describe('HealthCheck Component', () => {
  // Limpiamos los mocks después de cada prueba
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('debería renderizar el estado inicial y luego actualizar a Online', async () => {
    render(<HealthCheck />);

    // Verifica que el título se renderiza
    expect(screen.getByText('Estado del Sistema')).toBeInTheDocument();

    // Verifica que inicialmente muestra el estado "Verificando..."
    expect(screen.getByText('Verificando...')).toBeInTheDocument();

    // --- CORRECCIÓN ---
    // Usamos waitFor para esperar a que la actualización de estado asíncrona ocurra
    // y el DOM se actualice al estado "Online".
    await waitFor(() => {
      expect(screen.getByText('Online')).toBeInTheDocument();
    });

    // Verificamos que el estado pendiente ya no está presente
    expect(screen.queryByText('Verificando...')).not.toBeInTheDocument();
  });

  it('debería mostrar el estado "Offline" después de un error en la respuesta', async () => {
    // Sobrescribimos el mock de fetch para simular un error
    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      Promise.resolve({ ok: false })
    );

    render(<HealthCheck />);

    // Espera a que aparezca el estado de error
    await waitFor(() => {
      expect(screen.getByText('Offline')).toBeInTheDocument();
    });
  });
});


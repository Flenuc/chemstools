import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Provider } from 'react-redux';
import { store } from '@/store';
import MolarMassCalculator from '../MolarMassCalculator';

// Mock del servicio de API
jest.mock('@/services/api', () => ({
  __esModule: true,
  default: jest.fn(),
}));
import apiService from '@/services/api';
const mockedApiService = apiService as jest.Mock;

describe('MolarMassCalculator', () => {
  it('calcula y muestra la masa molar correctamente', async () => {
    mockedApiService.mockResolvedValue({ molecular_weight: 18.015 });

    render(
      <Provider store={store}>
        <MolarMassCalculator />
      </Provider>
    );

    const input = screen.getByLabelText(/Fórmula Química/i);
    const button = screen.getByRole('button', { name: /Calcular/i });

    fireEvent.change(input, { target: { value: 'H2O' } });
    fireEvent.click(button);

    // Espera a que aparezca el resultado
    await waitFor(() => {
      expect(screen.getByText(/18.0150 g\/mol/i)).toBeInTheDocument();
    });
  });
});

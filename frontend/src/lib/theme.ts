import type { ThemeConfig } from 'antd';

export const theme: ThemeConfig = {
  token: {
    // Colores principales
    colorPrimary: '#6366f1',
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',
    colorInfo: '#3b82f6',
    
    // Tipografía
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: 14,
    
    // Bordes y esquinas
    borderRadius: 8,
    
    // Sombras
    boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    boxShadowSecondary: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  },
  components: {
    Button: {
      controlHeight: 40,
      fontSize: 14,
      borderRadius: 8,
    },
    Input: {
      controlHeight: 40,
      fontSize: 14,
      borderRadius: 8,
    },
    Form: {
      labelFontSize: 14,
      verticalLabelPadding: '0 0 8px',
    },
    Alert: {
      borderRadiusLG: 12,
    },
  },
};

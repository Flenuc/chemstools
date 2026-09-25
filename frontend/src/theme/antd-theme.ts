import type { ThemeConfig } from 'antd';

// ChemsTools Brand Colors
export const brandColors = {
  primary: '#1890ff',      // Chemical blue
  secondary: '#52c41a',    // Success green (for valid compounds)
  tertiary: '#722ed1',     // Purple (for special features)
  error: '#f5222d',        // Error red
  warning: '#faad14',      // Warning yellow
  info: '#13c2c2',        // Info cyan
  success: '#52c41a',     // Success green
  
  // Neutrals
  gray: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#e8e8e8',
    300: '#d9d9d9',
    400: '#bfbfbf',
    500: '#8c8c8c',
    600: '#595959',
    700: '#434343',
    800: '#262626',
    900: '#1f1f1f',
  },
  
  // Background colors
  bgPrimary: '#ffffff',
  bgSecondary: '#fafafa',
  bgTertiary: '#f5f5f5',
  
  // Text colors
  textPrimary: 'rgba(0, 0, 0, 0.85)',
  textSecondary: 'rgba(0, 0, 0, 0.65)',
  textTertiary: 'rgba(0, 0, 0, 0.45)',
  textDisabled: 'rgba(0, 0, 0, 0.25)',
};

// Design Tokens
export const designTokens = {
  borderRadius: {
    xs: '2px',
    sm: '4px',
    base: '6px',
    lg: '8px',
    xl: '12px',
    '2xl': '16px',
    pill: '9999px',
  },
  
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    base: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
    '3xl': '64px',
  },
  
  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
    '4xl': '36px',
  },
  
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  
  animation: {
    duration: {
      fast: '0.15s',
      base: '0.3s',
      slow: '0.45s',
      slower: '0.6s',
    },
    easing: {
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
  },
  
  shadow: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  },
};

// Ant Design Theme Configuration
export const antdTheme: ThemeConfig = {
  token: {
    // Brand colors
    colorPrimary: brandColors.primary,
    colorSuccess: brandColors.success,
    colorWarning: brandColors.warning,
    colorError: brandColors.error,
    colorInfo: brandColors.info,
    
    // Typography
    fontSize: 16,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    
    // Layout
    borderRadius: 6,
    boxShadow: designTokens.shadow.base,
    
    // Motion
    motionDurationFast: '0.1s',
    motionDurationMid: '0.2s',
    motionDurationSlow: '0.3s',
    
    // Component specific
    controlHeight: 40,
    controlHeightSM: 32,
    controlHeightLG: 48,
  },
  
  components: {
    Button: {
      primaryShadow: designTokens.shadow.md,
      borderRadius: 6,
      fontWeight: 500,
    },
    
    Input: {
      borderRadius: 6,
      controlHeight: 40,
    },
    
    Card: {
      borderRadius: 12,
      boxShadow: designTokens.shadow.base,
    },
    
    Modal: {
      borderRadius: 12,
    },
    
    Message: {
      borderRadius: 6,
    },
    
    Notification: {
      borderRadius: 8,
    },
    
    Table: {
      borderRadius: 8,
    },
    
    Tabs: {
      itemActiveColor: brandColors.primary,
      itemHoverColor: brandColors.primary,
      inkBarColor: brandColors.primary,
    },
    
    Menu: {
      itemBorderRadius: 6,
      subMenuItemBorderRadius: 6,
    },
  },
  
  algorithm: undefined, // Can be set to theme.darkAlgorithm for dark mode
};

// CSS Variables for Tailwind integration
export const cssVariables = `
  :root {
    /* Brand Colors */
    --color-primary: ${brandColors.primary};
    --color-secondary: ${brandColors.secondary};
    --color-tertiary: ${brandColors.tertiary};
    --color-success: ${brandColors.success};
    --color-warning: ${brandColors.warning};
    --color-error: ${brandColors.error};
    --color-info: ${brandColors.info};
    
    /* Gray Scale */
    --color-gray-50: ${brandColors.gray[50]};
    --color-gray-100: ${brandColors.gray[100]};
    --color-gray-200: ${brandColors.gray[200]};
    --color-gray-300: ${brandColors.gray[300]};
    --color-gray-400: ${brandColors.gray[400]};
    --color-gray-500: ${brandColors.gray[500]};
    --color-gray-600: ${brandColors.gray[600]};
    --color-gray-700: ${brandColors.gray[700]};
    --color-gray-800: ${brandColors.gray[800]};
    --color-gray-900: ${brandColors.gray[900]};
    
    /* Spacing */
    --spacing-xs: ${designTokens.spacing.xs};
    --spacing-sm: ${designTokens.spacing.sm};
    --spacing-md: ${designTokens.spacing.md};
    --spacing-base: ${designTokens.spacing.base};
    --spacing-lg: ${designTokens.spacing.lg};
    --spacing-xl: ${designTokens.spacing.xl};
    --spacing-2xl: ${designTokens.spacing['2xl']};
    --spacing-3xl: ${designTokens.spacing['3xl']};
    
    /* Border Radius */
    --radius-xs: ${designTokens.borderRadius.xs};
    --radius-sm: ${designTokens.borderRadius.sm};
    --radius-base: ${designTokens.borderRadius.base};
    --radius-lg: ${designTokens.borderRadius.lg};
    --radius-xl: ${designTokens.borderRadius.xl};
    --radius-2xl: ${designTokens.borderRadius['2xl']};
    --radius-pill: ${designTokens.borderRadius.pill};
    
    /* Animation */
    --duration-fast: ${designTokens.animation.duration.fast};
    --duration-base: ${designTokens.animation.duration.base};
    --duration-slow: ${designTokens.animation.duration.slow};
    --duration-slower: ${designTokens.animation.duration.slower};
    
    --easing-in: ${designTokens.animation.easing.easeIn};
    --easing-out: ${designTokens.animation.easing.easeOut};
    --easing-in-out: ${designTokens.animation.easing.easeInOut};
    --easing-bounce: ${designTokens.animation.easing.bounce};
  }
`;

export default antdTheme;

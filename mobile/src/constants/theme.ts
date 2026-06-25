/**
 * App Theme Configuration
 */
import {MD3LightTheme} from 'react-native-paper';

export const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#0f766e', // Teal
    secondary: '#3b82f6', // Blue
    tertiary: '#78350f', // Brown
    background: '#ffffff',
    surface: '#f8f9fa',
    error: '#dc2626',
    success: '#16a34a',
    warning: '#ea580c',
    info: '#0284c7',
    text: '#1f2937',
    textSecondary: '#6b7280',
    border: '#e5e7eb',
  },
  roundness: 12,
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  typography: {
    h1: {
      fontSize: 32,
      fontWeight: '700',
      lineHeight: 40,
    },
    h2: {
      fontSize: 24,
      fontWeight: '600',
      lineHeight: 32,
    },
    h3: {
      fontSize: 20,
      fontWeight: '600',
      lineHeight: 28,
    },
    body: {
      fontSize: 16,
      fontWeight: '400',
      lineHeight: 24,
    },
    caption: {
      fontSize: 14,
      fontWeight: '400',
      lineHeight: 20,
    },
  },
};

export const COLORS = theme.colors;
export const SPACING = theme.spacing;
export const TYPOGRAPHY = theme.typography;

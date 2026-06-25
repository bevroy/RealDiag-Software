/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,jsx,ts,tsx}',
    './app/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
  ],
  corePlugins: {
    // Disable preflight so existing inline-styled pages are unaffected.
    preflight: false,
  },
  theme: {
    extend: {
      // Brand palette mirrors realdiag.org (teal accent + slate neutrals).
      colors: {
        brand: {
          50:  '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
          DEFAULT: '#0f766e',
        },
        ink: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
      },
      // Poppins, mirrors elionyx.com.
      fontFamily: {
        sans: [
          'Poppins',
          'system-ui',
          '-apple-system',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        pill: '9999px',
      },
      boxShadow: {
        brand: '0 4px 12px rgba(15, 118, 110, 0.18)',
        card:  '0 10px 30px rgba(15, 23, 42, 0.10)',
      },
      backgroundImage: {
        'brand-cta':  'linear-gradient(135deg, #14b8a6 0%, #0f766e 100%)',
        'brand-hero': 'linear-gradient(135deg, #0f172a 0%, #0f766e 100%)',
        'brand-page': 'linear-gradient(135deg, #f0fdfa 0%, #e7f5f3 50%, #f8fafc 100%)',
      },
    },
  },
  plugins: [],
};

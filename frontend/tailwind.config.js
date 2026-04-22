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
    extend: {},
  },
  plugins: [],
};

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'nhaa-navy': '#1e293b',
        'nhaa-blue': '#3b82f6',
        'nhaa-dark': '#0f172a',
        'risk-low': '#22c55e',
        'risk-moderate': '#eab308',
        'risk-high': '#ef4444',
        'risk-critical': '#1e1b4b',
      },
    },
  },
  plugins: [],
}

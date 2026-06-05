/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        gold: {
          DEFAULT: '#C9A84C',
          light:   '#E2C878',
          dark:    '#A8893A',
          muted:   'rgba(201,168,76,0.15)',
        },
        surface: {
          DEFAULT: '#111111',
          2:       '#1A1A1A',
          3:       '#222222',
        },
        border: {
          DEFAULT: '#2A2A2A',
          light:   '#333333',
        },
      },
    },
  },
  plugins: [],
}

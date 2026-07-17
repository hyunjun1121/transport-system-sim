/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#1c2127',
          800: '#252a31',
          700: '#2f343c',
          600: '#3a4048',
        },
        palantir: {
          blue: '#137cbd',
          cyan: '#14b8a6',
          border: '#3a4048',
        }
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
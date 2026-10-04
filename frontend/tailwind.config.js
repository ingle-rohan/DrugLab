/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
        primary: {
          DEFAULT: "#2563eb",
          foreground: "#ffffff",
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        navy: {
          800: '#0f172a',
          900: '#0a1120',
          950: '#060a13',
        },
        sidebar: {
          DEFAULT: '#091122',
          active: '#1e3a8a',
          hover: '#0f1f3d',
        }
      },
    },
  },
  plugins: [],
}

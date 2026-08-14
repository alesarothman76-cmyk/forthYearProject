/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          900: "#132024",
          700: "#2B3D42",
          500: "#5B7176",
          300: "#9CB0B4",
          100: "#DCE6E8",
        },
        clinical: {
          950: "#0A2F33",
          800: "#0F4A50",
          600: "#166B72",
          500: "#1B818A",
          400: "#3FA0A8",
          200: "#B7DBDE",
          100: "#E4F2F3",
        },
        severity: {
          healthy: "#2F7D5B",
          mild: "#C68A1E",
          moderate: "#C2650A",
          severe: "#B0301F",
        },
        canvas: "#F6F8F7",
      },
      fontFamily: {
        sans: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
}

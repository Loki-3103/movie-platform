/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0F172A",
        surface: "#1E293B",
        accent: "#FACC15",
        "accent-dark": "#EAB308",
        border: "#334155",
        muted: "#94A3B8",
        danger: "#F87171",
        success: "#4ADE80",
      },
    },
  },
  plugins: [],
};

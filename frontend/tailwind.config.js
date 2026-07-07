/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        mono: ["JetBrains Mono", "Consolas", "Menlo", "monospace"],
      },
      colors: {
        console: {
          bg: "#10110f",
          panel: "#171914",
          rail: "#23261f",
          edge: "#3b4036",
          text: "#d8dccf",
          muted: "#8f9984",
          green: "#9ccc65",
          amber: "#d8b35f",
          red: "#e57373",
        },
      },
    },
  },
  plugins: [],
};

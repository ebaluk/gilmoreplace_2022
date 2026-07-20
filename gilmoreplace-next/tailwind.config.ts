import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      screens: {
        md: "768px",
        lg: "1024px",
        xl: "1200px",
        "2xl": "1440px",
      },
      colors: {
        brand: {
          gold: "#C5A572",
          "gold-light": "#D4BC8A",
          "gold-dark": "#A8894E",
          charcoal: "#2C2C2C",
          "charcoal-light": "#4A4A4A",
          offwhite: "#F5F3EF",
          cream: "#FAF8F5",
        },
      },
      fontFamily: {
        gotham: ["Gotham", "sans-serif"],
        bailey: ["Bailey Sans ITC", "sans-serif"],
        cinzel: ["Cinzel", "serif"],
        helvetica: ["Helvetica", "Arial", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in-out",
        "slide-up": "slideUp 0.5s ease-out",
        "scroll-down": "scrollDown 2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        scrollDown: {
          "0%, 100%": { transform: "translateY(0)", opacity: "1" },
          "50%": { transform: "translateY(8px)", opacity: "0.5" },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;

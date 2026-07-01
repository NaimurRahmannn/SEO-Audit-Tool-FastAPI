import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Semantic tokens backed by CSS variables (see app/globals.css).
        primary: {
          DEFAULT: "var(--color-primary)",
          soft: "var(--color-primary-soft)",
          ink: "var(--color-primary-ink)",
        },
        pass: {
          DEFAULT: "var(--color-pass)",
          bg: "var(--color-pass-bg)",
          ink: "var(--color-pass-ink)",
        },
        warn: {
          DEFAULT: "var(--color-warn)",
          bg: "var(--color-warn-bg)",
          ink: "var(--color-warn-ink)",
        },
        fail: {
          DEFAULT: "var(--color-fail)",
          bg: "var(--color-fail-bg)",
          ink: "var(--color-fail-ink)",
        },
        canvas: "var(--color-bg)",
        surface: "var(--color-surface)",
        soft: "var(--color-soft)",
        line: "var(--color-line)",
        ink: {
          DEFAULT: "var(--color-ink)",
          2: "var(--color-ink-2)",
          3: "var(--color-ink-3)",
        },
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};

export default config;

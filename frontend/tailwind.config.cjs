const defaultTheme = require('tailwindcss/defaultTheme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  safelist: [
    // some classes are assigned dynamically, so tailwind doesn't find them at build time
    {
      pattern: /row-start-\d+/,
    }
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter var', ...defaultTheme.fontFamily.sans],
        serif: ['David Libre', ...defaultTheme.fontFamily.sans],
      },
      gridTemplateRows: {
        '15': 'repeat(15, minmax(0, 1fr))',
      },
      gridRowStart: Object.fromEntries(
        [...Array(8).keys()].map(i => i + 8).map(i => [`${i}`, `${i}`])
      ),
    },
  },
  plugins: [],
}
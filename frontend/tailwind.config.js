/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        darkSlate: '#0D1117',
        techBorder: '#1F2937',
        glowGreen: '#2ECC71',
        glowYellow: '#F1C40F',
        glowRed: '#E74C3C',
        glowBlue: '#3498DB'
      },
      boxShadow: {
        glow: '0 0 15px rgba(46, 204, 113, 0.2)',
        glowRed: '0 0 15px rgba(231, 76, 60, 0.2)',
        glowYellow: '0 0 15px rgba(241, 196, 15, 0.2)',
        glowBlue: '0 0 15px rgba(52, 152, 219, 0.2)'
      }
    },
  },
  plugins: [],
}

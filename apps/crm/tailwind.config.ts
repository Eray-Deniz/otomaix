import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        sidebar: {
          bg: '#1a1a2e',
          hover: '#16213e',
          active: '#0f3460',
          text: '#a8b2d8',
          'text-active': '#ffffff',
          border: '#2a2a4a',
        },
      },
    },
  },
  plugins: [],
}

export default config

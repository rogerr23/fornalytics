import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // In development, /api goes to the FastAPI backend, so no CORS is needed.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})

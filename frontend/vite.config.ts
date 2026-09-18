import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/articles': 'http://127.0.0.1:8000',
      '/swipes': 'http://127.0.0.1:8000',
      '/wiki': 'http://127.0.0.1:8000',
    },
  },
})

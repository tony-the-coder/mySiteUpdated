// vite.config.js
import path from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: "/static/",
  build: {
    manifest: "manifest.json",
    outDir: path.join(path.dirname(__dirname), "myproject", "assets"),
    rollupOptions: {
      input: {
        main: path.resolve('./src/main.jsx'),
      }
    }
  }
})



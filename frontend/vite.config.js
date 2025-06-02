// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  base: '/static/', // Matches Django's STATIC_URL
  build: {
    // Output to a 'dist' subdirectory INSIDE your Django app's static folder
    // or a project-level static folder's 'dist' subdirectory.
    // This example assumes DJANGO_VITE_ASSETS_PATH is BASE_DIR / "static" / "dist"
    // and this vite.config.js is in BASE_DIR / "frontend" /
    outDir: path.resolve(__dirname, '../static/dist'),
    assetsDir: '', // Assets will be directly in outDir (e.g., static/dist/main.js)
    manifest: true, // Crucial: Generates manifest.json for django-vite
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/main.jsx'), // Your React entry point
      },
    },
  },
})
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path';

export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production';
  return {
    root: "src",
    plugins: [
      react(),
      tailwindcss(),
    ],
    optimizeDeps: {
      include: ['clsx'],
    },
    base: isProduction ? "/static/vite/" : "/static/",
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    build: {
      manifest: "manifest.json",
      outDir: path.resolve(__dirname, "..", "assets", "vite"),
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, "src", "main.tsx"),
          aboutPageEntry: path.resolve(__dirname, "src", "aboutPageEntry.tsx"), // <-- ADD THIS LINE
          // Add other specific page entry points here as needed
        }
      }
    }
  }
});
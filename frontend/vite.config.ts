// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig(({ command }) => ({
  plugins: [
    react(),
  ],
  base: command === 'build' ? '/static/' : '/vite/',
  build: {
    outDir: path.resolve(__dirname, '../static/dist'),
    assetsDir: '',
    manifest: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/main.tsx'),
      },
    },
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    strictPort: true,
    cors: true,
    origin: 'http://localhost:5173',
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5173,
    }
  },
  resolve: {
    alias: {
      // '@': path.resolve(__dirname, 'src'),
    }
  }
}));
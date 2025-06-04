// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [
    react()
  ],
  // root: process.cwd(), // Default is the directory of the config file, which is 'frontend/'
  base: '/static/', // This MUST match Django's STATIC_URL

  server: {
    // The host Vite binds to. 'localhost' is usually fine.
    host: 'localhost',
    port: 5173, // Default Vite port
    strictPort: true, // Ensures Vite uses this port or fails
    origin: 'http://localhost:5173', // Helps client construct absolute URLs

    hmr: {
      // Explicitly set the host for HMR WebSocket connections.
      // This should match the host your browser uses to access the Vite dev server.
      host: 'localhost',
      port: 5173, // Ensure this matches the server port
      // protocol: 'ws', // Default is 'ws' or 'wss' based on server protocol
      // clientPort: 5173, // Default is server.port, explicitly setting can sometimes help
    }
  },

  build: {
    outDir: path.resolve(__dirname, '../static/dist'),
    assetsDir: '',
    manifest: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/main.tsx'),
      },
    },
  },

  resolve: {
    alias: {
      // '@': path.resolve(__dirname, 'src'),
    }
  }
})

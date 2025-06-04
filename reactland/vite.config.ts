/// <reference types="node" />
import * as path from "path";
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  root: "src",
  plugins: [react()],
  base: "/static/",
  build: {
    manifest: "manifest.json",
    outDir: path.join(path.dirname(__dirname), "mySite", "assets", "src"),
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "src", "main.tsx"),
      }
    }
  }
})
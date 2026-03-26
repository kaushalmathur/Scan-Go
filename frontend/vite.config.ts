import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// vite-plugin-pwa@1.2.0 does not yet support vite@8 — re-enable once upstream issue is resolved
// import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    // VitePWA({ registerType: 'autoUpdate' }) — temporarily disabled
  ],
  build: {
    chunkSizeWarningLimit: 2000,
  }
});

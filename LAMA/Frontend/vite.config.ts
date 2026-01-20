import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
        proxy: {
          '/classify': { target: env.VITE_ROUTER_URL || 'http://localhost:8001', changeOrigin: true },
          '/agent1': { target: env.VITE_ROUTER_URL || 'http://localhost:8001', changeOrigin: true },
          '/agent2': { target: env.VITE_ROUTER_URL || 'http://localhost:8001', changeOrigin: true },
          '/speech-to-text': { target: env.VITE_AGENT1_URL || 'http://localhost:8000', changeOrigin: true },
        }
      },
      plugins: [react()],
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
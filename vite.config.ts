import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080, // Change to 8080 for crestora-hub frontend, or 8081 for zyra-vision-shop
    watch: {
      // Ignore irrelevant or heavy directories/files: backend, python environments, etc.
      ignored: [
        '**/backend/**',
        '**/myvenv*/**',
        '**/venv*/**',
        '**/.venv*/**',
        '**/__pycache__/**',
        '**/node_modules/**',
        '**/dist/**',
        '**/.git/**',
        '**/artifacts/**',
        '**/*.pyc',
      ],
    }
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Optimize dependencies to reduce file watching
  optimizeDeps: {
    exclude: ["@vite/client", "@vite/env"]
  },
  build: {
    rollupOptions: {
      external: (id) => {
        return id.includes('/backend/') || id.includes('\\backend\\');
      }
    }
  }
}));

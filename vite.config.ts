import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8081,
    watch: {
      // Exclude backend directory and other heavy directories from file watching
      ignored: [
        "**/backend/**",
        "**/node_modules/**",
        "**/dist/**",
        "**/.git/**",
        "**/__pycache__/**",
        "**/*.pyc",
        "**/myvenv*/**",
        "**/venv*/**",
        "**/.venv*/**",
        "**/artifacts/**",
        "**/logs/**",
        "**/*.log",
        "**/coverage/**",
        "**/.nyc_output/**",
        "**/tmp/**",
        "**/temp/**"
      ]
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
  // Build optimizations
  build: {
    rollupOptions: {
      external: (id) => {
        // Exclude backend files from build
        return id.includes('/backend/') || id.includes('\\backend\\');
      }
    }
  }
}));

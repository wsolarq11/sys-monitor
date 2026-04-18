import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const host = process.env.TAURI_DEV_HOST;

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // Mock Tauri API for web mode (E2E tests)
  resolve: {
    alias: {
      '@tauri-apps/api/core': '/src/mocks/tauri-api-mock.ts',
      '@tauri-apps/api/event': '/src/mocks/tauri-api-mock.ts',
    },
  },

  // Vite options tailored for Tauri development and performance optimized
  // for being entered through the browser
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
    hmr: host
      ? {
          protocol: "ws",
          host,
          port: 1421,
        }
      : undefined,
    watch: {
      ignored: ["**/src-tauri/**"],
    },
  },
  
  // Build optimization (遵循 React Performance Optimization Skill)
  build: {
    // 代码分割配置
    rollupOptions: {
      output: {
        // 手动分块，优化加载性能
        manualChunks: {
          // React 核心库单独打包
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // 图表库单独打包
          'charts': ['recharts'],
          // UI 组件单独打包
          'ui': ['sonner'],
          // 监控相关
          'monitoring': ['@sentry/react', 'web-vitals'],
          // Tauri API
          'tauri': ['@tauri-apps/api', '@tauri-apps/plugin-notification', '@tauri-apps/plugin-shell'],
        },
      },
    },
    // 增加 chunk 大小警告阈值（从 500KB 提升到 1MB）
    chunkSizeWarningLimit: 1000,
    // 启用 sourcemap（生产环境可关闭）
    sourcemap: false,
    // 压缩选项
    minify: 'esbuild',
    terserOptions: {
      compress: {
        drop_console: true,  // 移除 console.log
        drop_debugger: true,
      },
    },
  },
});

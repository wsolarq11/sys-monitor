import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import * as Sentry from "@sentry/react"
import { Toaster } from 'sonner'

// Sentry错误追踪初始化
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN || "https://examplePublicKey@o0.ingest.sentry.io/0",
  integrations: [
    // 新版Sentry使用不同的集成方式
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  // 性能监控
  tracesSampleRate: 1.0,
  // 会话重放
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  // 环境配置
  environment: import.meta.env.MODE || "development",
  release: "sys-monitor@" + (import.meta.env.VITE_APP_VERSION || "0.1.0"),
  // 调试模式
  debug: import.meta.env.MODE === "development",
});

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <Sentry.ErrorBoundary fallback={<ErrorFallback />} showDialog>
      <App />
      <Toaster 
        position="top-right" 
        richColors 
        expand={false}
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </Sentry.ErrorBoundary>
  </React.StrictMode>,
)

// 错误边界回退组件
function ErrorFallback() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
        <h2 className="text-2xl font-bold text-red-600 mb-4">应用程序遇到错误</h2>
        <p className="text-gray-600 mb-4">
          抱歉，SysMonitor遇到了意外错误。我们已经自动报告了这个问题。
        </p>
        <button 
          onClick={() => window.location.reload()} 
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
        >
          重新加载应用
        </button>
      </div>
    </div>
  )
}

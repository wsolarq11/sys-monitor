# SysMonitor

A cross-platform system monitoring dashboard built with Rust and Tauri v2.

## Prerequisites

- Node.js 18+
- pnpm
- Rust 1.70+

## Development

```bash
# Install dependencies
pnpm install

# Start development server
pnpm tauri dev

# Run tests
cd src-tauri && cargo test
```

## Build

```bash
pnpm tauri build
```

## Platform Requirements

### Windows
- WebView2 (included in Windows 10 1803+)

### Linux
```bash
sudo apt install libwebkit2gtk-4.0-dev build-essential libssl-dev \
  libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

### macOS
- Xcode Command Line Tools

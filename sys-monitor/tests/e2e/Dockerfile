FROM mcr.microsoft.com/playwright:v1.40.0-jammy

WORKDIR /app

# 安装 pnpm
RUN corepack enable && corepack prepare pnpm@8 --activate

# 复制 package 文件
COPY package.json pnpm-lock.yaml ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制测试文件
COPY . .

# 安装 Playwright 浏览器
RUN pnpm exec playwright install --with-deps chromium

# 固定环境变量
ENV PLAYWRIGHT_HEADLESS=true
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV CI=true

# 设置工作目录
WORKDIR /app/tests/e2e

# 默认运行 smoke 测试
CMD ["pnpm", "exec", "playwright", "test", "--project=smoke"]

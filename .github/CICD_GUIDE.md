# CI/CD 构建发布指南

## 工作流概览

本项目包含三个 GitHub Actions 工作流,用于自动化构建、测试和发布流程。

### 1. CI 持续集成 (`ci.yml`)

**触发条件:**
- 推送到 `main` 或 `develop` 分支
- 创建 Pull Request 到 `main` 分支
- 推送版本标签 (`v*`)

**执行任务:**
- **后端测试**: 在 Windows/macOS/Linux 三平台运行 Rust 测试
  - 代码格式化检查 (`cargo fmt`)
  - 代码质量检查 (`cargo clippy`)
  - 单元测试 (`cargo test`)
  - Release 构建验证

- **前端测试**: TypeScript 类型检查和构建
  - 依赖安装 (pnpm)
  - TypeScript 编译检查
  - 前端构建验证

- **Tauri 应用构建**: 跨平台桌面应用构建
  - 生成 MSI/NSIS (Windows)、DMG (macOS)、DEB/AppImage (Linux)
  - 自动上传构建产物为 Artifacts

- **代码覆盖率**: 在主分支推送时生成覆盖率报告

### 2. 发布构建 (`release.yml`)

**触发条件:**
- 推送版本标签 (如 `v2.0.0`)
- 手动触发工作流 (Workflow Dispatch)

**执行任务:**
- **多平台构建**:
  - Windows: MSI 安装包 + NSIS 安装程序
  - macOS: DMG 磁盘镜像 (Intel + Apple Silicon)
  - Linux: DEB 包 + AppImage

- **自动发布**:
  - 生成变更日志 (Changelog)
  - 创建 GitHub Release (Draft 状态)
  - 上传所有平台构建产物

**手动触发参数:**
- `version`: 版本号 (例如: v2.0.0)
- `prerelease`: 是否为预发布版本

### 3. 版本管理 (`version-bump.yml`)

**触发条件:**
- 仅支持手动触发

**功能:**
- 自动计算新版本号 (基于语义化版本)
- 更新 `Cargo.toml` 和 `package.json` 中的版本号
- 创建 Git 标签并推送
- 自动触发发布工作流

**使用参数:**
- `version_type`: 版本类型
  - `patch`: 补丁版本 (1.0.0 → 1.0.1)
  - `minor`: 次版本 (1.0.0 → 1.1.0)
  - `major`: 主版本 (1.0.0 → 2.0.0)
- `custom_version`: 自定义版本号 (可选)
- `prerelease`: 是否标记为预发布

## 使用流程

### 日常开发流程

```bash
# 1. 开发完成后推送到分支
git push origin feature/my-feature

# 2. 创建 Pull Request
# CI 会自动运行所有测试和构建检查

# 3. PR 合并后
# CI 会在 main 分支再次运行完整测试
```

### 发布新版本流程

#### 方法一: 使用版本管理工作流 (推荐)

1. 进入 GitHub Actions 页面
2. 选择 "Version Bump & Tag" 工作流
3. 点击 "Run workflow"
4. 选择版本类型:
   - **patch**: Bug 修复和小改进
   - **minor**: 新功能添加
   - **major**: 重大破坏性变更
5. (可选) 输入自定义版本号
6. (可选) 勾选"预发布版本"
7. 点击运行

**自动执行:**
- 版本号自动更新
- 创建 Git 标签
- 触发发布工作流
- 构建所有平台安装包
- 创建 Draft Release

#### 方法二: 手动创建标签

```bash
# 1. 更新版本号
# 编辑 sys-monitor/src-tauri/Cargo.toml
# 修改 version = "2.0.0"

# 2. 提交更改
git add sys-monitor/src-tauri/Cargo.toml
git commit -m "chore: bump version to v2.0.0"

# 3. 创建并推送标签
git tag -a v2.0.0 -m "Release v2.0.0"
git push origin v2.0.0

# 4. 发布工作流自动触发
```

### 查看和管理发布

1. 访问: `https://github.com/<owner>/<repo>/releases`
2. 找到 Draft Release
3. 审查构建产物和变更日志
4. 编辑发布信息 (可选)
5. 点击 "Publish release" 正式发布

## 环境变量配置

### 必需的秘密变量 (Secrets)

在 GitHub 仓库设置中添加以下 Secrets:

**基础配置:**
- `GITHUB_TOKEN`: 自动生成,无需手动配置

**macOS 代码签名 (可选,用于 macOS 发布):**
- `APPLE_CERTIFICATE`: Apple 开发者证书 (base64 编码)
- `APPLE_CERTIFICATE_PASSWORD`: 证书密码
- `APPLE_SIGNING_IDENTITY`: 签名身份
- `APPLE_ID`: Apple ID
- `APPLE_PASSWORD`: Apple ID 专用密码
- `APPLE_TEAM_ID`: Apple 团队 ID

**其他服务 (可选):**
- `CODECOV_TOKEN`: Codecov 代码覆盖率服务令牌

### 配置步骤

1. 进入仓库 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加上述所需的密钥

## 构建产物说明

### Windows
- **MSI**: Windows Installer 安装包
  - 位置: `sys-monitor/src-tauri/target/release/bundle/msi/`
  - 适合企业部署

- **NSIS**: 可执行安装程序 (.exe)
  - 位置: `sys-monitor/src-tauri/target/release/bundle/nsis/`
  - 适合普通用户

### macOS
- **DMG**: 磁盘镜像文件
  - 位置: `sys-monitor/src-tauri/target/release/bundle/dmg/`
  - 包含已签名的 .app 文件

### Linux
- **DEB**: Debian/Ubuntu 安装包
  - 位置: `sys-monitor/src-tauri/target/release/bundle/deb/`

- **AppImage**: 通用 Linux 应用格式
  - 位置: `sys-monitor/src-tauri/target/release/bundle/appimage/`
  - 无需安装,直接运行

## 故障排查

### 构建失败

1. **检查日志**: 在 Actions 页面查看失败步骤的详细日志
2. **本地复现**: 在本地环境运行相同的构建命令
3. **缓存问题**: 尝试清除缓存后重新运行
   ```bash
   # 在 workflow 中添加缓存清除步骤或使用不同的缓存键
   ```

### 常见问题

**Q: macOS 构建失败,提示签名错误**
A: 检查 Apple 相关 Secrets 是否正确配置,或暂时禁用代码签名

**Q: Linux 构建缺少依赖**
A: 检查工作流中的系统依赖安装步骤,确保包含所有必需的库

**Q: 构建时间过长**
A: 检查缓存配置,确保 Cargo 和 pnpm 缓存正常工作

**Q: Artifact 上传失败**
A: 检查文件路径是否正确,确认构建产物确实生成

## 最佳实践

1. **语义化版本**: 遵循 SemVer 规范 (MAJOR.MINOR.PATCH)
2. **变更日志**: 每次发布前审查自动生成的 changelog
3. **预发布测试**: 重要版本先发布 alpha/beta 版本进行测试
4. **多平台验证**: 在每个平台上测试安装包是否正常
5. **标签管理**: 使用带注释的标签 (`git tag -a`)
6. **定期清理**: 删除旧的 draft releases 和 artifacts

## 自定义扩展

### 添加新的构建目标

编辑 `release.yml` 中的 matrix 配置:

```yaml
matrix:
  include:
    - platform: windows-latest
      os: windows-latest
      target: aarch64-pc-windows-msvc  # ARM64 Windows
      artifact_name: msi
```

### 添加发布通知

在 `release.yml` 末尾添加通知步骤:

```yaml
- name: Notify Discord
  uses: discord-webhook-action@v1
  with:
    webhook-url: ${{ secrets.DISCORD_WEBHOOK }}
    message: "新版本 ${{ github.ref_name }} 已发布!"
```

### 自动化部署

添加部署到应用商店或 CDN 的步骤:

```yaml
- name: Upload to CDN
  run: |
    aws s3 sync artifacts/ s3://my-cdn/releases/${{ github.ref_name }}/
```

## 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Tauri CI/CD 指南](https://tauri.app/v1/guides/building/ci/)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [Rust CI 最佳实践](https://doc.rust-lang.org/cargo/guide/continuous-integration.html)

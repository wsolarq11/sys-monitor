#!/usr/bin/env pwsh
# 工作区根目录清洁度检查与自动修复脚本
# 用途：检测并清理根目录的违规文件

$ErrorActionPreference = 'Stop'

# 定义允许的文件类型（白名单）
$allowedFiles = @(
    '.gitignore',
    '.lingmaignore',
    'README.md'  # 仅当项目需要时
)

# 定义禁止的文件模式（黑名单）
$forbiddenPatterns = @(
    '^\d+\.md$',           # 数字开头的md文件
    '^\d+KB$',             # 大小标记文件
    '^0$',                 # 临时文件
    '.*OPTIMIZATION.*',    # 优化相关文档
    '.*QUICK_REFERENCE.*', # 快速参考
    '.*SUMMARY.*',         # 总结报告
    '.*REPORT.*',          # 报告
    '.*CHECKLIST.*',       # 检查清单
    '^benchmark_.*\.py$',  # 基准测试脚本
    '^fix_.*\.py$',        # 修复脚本
    '^optimize_.*\.(py|ps1)$', # 优化脚本
    '^enable_.*\.py$',     # 启用脚本
    '^temp_.*',            # 临时文件
    '^test_.*\.py$',       # 测试脚本
)

Write-Host "🔍 检查工作区根目录清洁度..." -ForegroundColor Cyan

# 获取根目录所有文件
$rootPath = Split-Path $PSScriptRoot -Parent
$files = Get-ChildItem -Path $rootPath -File | Where-Object { 
    $_.Name -notmatch '^\.'  # 排除隐藏文件
}

$violations = @()

foreach ($file in $files) {
    $isAllowed = $allowedFiles -contains $file.Name
    
    if (-not $isAllowed) {
        foreach ($pattern in $forbiddenPatterns) {
            if ($file.Name -match $pattern) {
                $violations += $file
                break
            }
        }
    }
}

if ($violations.Count -eq 0) {
    Write-Host "✅ 根目录清洁度检查通过！" -ForegroundColor Green
    exit 0
}

Write-Host "❌ 发现 $($violations.Count) 个违规文件：" -ForegroundColor Red
$violations | ForEach-Object {
    Write-Host "   - $($_.Name) ($([math]::Round($_.Length / 1KB, 2)) KB)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🛠️  开始自动修复..." -ForegroundColor Cyan

# 确保目标目录存在
$docsReportsPath = Join-Path $rootPath ".lingma/docs/reports"
$scriptsPath = Join-Path $rootPath "scripts"

if (-not (Test-Path $docsReportsPath)) {
    New-Item -ItemType Directory -Path $docsReportsPath -Force | Out-Null
    Write-Host "   创建目录: .lingma/docs/reports" -ForegroundColor Gray
}

if (-not (Test-Path $scriptsPath)) {
    New-Item -ItemType Directory -Path $scriptsPath -Force | Out-Null
    Write-Host "   创建目录: scripts" -ForegroundColor Gray
}

# 移动违规文件
foreach ($file in $violations) {
    $fileName = $file.Name
    
    # 判断文件类型
    if ($fileName -match '\.py$|\.ps1$|\.sh$') {
        # 脚本文件 -> scripts/
        $destPath = Join-Path $scriptsPath $fileName
        
        # 如果scripts中已有同名文件，添加时间戳
        if (Test-Path $destPath) {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $baseName = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
            $extension = [System.IO.Path]::GetExtension($fileName)
            $destPath = Join-Path $scriptsPath "${baseName}_${timestamp}${extension}"
        }
        
        Move-Item $file.FullName $destPath -Force
        Write-Host "   📦 移动脚本: $fileName -> scripts/" -ForegroundColor Green
    }
    else {
        # 文档文件 -> .lingma/docs/reports/
        $destPath = Join-Path $docsReportsPath $fileName
        
        # 如果reports中已有同名文件，添加时间戳
        if (Test-Path $destPath) {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $baseName = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
            $extension = [System.IO.Path]::GetExtension($fileName)
            $destPath = Join-Path $docsReportsPath "${baseName}_${timestamp}${extension}"
        }
        
        Move-Item $file.FullName $destPath -Force
        Write-Host "   📄 移动文档: $fileName -> .lingma/docs/reports/" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ 根目录清洁度修复完成！" -ForegroundColor Green
Write-Host "📊 统计信息:" -ForegroundColor Cyan
Write-Host "   - 移动文档: $(($violations | Where-Object { $_.Name -notmatch '\.py$|\.ps1$|\.sh$' }).Count) 个" -ForegroundColor Gray
Write-Host "   - 移动脚本: $(($violations | Where-Object { $_.Name -match '\.py$|\.ps1$|\.sh$' }).Count) 个" -ForegroundColor Gray

exit 0

# Spec Watcher Windows计划任务安装脚本
# 功能: 自动注册Windows Task Scheduler任务，开机自启spec-watcher守护进程

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status,
    [string]$ProjectRoot = (Get-Location).Path
)

$TaskName = "SpecWatcherDaemon"
$TaskDescription = "Spec文件监听守护进程 - 实时监控Spec变化并触发重新评估"
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
$ScriptPath = Join-Path $ProjectRoot ".lingma\scripts\spec-watcher.py"
$LogPath = Join-Path $ProjectRoot ".lingma\logs\watcher-install.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    Write-Host $logEntry
    
    # 确保日志目录存在
    $logDir = Split-Path $LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    Add-Content -Path $LogPath -Value $logEntry
}

function Test-AdminPrivileges {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-SpecWatcherTask {
    Write-Log "开始安装Spec Watcher计划任务..."
    
    # 检查管理员权限
    if (-not (Test-AdminPrivileges)) {
        Write-Log "错误: 需要管理员权限" "ERROR"
        Write-Host "请以管理员身份运行此脚本" -ForegroundColor Red
        return $false
    }
    
    # 检查Python是否存在
    if (-not $PythonPath) {
        Write-Log "错误: 未找到Python" "ERROR"
        Write-Host "请先安装Python并添加到PATH" -ForegroundColor Red
        return $false
    }
    
    # 检查脚本是否存在
    if (-not (Test-Path $ScriptPath)) {
        Write-Log "错误: spec-watcher.py不存在: $ScriptPath" "ERROR"
        Write-Host "spec-watcher.py不存在" -ForegroundColor Red
        return $false
    }
    
    # 检查watchdog是否安装
    try {
        & python -c "import watchdog" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Log "安装watchdog依赖..." "WARNING"
            Write-Host "正在安装watchdog..." -ForegroundColor Yellow
            & python -m pip install watchdog
        }
    } catch {
        Write-Log "安装watchdog失败: $_" "ERROR"
        return $false
    }
    
    # 删除已存在的任务
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Log "删除已存在的任务..." "INFO"
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    # 创建计划任务动作
    $action = New-ScheduledTaskAction `
        -Execute $PythonPath `
        -Argument "`"$ScriptPath`" --start" `
        -WorkingDirectory $ProjectRoot
    
    # 创建触发器：登录时启动
    $trigger = New-ScheduledTaskTrigger `
        -AtLogOn `
        -User $env:USERNAME
    
    # 创建设置
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 5) `
        -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
        -Priority 7
    
    # 创建主体（以当前用户身份运行）
    $principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -LogonType Interactive `
        -RunLevel Highest
    
    # 注册任务
    try {
        Register-ScheduledTask `
            -TaskName $TaskName `
            -Description $TaskDescription `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Principal $principal `
            -Force
        
        Write-Log "Spec Watcher计划任务安装成功" "SUCCESS"
        Write-Host "✅ Spec Watcher计划任务已成功安装" -ForegroundColor Green
        Write-Host "   任务名称: $TaskName" -ForegroundColor Cyan
        Write-Host "   触发条件: 用户登录时" -ForegroundColor Cyan
        Write-Host "   Python路径: $PythonPath" -ForegroundColor Cyan
        Write-Host "   脚本路径: $ScriptPath" -ForegroundColor Cyan
        
        # 立即启动任务进行测试
        Write-Host "`n是否立即启动Spec Watcher进行测试? (Y/N)" -ForegroundColor Yellow
        $response = Read-Host
        if ($response -eq 'Y' -or $response -eq 'y') {
            Start-ScheduledTask -TaskName $TaskName
            Write-Host "Spec Watcher已启动" -ForegroundColor Green
        }
        
        return $true
    } catch {
        Write-Log "注册任务失败: $_" "ERROR"
        Write-Host "❌ 注册任务失败: $_" -ForegroundColor Red
        return $false
    }
}

function Uninstall-SpecWatcherTask {
    Write-Log "开始卸载Spec Watcher计划任务..."
    
    # 检查管理员权限
    if (-not (Test-AdminPrivileges)) {
        Write-Log "错误: 需要管理员权限" "ERROR"
        Write-Host "请以管理员身份运行此脚本" -ForegroundColor Red
        return $false
    }
    
    # 检查任务是否存在
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $task) {
        Write-Log "任务不存在，无需卸载" "WARNING"
        Write-Host "⚠️  Spec Watcher计划任务不存在" -ForegroundColor Yellow
        return $true
    }
    
    # 停止正在运行的任务
    try {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Write-Log "已停止正在运行的任务" "INFO"
    } catch {
        Write-Log "停止任务失败: $_" "WARNING"
    }
    
    # 删除任务
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Log "Spec Watcher计划任务已卸载" "SUCCESS"
        Write-Host "✅ Spec Watcher计划任务已卸载" -ForegroundColor Green
        return $true
    } catch {
        Write-Log "卸载任务失败: $_" "ERROR"
        Write-Host "❌ 卸载任务失败: $_" -ForegroundColor Red
        return $false
    }
}

function Get-SpecWatcherStatus {
    Write-Log "检查Spec Watcher状态..."
    
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    
    if (-not $task) {
        Write-Host "❌ Spec Watcher计划任务未安装" -ForegroundColor Red
        return @{
            Installed = $false
            Status = "Not Installed"
        }
    }
    
    $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
    $state = $task.State
    
    Write-Host "`n📊 Spec Watcher状态:" -ForegroundColor Cyan
    Write-Host "   安装状态: ✅ 已安装" -ForegroundColor Green
    Write-Host "   运行状态: $state" -ForegroundColor $(if ($state -eq 'Running') { 'Green' } else { 'Yellow' })
    Write-Host "   上次运行时间: $($taskInfo.LastRunTime)" -ForegroundColor Cyan
    Write-Host "   上次运行结果: $($taskInfo.LastTaskResult)" -ForegroundColor Cyan
    Write-Host "   下次运行时间: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
    Write-Host "   触发条件: 用户登录时" -ForegroundColor Cyan
    
    return @{
        Installed = $true
        Status = $state
        LastRunTime = $taskInfo.LastRunTime
        LastTaskResult = $taskInfo.LastTaskResult
        NextRunTime = $taskInfo.NextRunTime
    }
}

function Show-Help {
    Write-Host "`nSpec Watcher Windows计划任务管理工具" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    Write-Host "用法:" -ForegroundColor Yellow
    Write-Host "  .\install-windows-task.ps1 -Install      安装计划任务" -ForegroundColor White
    Write-Host "  .\install-windows-task.ps1 -Uninstall    卸载计划任务" -ForegroundColor White
    Write-Host "  .\install-windows-task.ps1 -Status       查看状态" -ForegroundColor White
    Write-Host "  .\install-windows-task.ps1               显示帮助" -ForegroundColor White
    Write-Host "`n参数:" -ForegroundColor Yellow
    Write-Host "  -ProjectRoot <path>  项目根目录 (默认: 当前目录)" -ForegroundColor White
    Write-Host "`n示例:" -ForegroundColor Yellow
    Write-Host "  .\install-windows-task.ps1 -Install" -ForegroundColor White
    Write-Host "  .\install-windows-task.ps1 -Status" -ForegroundColor White
    Write-Host "`n注意: 安装和卸载需要管理员权限" -ForegroundColor Yellow
}

# 主逻辑
if ($Install) {
    Install-SpecWatcherTask
} elseif ($Uninstall) {
    Uninstall-SpecWatcherTask
} elseif ($Status) {
    Get-SpecWatcherStatus
} else {
    Show-Help
}

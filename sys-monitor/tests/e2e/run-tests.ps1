#!/usr/bin/env pwsh

param(
    [ValidateSet('smoke', 'critical', 'regression', 'all')]
    [string]$TestType = 'all',
    
    [switch]$ headed,
    
    [switch]$Debug,
    
    [int]$Workers = 2
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SysMonitor Playwright Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$env:CI = $env:CI ?? "false"

if ($Debug) {
    Write-Host "Running in debug mode..." -ForegroundColor Yellow
    $headed = $true
}

$commonArgs = @(
    '--config', 'playwright.config.ts'
)

if ($headed) {
    $commonArgs += '--headed'
    Write-Host "Running in headed mode..." -ForegroundColor Yellow
}

if ($Debug) {
    $commonArgs += '--debug'
    Write-Host "Debug mode enabled - tests will run in serial" -ForegroundColor Yellow
} else {
    $commonArgs += "--workers=$Workers"
}

switch ($TestType) {
    'smoke' {
        Write-Host "Running Smoke Tests (@smoke) - Deployment Verification" -ForegroundColor Green
        $commonArgs += '--project=smoke'
        $commonArgs += '--grep=@smoke'
    }
    
    'critical' {
        Write-Host "Running Critical Tests (@critical) - Daily CI" -ForegroundColor Green
        $commonArgs += '--project=critical'
        $commonArgs += '--grep=@critical'
    }
    
    'regression' {
        Write-Host "Running Regression Tests (@regression) - Branch Merge" -ForegroundColor Green
        $commonArgs += '--project=regression'
        $commonArgs += '--grep=@regression'
    }
    
    'all' {
        Write-Host "Running All Tests - Full Suite" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Executing: pnpm playwright test $($commonArgs -join ' ')" -ForegroundColor Cyan
Write-Host ""

pnpm playwright test @commonArgs

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "Tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Tests failed with exit code: $exitCode" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

exit $exitCode

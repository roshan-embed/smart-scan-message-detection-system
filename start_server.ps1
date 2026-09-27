# ========================================================
# SMART SCAM MESSAGE DETECTION SYSTEM
# PowerShell Server Launcher with Auto-Browser
# ========================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$PythonExe = "python"
if (Test-Path "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe") {
    $PythonExe = "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe"
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " SMART SCAM MESSAGE DETECTION SYSTEM" -ForegroundColor White
Write-Host " Module 1: User Account & Authentication" -ForegroundColor Green
Write-Host " Server: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

# Open default browser after 2 seconds
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:5000"
} | Out-Null

& $PythonExe run.py

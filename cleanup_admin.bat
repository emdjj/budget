@echo off
title C Drive Cleanup & Cache Migration - ADMIN
cd /d "D:\budget"

echo ============================================
echo   C Drive Cleanup - Admin Tasks
echo   Running with elevated privileges...
echo ============================================
echo.

:: ============================================
:: Part 1: DISM Component Cleanup (Level 2)
:: ============================================
echo [1/3] Running DISM WinSxS component cleanup...
echo This may take several minutes. Please wait...
DISM.exe /Online /Cleanup-Image /StartComponentCleanup
echo DISM cleanup complete.
echo.

:: ============================================
:: Part 2: ProgramData Cleanup
:: ============================================
echo [2/3] Cleaning ProgramData...

:: Epic
if exist "C:\ProgramData\Epic" (
    echo Cleaning Epic...
    takeown /f "C:\ProgramData\Epic" /r /d y >nul 2>&1
    icacls "C:\ProgramData\Epic" /grant "%USERNAME%:F" /t /q >nul 2>&1
    rd /s /q "C:\ProgramData\Epic\UnrealEngine\DerivedDataCache" 2>nul
    rd /s /q "C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests" 2>nul
    echo   Done
)

:: NVIDIA Corporation (ProgramData)
if exist "C:\ProgramData\NVIDIA Corporation\Downloader" (
    echo Cleaning NVIDIA Corporation cache...
    rd /s /q "C:\ProgramData\NVIDIA Corporation\Downloader" 2>nul
    echo   Done
)

:: Package Cache
if exist "C:\ProgramData\Package Cache" (
    echo Cleaning Package Cache...
    takeown /f "C:\ProgramData\Package Cache" /r /d y >nul 2>&1
    icacls "C:\ProgramData\Package Cache" /grant "%USERNAME%:F" /t /q >nul 2>&1
    rd /s /q "C:\ProgramData\Package Cache" 2>nul
    echo   Done
)
echo.

:: ============================================
:: Part 3: Setup Directory Symlinks (Cache to D:)
:: ============================================
echo [3/3] Setting up directory symlinks for cache relocation to D: drive...

:: Make sure D: target directories exist
if not exist "D:\AppDataCache" mkdir "D:\AppDataCache"
if not exist "D:\AppDataCache\NetEase" mkdir "D:\AppDataCache\NetEase"
if not exist "D:\AppDataCache\DingTalk" mkdir "D:\AppDataCache\DingTalk"
if not exist "D:\AppDataCache\JetBrains" mkdir "D:\AppDataCache\JetBrains"
if not exist "D:\AppDataCache\b1" mkdir "D:\AppDataCache\b1"
if not exist "D:\AppDataCache\NVIDIA" mkdir "D:\AppDataCache\NVIDIA"

:: Close apps that might lock these directories
echo   Closing apps that may lock these folders...
taskkill /f /im "CloudMusic.exe" 2>nul
taskkill /f /im "DingTalk.exe" 2>nul
taskkill /f /im "idea64.exe" 2>nul
taskkill /f /im "pycharm64.exe" 2>nul
>nul timeout /t 3 /nobreak

:: 1. NetEase
echo   NetEase...
if exist "C:\Users\%USERNAME%\AppData\Local\NetEase" (
    xcopy "C:\Users\%USERNAME%\AppData\Local\NetEase\*" "D:\AppDataCache\NetEase\" /E /C /Q /Y >nul 2>&1
    rd /s /q "C:\Users\%USERNAME%\AppData\Local\NetEase" 2>nul
    mklink /D "C:\Users\%USERNAME%\AppData\Local\NetEase" "D:\AppDataCache\NetEase"
)

:: 2. DingTalk
echo   DingTalk...
if exist "C:\Users\%USERNAME%\AppData\Local\DingTalk_108" (
    xcopy "C:\Users\%USERNAME%\AppData\Local\DingTalk_108\*" "D:\AppDataCache\DingTalk\" /E /C /Q /Y >nul 2>&1
    rd /s /q "C:\Users\%USERNAME%\AppData\Local\DingTalk_108" 2>nul
    mklink /D "C:\Users\%USERNAME%\AppData\Local\DingTalk_108" "D:\AppDataCache\DingTalk"
)

:: 3. b1 (Claude/bing data)
echo   b1...
if exist "C:\Users\%USERNAME%\AppData\Local\b1" (
    xcopy "C:\Users\%USERNAME%\AppData\Local\b1\*" "D:\AppDataCache\b1\" /E /C /Q /Y >nul 2>&1
    rd /s /q "C:\Users\%USERNAME%\AppData\Local\b1" 2>nul
    mklink /D "C:\Users\%USERNAME%\AppData\Local\b1" "D:\AppDataCache\b1"
)

:: 4. NVIDIA shader cache subdirs only
echo   NVIDIA shader cache...
if not exist "D:\AppDataCache\NVIDIA\DXCache" mkdir "D:\AppDataCache\NVIDIA\DXCache"
if not exist "D:\AppDataCache\NVIDIA\GLCache" mkdir "D:\AppDataCache\NVIDIA\GLCache"
if exist "C:\Users\%USERNAME%\AppData\Local\NVIDIA" (
    if exist "C:\Users\%USERNAME%\AppData\Local\NVIDIA\DXCache" (
        rd /s /q "C:\Users\%USERNAME%\AppData\Local\NVIDIA\DXCache" 2>nul
        mklink /D "C:\Users\%USERNAME%\AppData\Local\NVIDIA\DXCache" "D:\AppDataCache\NVIDIA\DXCache"
    )
    if exist "C:\Users\%USERNAME%\AppData\Local\NVIDIA\GLCache" (
        rd /s /q "C:\Users\%USERNAME%\AppData\Local\NVIDIA\GLCache" 2>nul
        mklink /D "C:\Users\%USERNAME%\AppData\Local\NVIDIA\GLCache" "D:\AppDataCache\NVIDIA\GLCache"
    )
)

:: 5. JetBrains cache subdirs only
echo   JetBrains...
if not exist "D:\AppDataCache\JetBrains\IntelliJIdea2025.3" mkdir "D:\AppDataCache\JetBrains\IntelliJIdea2025.3"
if not exist "D:\AppDataCache\JetBrains\PyCharm2024.3" mkdir "D:\AppDataCache\JetBrains\PyCharm2024.3"

if exist "C:\Users\%USERNAME%\AppData\Local\JetBrains\IntelliJIdea2025.3\cache" (
    rd /s /q "C:\Users\%USERNAME%\AppData\Local\JetBrains\IntelliJIdea2025.3\cache" 2>nul
    mklink /D "C:\Users\%USERNAME%\AppData\Local\JetBrains\IntelliJIdea2025.3\cache" "D:\AppDataCache\JetBrains\IntelliJIdea2025.3"
)
if exist "C:\Users\%USERNAME%\AppData\Local\JetBrains\IntelliJIdea2025.3\index" (
    rd /s /q "C:\Users\%USERNAME%\AppData\Local\JetBrains\IntelliJIdea2025.3\index" 2>nul
    mklink /D "C:\Users\%USERNAME%\AppData\Local\JetBrains\IntelliJIdea2025.3\index" "D:\AppDataCache\JetBrains\IntelliJIdea2025.3"
)
if exist "C:\Users\%USERNAME%\AppData\Local\JetBrains\PyCharm2024.3\cache" (
    rd /s /q "C:\Users\%USERNAME%\AppData\Local\JetBrains\PyCharm2024.3\cache" 2>nul
    mklink /D "C:\Users\%USERNAME%\AppData\Local\JetBrains\PyCharm2024.3\cache" "D:\AppDataCache\JetBrains\PyCharm2024.3"
)
if exist "C:\Users\%USERNAME%\AppData\Local\JetBrains\PyCharm2024.3\index" (
    rd /s /q "C:\Users\%USERNAME%\AppData\Local\JetBrains\PyCharm2024.3\index" 2>nul
    mklink /D "C:\Users\%USERNAME%\AppData\Local\JetBrains\PyCharm2024.3\index" "D:\AppDataCache\JetBrains\PyCharm2024.3"
)

echo.
echo ============================================
echo   All admin tasks completed!
echo.
echo   Summary:
echo   - DISM WinSxS cleaned
echo   - ProgramData caches cleaned
echo   - App caches relocated to D:\AppDataCache\
echo.
echo   Press any key to exit...
echo ============================================
>nul pause

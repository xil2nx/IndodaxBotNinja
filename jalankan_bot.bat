@echo off
setlocal
chcp 65001
title il2n Indodax Turbo Bot 2026
color 0b
cls

echo ==================================================
echo        SISTEM OTOMATISASI ROBOT INDODAX il2n V1.1
echo ==================================================
echo.

:: ================================
:: 1. CEK INSTALASI PYTHON
:: ================================
echo [1/5] Memeriksa instalasi Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0c
    echo [WARN] Python tidak ditemukan. Mencoba install otomatis...
    
    :: Tentukan URL installer Python terbaru (64-bit, Windows)
    set PYTHON_URL=https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
    set PYTHON_INSTALLER=%TEMP%\python_installer.exe

    echo Mengunduh Python...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"
    if %errorlevel% neq 0 (
        echo [ERROR] Gagal mengunduh installer Python!
        pause
        exit
    )

    echo Menginstal Python secara silent...
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    if %errorlevel% neq 0 (
        echo [ERROR] Instalasi Python gagal!
        pause
        exit
    )

    echo [OK] Python berhasil diinstal.
) else (
    for /f "tokens=2 delims= " %%i in ('python --version') do set PYVER=%%i
    echo [OK] Python terdeteksi versi %PYVER%.
)
echo.

:: ================================
:: 2. CEK & PERBAIKI PIP
:: ================================
echo [2/5] Memeriksa pengelola paket (PIP)...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] PIP tidak ditemukan. Mencoba memperbaiki otomatis...
    python -m ensurepip --default-pip >nul 2>&1
    python -m pip install --upgrade pip --quiet
    if %errorlevel% neq 0 (
        color 0c
        echo [ERROR] PIP gagal diperbaiki!
        pause
        exit
    )
)
echo [OK] PIP siap digunakan.
echo.

:: ================================
:: 3. INSTAL / UPDATE LIBRARY
:: ================================
echo [3/5] Sinkronisasi Library (ccxt, pandas, colorama, configparser)...
python -m pip install --upgrade --quiet ccxt pandas colorama configparser
if %errorlevel% neq 0 (
    color 0c
    echo [ERROR] Gagal mengunduh library. Periksa koneksi internet!
    pause
    exit
)
echo [OK] Semua library siap.
echo.

:: ================================
:: 4. CEK FILE PENDUKUNG
:: ================================
echo [4/5] Memeriksa file aplikasi...
if not exist "config.txt" (
    color 0c
    echo [ERROR] File config.txt tidak ditemukan!
    echo Buat file config.txt berisi API_KEY, SECRET_KEY, TOKEN, dan CHAT_ID Anda.
    pause
    exit
)
if not exist "bot_indodax.py" (
    color 0c
    echo [ERROR] File bot_indodax.py tidak ditemukan!
    pause
    exit
)
echo [OK] File aplikasi lengkap.
echo.

:: ================================
:: 5. SINKRONISASI WAKTU (OPSIONAL)
:: ================================
echo [5/5] Sinkronisasi waktu sistem...
net session >nul 2>&1
if %errorlevel% == 0 (
    w32tm /resync >nul 2>&1
    echo [OK] Waktu disinkronkan dengan server Windows.
) else (
    echo [INFO] Jalankan sebagai Admin untuk sinkronisasi waktu otomatis.
)
echo.

:: ================================
:: JALANKAN BOT
:: ================================
echo --------------------------------------------------
echo [SUKSES] Robot siap dijalankan!
echo --------------------------------------------------
timeout /t 2 >nul
cls
python bot_indodax.py
pause

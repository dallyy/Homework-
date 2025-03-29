@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

set "PYTHONIOENCODING=utf-8"
set "LOG_FILE=run_both.log"
set "PROJECT_ROOT=%~dp0"
set "TEST_SCRIPT=%PROJECT_ROOT%test.py"
set "QD_SCRIPT=%PROJECT_ROOT%vlu\qd.py"

:: 检查并安装必要的Python依赖
python -c "import dotenv" >nul 2>&1
if errorlevel 1 (
    echo Installing python-dotenv...
    pip install python-dotenv
    if errorlevel 1 (
        echo Error: Failed to install python-dotenv
        exit /b 1
    )
)

if not exist "%TEST_SCRIPT%" (
    echo Error: Test script not found at %TEST_SCRIPT%
    exit /b 1
)

if not exist "%QD_SCRIPT%" (
    echo Error: QD script not found at %QD_SCRIPT%
    exit /b 1
)

type nul > "%LOG_FILE%"

start "Test Process" /B cmd /c "python "%TEST_SCRIPT%" >> "%LOG_FILE%" 2>&1"
echo Started test.py (PID: !ERRORLEVEL!)

pushd "%PROJECT_ROOT%vlu"
start "QD Process" /B cmd /c "uv run qd.py >> "..\qd.log" 2>&1"
popd
echo Started qd.py (PID: !ERRORLEVEL!)

echo 按任意键终止进程...
pause > nul

taskkill /FI "WINDOWTITLE eq Test Process*" /T /F > nul
taskkill /FI "WINDOWTITLE eq QD Process*" /T /F > nul

echo 所有进程已终止
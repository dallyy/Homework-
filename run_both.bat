@echo off

setlocal enabledelayedexpansion

:: 设置项目根目录
set "PROJECT_ROOT=%~dp0"

:: 启动main.py进程
start /B "Test Process" cmd /c python "%PROJECT_ROOT%main.py"

:: 进入vlu目录启动qd.py
cd /d "%PROJECT_ROOT%vlu"
start /B "QD Process" cmd /c uv run qd.py

:: 保持窗口打开
@echo off
chcp 65001
echo 正在检查Python环境...

python --version >nul 2>&1
if errorlevel 1 (
    echo 未检测到Python，请先安装Python
    pause
    exit /b 1
)

echo 正在创建虚拟环境...
python -m venv venv
call venv\Scripts\activate

echo 正在升级pip...
python -m pip install --upgrade pip

echo 正在安装依赖包...
pip install -r requirements.txt

echo 依赖包安装完成！
pause
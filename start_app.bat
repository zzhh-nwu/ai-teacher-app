@echo off
chcp 65001 >nul
title AI课程设计助手启动器

echo ================================
echo    AI课程设计助手启动程序
echo ================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.7或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 正在检查依赖包...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo 正在安装必需的依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误：依赖包安装失败
        pause
        exit /b 1
    )
)

echo 正在启动AI课程设计助手...
echo 启动成功后会自动在浏览器中打开应用...
echo 请稍候...
echo.
echo 如果浏览器没有自动打开，请手动访问：
echo http://localhost:8501
echo.

streamlit run app.py

pause
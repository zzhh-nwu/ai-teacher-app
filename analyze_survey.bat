@echo off
chcp 65001 >nul
title 调查结果分析工具

echo ================================
echo    满意度调查结果分析工具
echo ================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python
    pause
    exit /b 1
)

echo 正在生成调查结果可视化图表...
python survey_results_plot.py

if errorlevel 1 (
    echo.
    echo 分析失败，可能的原因：
    echo 1. survey_results.json文件不存在
    echo 2. 缺少必要的依赖包
    echo 3. 请先运行应用并收集一些调查数据
    pause
) else (
    echo.
    echo ✅ 分析完成！
    echo 图表已保存到 survey_analysis_results 文件夹
    echo 按任意键打开结果文件夹...
    pause
    if exist "survey_analysis_results" (
        explorer "survey_analysis_results"
    )
)
@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   标注评测报告生成工具 - 安装依赖
echo ========================================
echo.
echo 正在安装依赖，请稍候...
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo ========================================
if %errorlevel% equ 0 (
    echo   ✓ 依赖安装成功！
) else (
    echo   ✗ 安装失败，请检查 Python 是否正确安装
)
echo ========================================
echo.
pause
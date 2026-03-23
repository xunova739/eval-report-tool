@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   标注评测报告生成工具 - 启动中...
echo ========================================
echo.
echo 请稍候，正在启动 Web 服务...
echo 启动后浏览器会自动打开 http://localhost:8502
echo.
echo 【注意】请勿关闭此窗口，关闭窗口将停止服务
echo.
echo ========================================
python -m streamlit run app.py --server.port 8502 --server.headless true
pause
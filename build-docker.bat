@echo off
REM Docker 镜像构建和导出脚本
REM 使用方法：双击运行此脚本

echo ========================================
echo 旅行规划助手 - Docker 镜像构建和导出
echo ========================================
echo.

REM 检查 Docker 是否运行
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker 未安装或未运行！
    echo 请先安装并启动 Docker Desktop
    pause
    exit /b 1
)

echo [1/4] 检查 Docker 环境...
docker --version
echo.

echo [2/4] 构建 Docker 镜像...
docker build -t travel-planning:latest .
if %errorlevel% neq 0 (
    echo [错误] 镜像构建失败！
    pause
    exit /b 1
)
echo [成功] 镜像构建完成！
echo.

echo [3/4] 导出 Docker 镜像为 tar 文件...
docker save -o travel-planning-image.tar travel-planning:latest
if %errorlevel% neq 0 (
    echo [错误] 镜像导出失败！
    pause
    exit /b 1
)
echo [成功] 镜像导出完成！
echo.

echo [4/4] 显示镜像信息...
docker images travel-planning:latest
echo.

echo ========================================
echo 构建和导出完成！
echo ========================================
echo.
echo 生成的文件：
echo   - travel-planning-image.tar (Docker 镜像文件)
echo.
echo 使用方法：
echo   1. 导入镜像: docker load -i travel-planning-image.tar
echo   2. 运行容器: docker run -d -p 8501:8501 --name travel-planning travel-planning:latest
echo   3. 访问应用: http://localhost:8501
echo.
pause

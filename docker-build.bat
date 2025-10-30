@echo off
echo ========================================
echo CCCD Scanner - Docker Build Script
echo ========================================
echo.

echo [1/3] Building Docker image...
docker build -t cccd-scanner:latest .

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build Docker image!
    pause
    exit /b 1
)

echo.
echo [2/3] Stopping existing container (if any)...
docker stop cccd-scanner-app 2>nul
docker rm cccd-scanner-app 2>nul

echo.
echo [3/3] Starting new container...
docker run -d ^
    --name cccd-scanner-app ^
    -p 8501:8501 ^
    --restart unless-stopped ^
    cccd-scanner:latest

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to start container!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! CCCD Scanner is running!
echo ========================================
echo.
echo Access the application at: http://localhost:8501
echo.
echo Commands:
echo   View logs:    docker logs cccd-scanner-app
echo   Stop app:     docker stop cccd-scanner-app
echo   Remove app:   docker rm cccd-scanner-app
echo.
pause
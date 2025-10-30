@echo off
echo ========================================
echo CCCD Scanner - Docker Compose
echo ========================================
echo.

echo What would you like to do?
echo [1] Build and start the application
echo [2] Start the application
echo [3] Stop the application
echo [4] View logs
echo [5] Remove everything
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Building and starting application...
    docker-compose up --build -d
    goto :success
)

if "%choice%"=="2" (
    echo.
    echo Starting application...
    docker-compose up -d
    goto :success
)

if "%choice%"=="3" (
    echo.
    echo Stopping application...
    docker-compose down
    echo Application stopped.
    goto :end
)

if "%choice%"=="4" (
    echo.
    echo Showing logs (Ctrl+C to exit)...
    docker-compose logs -f
    goto :end
)

if "%choice%"=="5" (
    echo.
    echo Removing everything...
    docker-compose down -v --rmi all
    echo Everything removed.
    goto :end
)

echo Invalid choice!
goto :end

:success
echo.
echo ========================================
echo SUCCESS! CCCD Scanner is running!
echo ========================================
echo.
echo Access the application at: http://localhost:8501
echo.
echo Useful commands:
echo   View logs:        docker-compose logs -f
echo   Stop:             docker-compose down
echo   Rebuild:          docker-compose up --build -d
echo.

:end
pause
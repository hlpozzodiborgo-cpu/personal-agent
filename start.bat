@echo off
echo ================================================
echo   Investor AI
echo ================================================

if not exist "backend\venv" (
    echo Setup non complete. Lancez setup.bat d'abord.
    pause & exit /b 1
)
if not exist "frontend\node_modules" (
    echo Setup non complete. Lancez setup.bat d'abord.
    pause & exit /b 1
)

REM Liberer les ports si occupes
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr " :8000 "') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr " :3000 "') do taskkill /F /PID %%a >nul 2>&1

REM Demarrer le backend dans une nouvelle fenetre
start "Investor AI - Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"

REM Attendre que le backend demarre
timeout /t 3 /nobreak >nul

REM Demarrer le frontend dans une nouvelle fenetre
start "Investor AI - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo  Dashboard : http://localhost:3000
echo  API Docs  : http://localhost:8000/docs
echo.
echo Deux fenetres ont ete ouvertes (backend + frontend).
echo Fermez-les pour arreter l'application.
echo.
pause

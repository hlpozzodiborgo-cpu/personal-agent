@echo off
echo ================================================
echo   Setup Investor AI
echo ================================================
echo.

REM Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python non trouve. Installez-le depuis https://python.org
    pause & exit /b 1
)

REM Backend
echo [1/3] Creation de l'environnement Python...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
call venv\Scripts\deactivate.bat
cd ..

REM Copier .env si absent
if not exist backend\.env (
    copy backend\.env.example backend\.env
    echo [!] Editez backend\.env et ajoutez votre cle Finnhub
)

REM Frontend
echo [2/3] Installation des dependances Node.js...
cd frontend
call npm install
cd ..

echo.
echo [3/3] Setup termine !
echo Lancez l'application avec : start.bat
echo.
pause

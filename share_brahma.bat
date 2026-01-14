@echo off
TITLE Brahma AI - Public Share
COLOR 0A

echo.
echo ========================================================
echo        BRAHMA AI - PUBLIC SHARING MODE
echo ========================================================
echo.

echo [1/3] Starting Local AI Server...
start /B streamlit run app.py --server.headless true > NUL 2>&1

echo [2/3] Waiting for startup...
timeout /t 5 /nobreak > NUL

echo.
echo ========================================================
echo IMPORTANT: If asked for a "Tunnel Password", enter this IP:
curl -s https://api.ipify.org
echo.
echo (Highlight and Right-Click to copy the IP above)
echo ========================================================
echo.

echo [3/3] Generating Public URL...
echo.
call npx -y localtunnel --port 8501

echo.
echo Server stopped.
taskkill /IM streamlit.exe /F > NUL 2>&1
pause

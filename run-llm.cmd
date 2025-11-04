@echo off
REM run-llm.cmd — Double-click this in Explorer to start the right backend.
REM It launches the PowerShell script with a permissive policy for this run only.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-llm.ps1"
IF ERRORLEVEL 1 (
  echo.
  echo [AT-Mind] Error: LLM startup failed. See messages above.
  pause
  exit /b 1
)
echo.
echo [AT-Mind] LLM backend is up. You can now start your app.
pause

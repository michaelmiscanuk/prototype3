:: filepath: c:\Users\mmiscanuk\OneDrive\Knowledge Base\0207_GenAI\Code\CrewAI\test_prototypes\protototype3b\prototype3\safe_crewai.bat
@echo off
setlocal

:: Set environment variable to force direct Python execution
set UV_NO_HARDLINKS=1
set FORCE_DIRECT_PYTHON=1

:: Get command line arguments
set "action=%1"
set "command=%2"

:: If no arguments, show help
if "%action%"=="" (
    echo USAGE: safe_crewai.bat [flow^|run] [command]
    echo.
    echo This is a safe launcher for CrewAI that works in cloud-synced folders.
    echo Examples:
    echo   safe_crewai.bat flow kickoff  - Run flow kickoff
    echo   safe_crewai.bat run           - Run the default entry point
    exit /b 1
)

:: Process commands
if /i "%action%"=="flow" (
    if /i "%command%"=="kickoff" (
        echo Running flow kickoff safely...
        python -m prototype3.safe_launcher
    ) else (
        echo Unknown flow command: %command%
    )
) else if /i "%action%"=="run" (
    echo Running default entry point safely...
    python run_flow.py
) else (
    echo Unknown action: %action%
)

endlocal
@echo off
REM Startup script for ADK Travel Planner - Windows

echo Starting ADK Travel Planner Agents...
echo.

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found!
    echo Please create a .env file with your OPENAI_API_KEY
    pause
    exit /b 1
)

REM Load environment variables
for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do set %%a

REM Check if OPENAI_API_KEY is set
if "%OPENAI_API_KEY%"=="" (
    echo Error: OPENAI_API_KEY not set in .env file!
    echo Please add your OpenAI API key to the .env file
    pause
    exit /b 1
)

echo Environment variables loaded
echo.

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

echo Starting Flight Agent on port 8001...
start /B python -m agents.flight_agent > logs\flight_agent.log 2>&1
timeout /t 2 /nobreak > nul

echo Starting Stay Agent on port 8002...
start /B python -m agents.stay_agent > logs\stay_agent.log 2>&1
timeout /t 2 /nobreak > nul

echo Starting Activities Agent on port 8003...
start /B python -m agents.activities_agent > logs\activities_agent.log 2>&1
timeout /t 2 /nobreak > nul

echo Starting Host Agent on port 8000...
start /B python -m agents.host_agent > logs\host_agent.log 2>&1
timeout /t 3 /nobreak > nul

echo.
echo All agents started successfully!
echo.
echo View logs in the logs\ directory
echo.
echo Starting Streamlit UI...
echo Open http://localhost:8501 in your browser
echo.
echo To stop all agents, close this window or press Ctrl+C
echo.

REM Start Streamlit UI
streamlit run travel_ui.py

pause

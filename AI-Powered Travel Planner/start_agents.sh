#!/bin/bash

# Startup script for ADK Travel Planner - Mac/Linux

echo "🚀 Starting ADK Travel Planner Agents..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY not set in .env file!"
    echo "Please add your Google API key to the .env file"
    exit 1
fi

echo "✅ Environment variables loaded"
echo ""

# Function to check if port is in use
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
    return $?
}

# Function to kill process on port
kill_port() {
    if check_port $1; then
        echo "⚠️  Port $1 is in use. Killing existing process..."
        lsof -ti:$1 | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
kill_port 8000
kill_port 8001
kill_port 8002
kill_port 8003
echo ""

# Start Flight Agent
echo "✈️  Starting Flight Agent on port 8001..."
python -m agents.flight_agent > logs/flight_agent.log 2>&1 &
FLIGHT_PID=$!
sleep 2

# Start Stay Agent
echo "🏨 Starting Stay Agent on port 8002..."
python -m agents.stay_agent > logs/stay_agent.log 2>&1 &
STAY_PID=$!
sleep 2

# Start Activities Agent
echo "🗺️  Starting Activities Agent on port 8003..."
python -m agents.activities_agent > logs/activities_agent.log 2>&1 &
ACTIVITIES_PID=$!
sleep 2

# Start Host Agent
echo "🎯 Starting Host Agent on port 8000..."
python -m agents.host_agent > logs/host_agent.log 2>&1 &
HOST_PID=$!
sleep 3

echo ""
echo "✅ All agents started successfully!"
echo ""
echo "Agent Status:"
echo "  • Flight Agent (8001): PID $FLIGHT_PID"
echo "  • Stay Agent (8002): PID $STAY_PID"
echo "  • Activities Agent (8003): PID $ACTIVITIES_PID"
echo "  • Host Agent (8000): PID $HOST_PID"
echo ""
echo "📊 View logs in the logs/ directory"
echo ""
echo "🌐 Starting Streamlit UI..."
echo "   Open http://localhost:8501 in your browser"
echo ""
echo "To stop all agents, run: pkill -f 'agents.*agent'"
echo ""

# Start Streamlit UI (in foreground)
streamlit run travel_ui.py

# Cleanup on exit
trap "echo ''; echo '🛑 Stopping all agents...'; kill $FLIGHT_PID $STAY_PID $ACTIVITIES_PID $HOST_PID 2>/dev/null; exit" INT TERM

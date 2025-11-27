# ADK-Powered Multi-Agent Travel Planner

## Project Overview
A multi-agent AI travel planning system built with Google's Agent Development Kit (ADK) and the A2A (Agent-to-Agent) protocol. The system uses specialized agents to handle flights, hotels, and activities, all coordinated by a central host agent and presented through a Streamlit UI.

## Technology Stack
- **Framework**: Google Agent Development Kit (ADK)
- **LLM Provider**: OpenAI GPT-4o (model-agnostic, supports Gemini, Claude, Mistral via LiteLLM)
- **Protocol**: Agent-to-Agent (A2A) - Google's open standard for agent communication
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **HTTP Client**: httpx (async)
- **Schema Validation**: Pydantic

## Architecture
Multi-agent system with:
- **host_agent** (port 8000): Central orchestrator that coordinates all other agents
- **flight_agent** (port 8001): Recommends flight options
- **stay_agent** (port 8002): Finds hotels within budget
- **activities_agent** (port 8003): Suggests tourist activities

All agents expose a standard `/run` endpoint following the A2A protocol specification.

## Project Structure
```
ADK_travel_planner/
├── agents/
│   ├── host_agent/
│   │   ├── agent.py              # ADK agent definition with LLM model
│   │   ├── task_manager.py       # Orchestration logic (calls other agents)
│   │   ├── __main__.py           # FastAPI server entry point
│   │   └── .well-known/
│   │       └── agent.json        # A2A metadata for agent discovery
│   │
│   ├── flight_agent/
│   │   ├── agent.py              # Flight recommendation logic
│   │   ├── task_manager.py       # Wraps execute() for server
│   │   ├── __main__.py           # FastAPI server on port 8001
│   │   └── .well-known/
│   │       └── agent.json
│   │
│   ├── stay_agent/
│   │   ├── agent.py              # Hotel/accommodation finder
│   │   ├── task_manager.py
│   │   ├── __main__.py           # FastAPI server on port 8002
│   │   └── .well-known/
│   │       └── agent.json
│   │
│   └── activities_agent/
│       ├── agent.py              # Activity recommendation engine
│       ├── task_manager.py
│       ├── __main__.py           # FastAPI server on port 8003
│       └── .well-known/
│           └── agent.json
│
├── common/
│   ├── a2a_client.py             # HTTP client for calling agent endpoints
│   └── a2a_server.py             # Reusable FastAPI wrapper for /run endpoint
│
├── shared/
│   └── schemas.py                # TravelRequest Pydantic schema
│
├── travel_ui.py                  # Streamlit frontend application
├── requirements.txt
└── README.md
```

## Dependencies
```txt
google-adk
litellm
fastapi
uvicorn
httpx
pydantic
openai
streamlit
```

## Setup Instructions

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install google-adk litellm fastapi uvicorn httpx pydantic openai streamlit
```

### 2. API Key Configuration
```bash
# Set OpenAI API key (or use another provider)
export OPENAI_API_KEY="your_key_here"
```

### 3. Build Shared Components

#### Create `shared/schemas.py`
```python
from pydantic import BaseModel

class TravelRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
```

#### Create `common/a2a_client.py`
```python
import httpx

async def call_agent(url, payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json()
```

#### Create `common/a2a_server.py`
```python
from fastapi import FastAPI
import uvicorn

def create_app(agent):
    app = FastAPI()
    
    @app.post("/run")
    async def run(payload: dict):
        return await agent.execute(payload)
    
    return app
```

### 4. Build Individual Agents

Each agent follows the same structure with three main files:

#### Pattern for each agent:

**agents/[agent_name]/agent.py:**
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

# Define agent with specific instructions
[agent_name] = Agent(
    name="[agent_name]",
    model=LiteLlm("openai/gpt-4o"),
    description="[Agent description]",
    instruction="[Detailed system prompt]"
)

# Session management
session_service = InMemorySessionService()
runner = Runner(
    agent=[agent_name],
    app_name="[app_name]",
    session_service=session_service
)

USER_ID = "user_[agent_name]"
SESSION_ID = "session_[agent_name]"

# Execute function
async def execute(request):
    session_service.create_session(
        app_name="[app_name]",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    # Build prompt from request
    prompt = f"[Dynamic prompt with {request['destination']}, etc.]"
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                return parsed
            except json.JSONDecodeError:
                return {"result": response_text}
```

**agents/[agent_name]/task_manager.py:**
```python
from .agent import execute

async def run(payload):
    return await execute(payload)
```

**agents/[agent_name]/__main__.py:**
```python
from common.a2a_server import create_app
from .task_manager import run

app = create_app(agent=type("Agent", (), {"execute": run}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=[PORT_NUMBER])
```

**agents/[agent_name]/.well-known/agent.json:**
```json
{
    "name": "[agent_name]",
    "description": "[Agent description]"
}
```

### 5. Specific Agent Implementations

#### Flight Agent (`agents/flight_agent/agent.py`)
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Recommends flight options for the user.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 flight options. "
        "For each flight, provide airline, departure time, arrival time, duration, and price. "
        "Respond in JSON format using the key 'flights' with a list of flight objects."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)

USER_ID = "user_flight"
SESSION_ID = "session_flight"

async def execute(request):
    session_service.create_session(
        app_name="flight_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    prompt = (
        f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 flights, each with airline, departure time, "
        f"arrival time, duration, and price. Respond in JSON format using the key 'flights' with a list."
    )
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "flights" in parsed and isinstance(parsed["flights"], list):
                    return {"flights": parsed["flights"]}
                else:
                    return {"flights": response_text}
            except json.JSONDecodeError:
                return {"flights": response_text}
```

#### Stay Agent (`agents/stay_agent/agent.py`)
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

stay_agent = Agent(
    name="stay_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Finds hotels within budget.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 hotel options. "
        "For each hotel, provide name, location, rating, price per night, and amenities. "
        "Respond in JSON format using the key 'stays' with a list of hotel objects."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=stay_agent,
    app_name="stay_app",
    session_service=session_service
)

USER_ID = "user_stay"
SESSION_ID = "session_stay"

async def execute(request):
    session_service.create_session(
        app_name="stay_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    prompt = (
        f"User needs accommodation in {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 hotels with name, location, rating, price per night, "
        f"and amenities. Respond in JSON format using the key 'stays' with a list."
    )
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "stays" in parsed and isinstance(parsed["stays"], list):
                    return {"stays": parsed["stays"]}
                else:
                    return {"stays": response_text}
            except json.JSONDecodeError:
                return {"stays": response_text}
```

#### Activities Agent (`agents/activities_agent/agent.py`)
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

activities_agent = Agent(
    name="activities_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Suggests interesting activities for the user at a destination.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 engaging tourist or cultural activities. "
        "For each activity, provide a name, a short description, price estimate, and duration in hours. "
        "Respond in JSON format using the key 'activities' with a list of activity objects."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent,
    app_name="activities_app",
    session_service=session_service
)

USER_ID = "user_activities"
SESSION_ID = "session_activities"

async def execute(request):
    session_service.create_session(
        app_name="activities_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    prompt = (
        f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 activities, each with name, description, "
        f"price estimate, and duration. Respond in JSON format using the key 'activities' with a list."
    )
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "activities" in parsed and isinstance(parsed["activities"], list):
                    return {"activities": parsed["activities"]}
                else:
                    return {"activities": response_text}
            except json.JSONDecodeError:
                return {"activities": response_text}
```

### 6. Host Agent Implementation

#### Host Agent (`agents/host_agent/agent.py`)
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

host_agent = Agent(
    name="host_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Coordinates travel planning by calling flight, stay, and activity agents.",
    instruction=(
        "You are the host agent responsible for orchestrating trip planning tasks. "
        "You call external agents to gather flights, stays, and activities, then return a final result."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=host_agent,
    app_name="host_app",
    session_service=session_service
)

USER_ID = "user_host"
SESSION_ID = "session_host"

async def execute(request):
    session_service.create_session(
        app_name="host_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    prompt = (
        f"Plan a trip to {request['destination']} from {request['start_date']} to {request['end_date']} "
        f"within a total budget of {request['budget']}. Call the flights, stays, and activities agents for results."
    )
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            return {"summary": event.content.parts[0].text}
```

#### Host Agent Task Manager (`agents/host_agent/task_manager.py`)
```python
from common.a2a_client import call_agent

FLIGHT_URL = "http://localhost:8001/run"
STAY_URL = "http://localhost:8002/run"
ACTIVITIES_URL = "http://localhost:8003/run"

async def run(payload):
    # Print what the host agent is sending
    print("Incoming payload:", payload)
    
    # Call all agents
    flights = await call_agent(FLIGHT_URL, payload)
    stay = await call_agent(STAY_URL, payload)
    activities = await call_agent(ACTIVITIES_URL, payload)
    
    # Log outputs
    print("flights:", flights)
    print("stay:", stay)
    print("activities:", activities)
    
    # Ensure all are dicts before access
    flights = flights if isinstance(flights, dict) else {}
    stay = stay if isinstance(stay, dict) else {}
    activities = activities if isinstance(activities, dict) else {}
    
    return {
        "flights": flights.get("flights", "No flights returned."),
        "stay": stay.get("stays", "No stay options returned."),
        "activities": activities.get("activities", "No activities found.")
    }
```

### 7. Build Streamlit UI

Create `travel_ui.py`:
```python
import streamlit as st
import requests

st.set_page_config(page_title="ADK-Powered Travel Planner", page_icon="✈️")
st.title("🌍 ADK-Powered Travel Planner")

origin = st.text_input("Where are you flying from?", placeholder="e.g., New York")
destination = st.text_input("Destination", placeholder="e.g., Paris")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
budget = st.number_input("Budget (in USD)", min_value=100, step=50)

if st.button("Plan My Trip ✨"):
    if not all([origin, destination, start_date, end_date, budget]):
        st.warning("Please fill in all the details.")
    else:
        payload = {
            "origin": origin,
            "destination": destination,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "budget": budget
        }
        
        with st.spinner("Planning your perfect trip..."):
            try:
                response = requests.post("http://localhost:8000/run", json=payload, timeout=120)
                
                if response.ok:
                    data = response.json()
                    
                    st.success("✅ Your travel plan is ready!")
                    
                    # Display Flights
                    st.subheader("✈️ Flights")
                    if isinstance(data["flights"], list):
                        for i, flight in enumerate(data["flights"], 1):
                            with st.expander(f"Flight Option {i}"):
                                st.write(flight)
                    else:
                        st.markdown(data["flights"])
                    
                    # Display Stays
                    st.subheader("🏨 Stays")
                    if isinstance(data["stay"], list):
                        for i, hotel in enumerate(data["stay"], 1):
                            with st.expander(f"Hotel Option {i}"):
                                st.write(hotel)
                    else:
                        st.markdown(data["stay"])
                    
                    # Display Activities
                    st.subheader("🗺️ Activities")
                    if isinstance(data["activities"], list):
                        for i, activity in enumerate(data["activities"], 1):
                            with st.expander(f"Activity {i}"):
                                st.write(activity)
                    else:
                        st.markdown(data["activities"])
                else:
                    st.error(f"Failed to fetch travel plan. Status: {response.status_code}")
                    st.error(response.text)
            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
```

## Running the Application

### Method 1: Start All Agent Servers in Background
```bash
# Start all agents in background
uvicorn agents.host_agent.__main__:app --port 8000 &
uvicorn agents.flight_agent.__main__:app --port 8001 &
uvicorn agents.stay_agent.__main__:app --port 8002 &
uvicorn agents.activities_agent.__main__:app --port 8003 &

# Start Streamlit UI
streamlit run travel_ui.py
```

### Method 2: Start Each in Separate Terminals (Recommended for Development)
```bash
# Terminal 1 - Host Agent
uvicorn agents.host_agent.__main__:app --port 8000

# Terminal 2 - Flight Agent
uvicorn agents.flight_agent.__main__:app --port 8001

# Terminal 3 - Stay Agent
uvicorn agents.stay_agent.__main__:app --port 8002

# Terminal 4 - Activities Agent
uvicorn agents.activities_agent.__main__:app --port 8003

# Terminal 5 - Streamlit UI
streamlit run travel_ui.py
```

### Method 3: Using Process Manager (Production)
```bash
# Install pm2
npm install -g pm2

# Create ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'host_agent',
      script: 'uvicorn',
      args: 'agents.host_agent.__main__:app --port 8000'
    },
    {
      name: 'flight_agent',
      script: 'uvicorn',
      args: 'agents.flight_agent.__main__:app --port 8001'
    },
    {
      name: 'stay_agent',
      script: 'uvicorn',
      args: 'agents.stay_agent.__main__:app --port 8002'
    },
    {
      name: 'activities_agent',
      script: 'uvicorn',
      args: 'agents.activities_agent.__main__:app --port 8003'
    },
    {
      name: 'streamlit_ui',
      script: 'streamlit',
      args: 'run travel_ui.py'
    }
  ]
};

# Start all services
pm2 start ecosystem.config.js
```

## Key Features

### Multi-Agent Design
- Each agent has a **single responsibility** (flights, stays, activities)
- **Loose coupling** via HTTP/JSON communication
- **Scalable** - agents can be deployed independently
- **Maintainable** - changes to one agent don't affect others

### A2A Protocol Compliance
- Standard `/run` endpoint across all agents
- `.well-known/agent.json` metadata for discovery
- Interoperable with LangGraph, CrewAI, and other orchestrators
- JSON-based message passing

### Model-Agnostic
- Uses LiteLLM wrapper
- Easy to switch between OpenAI, Gemini, Claude, Mistral
- Just change the model string: `LiteLlm("openai/gpt-4o")`

### Production-Ready Features
- Async HTTP communication with httpx
- Schema validation with Pydantic
- Session management with InMemorySessionService
- Structured JSON responses
- Error handling and fallbacks
- Timeout management

## Customization Options

### Change LLM Provider
```python
# Use Gemini
model=LiteLlm("gemini/gemini-pro")

# Use Claude
model=LiteLlm("anthropic/claude-3-sonnet-20240229")

# Use Mistral
model=LiteLlm("mistral/mistral-medium")

# Use Local Model
model=LiteLlm("ollama/llama2")
```

### Modify Agent Instructions
Edit the `instruction` parameter in each agent's `agent.py` file to change behavior:
```python
instruction=(
    "Your custom prompt here. "
    "Specify output format, tone, constraints, etc. "
    "For structured output, explicitly request JSON format."
)
```

### Adjust Temperature and Model Parameters
```python
# In agent definition
agent = Agent(
    name="flight_agent",
    model=LiteLlm("openai/gpt-4o", temperature=0.7, max_tokens=1000),
    description="...",
    instruction="..."
)
```

### Add More Agents
1. Create new folder: `agents/new_agent/`
2. Copy structure from existing agent (agent.py, task_manager.py, __main__.py)
3. Update port number in `__main__.py`
4. Add endpoint to host_agent's task_manager.py:
   ```python
   NEW_AGENT_URL = "http://localhost:8004/run"
   new_data = await call_agent(NEW_AGENT_URL, payload)
   ```
5. Start the new agent server

## Deployment Considerations

### Cloud Deployment Options

Each agent can be deployed independently to:
- **Google Cloud Run**: Serverless container deployment
- **AWS Lambda**: With Mangum FastAPI adapter
- **Railway**: Easy deployment with GitHub integration
- **Render**: Simple web service deployment
- **Heroku**: Classic PaaS option
- **DigitalOcean App Platform**: Managed app hosting

### Containerization

**Dockerfile for individual agent:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# For flight agent (adjust port for other agents)
CMD ["uvicorn", "agents.flight_agent.__main__:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Docker Compose for local multi-agent setup:**
```yaml
version: '3.8'

services:
  host_agent:
    build: .
    command: uvicorn agents.host_agent.__main__:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FLIGHT_AGENT_URL=http://flight_agent:8001
      - STAY_AGENT_URL=http://stay_agent:8002
      - ACTIVITIES_AGENT_URL=http://activities_agent:8003
    depends_on:
      - flight_agent
      - stay_agent
      - activities_agent

  flight_agent:
    build: .
    command: uvicorn agents.flight_agent.__main__:app --host 0.0.0.0 --port 8001
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  stay_agent:
    build: .
    command: uvicorn agents.stay_agent.__main__:app --host 0.0.0.0 --port 8002
    ports:
      - "8002:8002"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  activities_agent:
    build: .
    command: uvicorn agents.activities_agent.__main__:app --host 0.0.0.0 --port 8003
    ports:
      - "8003:8003"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  streamlit_ui:
    build: .
    command: streamlit run travel_ui.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    environment:
      - HOST_AGENT_URL=http://host_agent:8000
    depends_on:
      - host_agent
```

### Environment Variables

**Create `.env` file:**
```bash
OPENAI_API_KEY=your_openai_key_here
HOST_AGENT_URL=http://localhost:8000
FLIGHT_AGENT_URL=http://localhost:8001
STAY_AGENT_URL=http://localhost:8002
ACTIVITIES_AGENT_URL=http://localhost:8003
```

**Load in Python:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

## Testing

### Test Individual Agents

**Test Flight Agent:**
```bash
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris",
    "start_date": "2025-06-01",
    "end_date": "2025-06-07",
    "budget": 2000
  }'
```

**Test Stay Agent:**
```bash
curl -X POST http://localhost:8002/run \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo",
    "start_date": "2025-07-15",
    "end_date": "2025-07-22",
    "budget": 3000
  }'
```

**Test Activities Agent:**
```bash
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Rome",
    "start_date": "2025-08-10",
    "end_date": "2025-08-17",
    "budget": 2500
  }'
```

### Test Host Agent (Full Orchestration)
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Barcelona",
    "start_date": "2025-09-01",
    "end_date": "2025-09-08",
    "budget": 2800
  }'
```

### Python Test Script

Create `test_agents.py`:
```python
import asyncio
import httpx

async def test_agent(url, name, payload):
    print(f"\nTesting {name}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    payload = {
        "destination": "London",
        "start_date": "2025-12-01",
        "end_date": "2025-12-08",
        "budget": 3500
    }
    
    await test_agent("http://localhost:8001/run", "Flight Agent", payload)
    await test_agent("http://localhost:8002/run", "Stay Agent", payload)
    await test_agent("http://localhost:8003/run", "Activities Agent", payload)
    await test_agent("http://localhost:8000/run", "Host Agent", payload)

if __name__ == "__main__":
    asyncio.run(main())
```

Run with: `python test_agents.py`

## Troubleshooting

### Common Issues

**1. Port Already in Use:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use fuser (Linux)
fuser -k 8000/tcp
```

**2. Import Errors:**
```bash
# Ensure you're in project root
pwd  # Should show your project directory

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**3. Module Not Found:**
```bash
# Reinstall dependencies
pip install --upgrade google-adk litellm fastapi uvicorn httpx pydantic openai streamlit

# Verify installation
pip list | grep -E "google-adk|litellm|fastapi"
```

**4. Agent Not Responding:**
- Check if all dependencies are installed
- Verify API key is set correctly: `echo $OPENAI_API_KEY`
- Review server logs for errors
- Test with curl to isolate UI issues

**5. JSON Parsing Errors:**
```python
# Add more explicit JSON instruction in agent
instruction=(
    "IMPORTANT: You MUST respond with valid JSON only. "
    "Use this exact format: {\"flights\": [{\"airline\": \"...\", ...}]} "
    "Do not include any text before or after the JSON."
)
```

**6. Connection Refused:**
- Ensure all agents are running: `ps aux | grep uvicorn`
- Check if ports are accessible: `netstat -an | grep LISTEN`
- Verify URLs in host_agent/task_manager.py

**7. Timeout Errors:**
```python
# Increase timeout in a2a_client.py
async def call_agent(url, payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=120.0)  # Increased
        response.raise_for_status()
        return response.json()
```

**8. API Rate Limits:**
```python
# Add retry logic
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_agent_with_retry(url, payload):
    return await call_agent(url, payload)
```

## Performance Optimization

### 1. Parallel Agent Calls
```python
import asyncio

async def run(payload):
    # Call agents in parallel instead of sequentially
    results = await asyncio.gather(
        call_agent(FLIGHT_URL, payload),
        call_agent(STAY_URL, payload),
        call_agent(ACTIVITIES_URL, payload),
        return_exceptions=True
    )
    
    flights, stay, activities = results
    
    return {
        "flights": flights.get("flights", "No flights") if isinstance(flights, dict) else "Error",
        "stay": stay.get("stays", "No stays") if isinstance(stay, dict) else "Error",
        "activities": activities.get("activities", "No activities") if isinstance(activities, dict) else "Error"
    }
```

### 2. Add Caching
```python
from functools import lru_cache
import hashlib
import json

def cache_key(payload):
    return hashlib.md5(json.dumps(payload, sort_keys=True).encode()).hexdigest()

# Simple in-memory cache
cache = {}

async def run_with_cache(payload):
    key = cache_key(payload)
    if key in cache:
        print("Returning cached result")
        return cache[key]
    
    result = await run(payload)
    cache[key] = result
    return result
```

### 3. Add Request Queuing
```python
from asyncio import Queue, create_task

request_queue = Queue(maxsize=100)

async def queue_processor():
    while True:
        payload, response_callback = await request_queue.get()
        result = await run(payload)
        response_callback(result)
        request_queue.task_done()
```

## Advanced Features

### 1. Add Authentication
```python
from fastapi import Header, HTTPException

API_KEY = "your-secret-key"

@app.post("/run")
async def run(payload: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return await agent.execute(payload)
```

### 2. Add Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def run(payload):
    logger.info(f"Received request: {payload}")
    result = await execute(payload)
    logger.info(f"Returning result: {result}")
    return result
```

### 3. Add Monitoring
```python
from prometheus_client import Counter, Histogram
import time

request_count = Counter('agent_requests_total', 'Total agent requests')
request_duration = Histogram('agent_request_duration_seconds', 'Request duration')

async def run(payload):
    request_count.inc()
    start_time = time.time()
    
    result = await execute(payload)
    
    duration = time.time() - start_time
    request_duration.observe(duration)
    
    return result
```

### 4. Add Database Storage
```python
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class TravelPlan(Base):
    __tablename__ = 'travel_plans'
    
    id = Column(Integer, primary_key=True)
    destination = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    budget = Column(Integer)
    result = Column(JSON)

engine = create_engine('sqlite:///travel_plans.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

async def run_and_save(payload):
    result = await run(payload)
    
    session = Session()
    plan = TravelPlan(
        destination=payload['destination'],
        start_date=payload['start_date'],
        end_date=payload['end_date'],
        budget=payload['budget'],
        result=result
    )
    session.add(plan)
    session.commit()
    session.close()
    
    return result
```

## Learning Resources

### Official Documentation
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol Specification](https://google.github.io/adk-docs/agent2agent/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Courses & Tutorials
- [DataCamp: Building AI Agents With Google ADK](https://www.datacamp.com/courses/building-ai-agents-with-google-adk)
- [LangGraph Tutorial](https://www.datacamp.com/tutorial/langgraph-tutorial)
- [CrewAI Tutorial](https://www.datacamp.com/tutorial/crew-ai)

### Related Tools & Frameworks
- [LangChain](https://www.langchain.com/)
- [AutoGen](https://microsoft.github.io/autogen/)
- [Semantic Kernel](https://learn.microsoft.com/en-us/semantic-kernel/)

## Next Steps & Extensions

### 1. Real API Integration
Replace LLM generation with actual API calls:
- **Flights**: Amadeus API, Skyscanner API
- **Hotels**: Booking.com API, Hotels.com API
- **Activities**: GetYourGuide API, Viator API

### 2. User Authentication
- Implement OAuth 2.0
- Store user preferences
- Save travel history

### 3. Payment Integration
- Stripe for bookings
- PayPal integration
- Price tracking and alerts

### 4. Enhanced AI Features
- Multi-turn conversations
- Context-aware recommendations
- User preference learning
- Budget optimization

### 5. Mobile App
- React Native frontend
- Push notifications
- Offline mode

### 6. Advanced Orchestration
- Conditional agent execution
- Dynamic workflow generation
- Agent health monitoring
- Fallback strategies

### 7. Analytics Dashboard
- User behavior tracking
- Popular destinations
- Conversion metrics
- Cost analysis

## Production Checklist

- [ ] Set up proper error handling and logging
- [ ] Implement rate limiting
- [ ] Add authentication and authorization
- [ ] Set up monitoring and alerting
- [ ] Configure CORS properly
- [ ] Use environment variables for all configs
- [ ] Set up CI/CD pipeline
- [ ] Implement database for persistence
- [ ] Add comprehensive testing
- [ ] Set up backup and recovery
- [ ] Document API endpoints
- [ ] Configure SSL/TLS
- [ ] Implement caching strategy
- [ ] Set up load balancing
- [ ] Plan for scaling

## Repository & References

**GitHub Repository:** [Google-Agent-Development-Kit-Demo](https://github.com/AashiDutt/Google-Agent-Development-Kit-Demo)

**Original Tutorial:** [DataCamp ADK Tutorial](https://www.datacamp.com/tutorial/agent-development-kit-adk)

---

**Built with Google ADK | A2A Protocol | FastAPI | Streamlit**

*Last Updated: November 2024*

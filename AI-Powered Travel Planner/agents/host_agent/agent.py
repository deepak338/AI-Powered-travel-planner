from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define host agent with orchestration instructions
# Using Gemini Flash for cost-effectiveness (native integration)
host_agent = Agent(
    name="host_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
        max_output_tokens=300
    ),
    description="Coordinates travel planning by calling flight, stay, and activity agents.",
    instruction=(
        "You are the host agent responsible for orchestrating trip planning tasks. "
        "You coordinate with external agents to gather flights, stays, and activities, then return a final result. "
        "Provide a brief, helpful summary of the travel plan."
    )
)

# Session management
session_service = InMemorySessionService()
runner = Runner(
    agent=host_agent,
    app_name="host_app",
    session_service=session_service
)

USER_ID = "user_host"
SESSION_ID = "session_host"

async def execute(request):
    """Execute travel planning orchestration"""
    session_service.create_session(
        app_name="host_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    origin = request.get('origin', 'your location')
    prompt = (
        f"Plan a trip from {origin} to {request['destination']} from {request['start_date']} to {request['end_date']} "
        f"within a total budget of ${request['budget']}. Coordinate with flight, stay, and activities agents for comprehensive results."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            return {"summary": event.content.parts[0].text}

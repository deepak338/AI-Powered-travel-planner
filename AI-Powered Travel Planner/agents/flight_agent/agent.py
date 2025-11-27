from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define flight agent with specific instructions
# Using Gemini Flash for cost-effectiveness (native integration)
flight_agent = Agent(
    name="flight_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
        max_output_tokens=500
    ),
    description="Recommends flight options for the user.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 flight options. "
        "For each flight, provide airline, departure time, arrival time, duration, and price. "
        "IMPORTANT: You MUST respond with valid JSON only. Be concise. "
        "Use this exact format: {\"flights\": [{\"airline\": \"...\", \"departure_time\": \"...\", "
        "\"arrival_time\": \"...\", \"duration\": \"...\", \"price\": ...}]} "
        "Do not include any text before or after the JSON."
    )
)

# Session management
session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)

USER_ID = "user_flight"
SESSION_ID = "session_flight"

async def execute(request):
    """Execute flight recommendation based on request"""
    # Build prompt from request
    origin = request.get('origin', 'your location')
    prompt = (
        f"User is flying from {origin} to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a total trip budget of ${request['budget']}. Suggest 2-3 flights, each with airline, departure time, "
        f"arrival time, duration, and price. Respond in JSON format using the key 'flights' with a list."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    # Create a new session for each request
    import uuid
    unique_session_id = f"session_flight_{uuid.uuid4().hex[:8]}"

    try:
        await session_service.create_session(
            app_name="flight_app",
            user_id=USER_ID,
            session_id=unique_session_id
        )
    except:
        # Session might already exist, continue
        pass

    async for event in runner.run_async(user_id=USER_ID, session_id=unique_session_id, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                # Try to parse as JSON
                parsed = json.loads(response_text)
                if "flights" in parsed and isinstance(parsed["flights"], list):
                    return {"flights": parsed["flights"]}
                else:
                    return {"flights": response_text}
            except json.JSONDecodeError:
                # If parsing fails, return as text
                return {"flights": response_text}

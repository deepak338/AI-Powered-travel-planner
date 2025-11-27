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

# Define activities agent with specific instructions
# Using Gemini Flash for cost-effectiveness (native integration)
activities_agent = Agent(
    name="activities_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
        max_output_tokens=500
    ),
    description="Suggests interesting activities for the user at a destination.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 engaging tourist or cultural activities. "
        "For each activity, provide a name, a short description, price estimate, and duration in hours. "
        "IMPORTANT: You MUST respond with valid JSON only. Be concise. "
        "Use this exact format: {\"activities\": [{\"name\": \"...\", \"description\": \"...\", "
        "\"price\": ..., \"duration_hours\": ...}]} "
        "Do not include any text before or after the JSON."
    )
)

# Session management
session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent,
    app_name="activities_app",
    session_service=session_service
)

USER_ID = "user_activities"
SESSION_ID = "session_activities"

async def execute(request):
    """Execute activity recommendation based on request"""
    # Build prompt from request
    prompt = (
        f"User is visiting {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a total trip budget of ${request['budget']}. Suggest 2-3 activities, each with name, description, "
        f"price estimate, and duration in hours. Respond in JSON format using the key 'activities' with a list."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    # Create a new session for each request
    import uuid
    unique_session_id = f"session_activities_{uuid.uuid4().hex[:8]}"

    try:
        await session_service.create_session(
            app_name="activities_app",
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
                if "activities" in parsed and isinstance(parsed["activities"], list):
                    return {"activities": parsed["activities"]}
                else:
                    return {"activities": response_text}
            except json.JSONDecodeError:
                # If parsing fails, return as text
                return {"activities": response_text}

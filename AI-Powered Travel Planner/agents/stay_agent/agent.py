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

# Define stay agent with specific instructions
# Using Gemini Flash for cost-effectiveness (native integration)
stay_agent = Agent(
    name="stay_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
        max_output_tokens=500
    ),
    description="Finds hotels within budget.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 hotel options. "
        "For each hotel, provide name, location, rating, price per night, and amenities. "
        "IMPORTANT: You MUST respond with valid JSON only. Be concise. "
        "Use this exact format: {\"stays\": [{\"name\": \"...\", \"location\": \"...\", "
        "\"rating\": ..., \"price_per_night\": ..., \"amenities\": [\"...\", \"...\"]}]} "
        "Do not include any text before or after the JSON."
    )
)

# Session management
session_service = InMemorySessionService()
runner = Runner(
    agent=stay_agent,
    app_name="stay_app",
    session_service=session_service
)

USER_ID = "user_stay"
SESSION_ID = "session_stay"

async def execute(request):
    """Execute hotel recommendation based on request"""
    # Build prompt from request
    prompt = (
        f"User needs accommodation in {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a total trip budget of ${request['budget']}. Suggest 2-3 hotels with name, location, rating, price per night, "
        f"and amenities. Respond in JSON format using the key 'stays' with a list."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    # Create a new session for each request
    import uuid
    unique_session_id = f"session_stay_{uuid.uuid4().hex[:8]}"

    try:
        await session_service.create_session(
            app_name="stay_app",
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
                if "stays" in parsed and isinstance(parsed["stays"], list):
                    return {"stays": parsed["stays"]}
                else:
                    return {"stays": response_text}
            except json.JSONDecodeError:
                # If parsing fails, return as text
                return {"stays": response_text}

#!/usr/bin/env python3
"""
Simple test script for ADK Travel Planner
This tests the AI agents directly without the full A2A server setup
"""

import asyncio
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
import json
import os

# Ensure GOOGLE_API_KEY is set
from dotenv import load_dotenv
load_dotenv()

async def test_flight_agent():
    """Test flight recommendations"""
    print("\n" + "="*60)
    print("Testing Flight Agent...")
    print("="*60)

    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    agent = Agent(
        name="flight_test",
        model=Gemini(model="gemini-2.5-flash", temperature=0.3, max_output_tokens=500),
        description="Flight recommender",
        instruction=(
            "Suggest 2-3 flight options in JSON format. Be concise. "
            "Format: {\"flights\": [{\"airline\": \"...\", \"departure_time\": \"...\", "
            "\"arrival_time\": \"...\", \"duration\": \"...\", \"price\": ...}]}"
        )
    )

    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="test_app", session_service=session_service)

    prompt = ("User flying from New York to Paris from 2025-06-01 to 2025-06-07, "
              "budget $2000. Suggest 2-3 flights with airline, times, duration, price in JSON.")

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    user_id = "test_user"
    session_id = "test_session"

    try:
        # Create session
        await session_service.create_session(app_name="test_app", user_id=user_id, session_id=session_id)

        # Run agent
        print("\n⏳ Calling Gemini 1.5 Flash... (this may take 10-20 seconds)")
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=message):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                print("\n✅ Flight Agent Response:")
                print(response_text)

                # Try to parse as JSON
                try:
                    parsed = json.loads(response_text)
                    print("\n✅ Successfully parsed as JSON!")
                    print(json.dumps(parsed, indent=2))
                except:
                    print("\n⚠️  Response received but not valid JSON")
                    print("(This is okay - Gemini sometimes adds extra text)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_all():
    """Run all tests"""
    print("\n🚀 ADK Travel Planner - Simple Test")
    print("="*60)
    print(f"Using Google API Key: {os.getenv('GOOGLE_API_KEY')[:20]}...")
    print(f"Model: Gemini 1.5 Flash")
    print(f"Max Tokens: 500 (Cost Control)")
    print("="*60)

    await test_flight_agent()

    print("\n" + "="*60)
    print("✅ Test Complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_all())

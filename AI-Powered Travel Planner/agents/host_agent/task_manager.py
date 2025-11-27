from common.a2a_client import call_agent
import asyncio

FLIGHT_URL = "http://localhost:8001/run"
STAY_URL = "http://localhost:8002/run"
ACTIVITIES_URL = "http://localhost:8003/run"

async def run(payload):
    """
    Orchestrate calls to all specialized agents in parallel.

    Args:
        payload: Travel request with destination, dates, and budget

    Returns:
        Combined results from all agents
    """
    # Print what the host agent is receiving
    print("=" * 50)
    print("Host Agent: Incoming payload:", payload)
    print("=" * 50)

    try:
        # Call all agents in parallel for better performance
        results = await asyncio.gather(
            call_agent(FLIGHT_URL, payload),
            call_agent(STAY_URL, payload),
            call_agent(ACTIVITIES_URL, payload),
            return_exceptions=True
        )

        flights, stay, activities = results

        # Log outputs
        print("\n" + "-" * 50)
        print("Flight Agent Response:", flights)
        print("-" * 50)
        print("Stay Agent Response:", stay)
        print("-" * 50)
        print("Activities Agent Response:", activities)
        print("-" * 50 + "\n")

        # Check for errors and provide detailed feedback
        errors = []

        if isinstance(flights, Exception):
            error_msg = f"Flight agent error: {str(flights)}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
            flights = {}
        elif not isinstance(flights, dict):
            flights = {}

        if isinstance(stay, Exception):
            error_msg = f"Stay agent error: {str(stay)}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
            stay = {}
        elif not isinstance(stay, dict):
            stay = {}

        if isinstance(activities, Exception):
            error_msg = f"Activities agent error: {str(activities)}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
            activities = {}
        elif not isinstance(activities, dict):
            activities = {}

        response = {
            "flights": flights.get("flights", "No flights returned."),
            "stay": stay.get("stays", "No stay options returned."),
            "activities": activities.get("activities", "No activities found.")
        }

        # Add error information if any agents failed
        if errors:
            response["errors"] = errors
            print(f"\n⚠️  {len(errors)} agent(s) failed")

        return response

    except Exception as e:
        error_msg = f"Error in host agent orchestration: {e}"
        print(f"❌ {error_msg}")
        return {
            "error": error_msg,
            "flights": "Error retrieving flights",
            "stay": "Error retrieving stays",
            "activities": "Error retrieving activities"
        }

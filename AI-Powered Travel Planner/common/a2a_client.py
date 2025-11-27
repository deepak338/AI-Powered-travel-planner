import httpx

async def call_agent(url: str, payload: dict):
    """
    Call an agent endpoint with the given payload.

    Args:
        url: The agent endpoint URL
        payload: The request payload

    Returns:
        The JSON response from the agent
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json()

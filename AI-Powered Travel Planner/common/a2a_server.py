from fastapi import FastAPI
import uvicorn

def create_app(agent):
    """
    Create a FastAPI app with a standard /run endpoint for A2A protocol.

    Args:
        agent: An agent object with an execute() method

    Returns:
        FastAPI application instance
    """
    app = FastAPI()

    @app.post("/run")
    async def run(payload: dict):
        """Standard A2A protocol endpoint"""
        return await agent.execute(payload)

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {"status": "healthy"}

    return app

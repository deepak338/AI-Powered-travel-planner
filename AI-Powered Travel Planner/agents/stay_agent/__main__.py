from common.a2a_server import create_app
from .task_manager import run

# Create agent wrapper class
class AgentWrapper:
    async def execute(self, payload):
        return await run(payload)

app = create_app(agent=AgentWrapper())

if __name__ == "__main__":
    import uvicorn
    print("Starting Stay Agent on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)

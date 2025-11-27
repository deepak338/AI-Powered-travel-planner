from .agent import execute

async def run(payload):
    """Run the stay agent with the given payload"""
    return await execute(payload)

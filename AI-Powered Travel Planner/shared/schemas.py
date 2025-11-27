from pydantic import BaseModel

class TravelRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
    origin: str = "New York"  # Optional field with default

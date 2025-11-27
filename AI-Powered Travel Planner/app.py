import streamlit as st
import json
import re
import os
from urllib.parse import quote
import asyncio
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- Get API Key from Streamlit Secrets or Environment ---
try:
    GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
except:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Constants for icons ---
FLIGHT_ICON_URL = "https://i.ibb.co/9g0d8x1/flight-icon.png"
HOTEL_ICON_URL = "https://i.ibb.co/jLwzS3s/hotel-icon.png"
ACTIVITY_ICON_URL = "https://i.ibb.co/dKqgBbr/activity-icon.png"

# --- Helper Functions ---
def extract_json_from_markdown(text):
    if isinstance(text, (list, dict)):
        return text
    if not isinstance(text, str):
        return text
    try:
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return text

# --- AI Agent Functions ---
@st.cache_resource
def get_agents():
    """Initialize all AI agents (cached for performance)"""
    
    # Flight Agent
    flight_agent = Agent(
        name="flight_agent",
        model=Gemini(model="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY, temperature=0.3, max_output_tokens=500),
        description="Flight recommender",
        instruction=(
            "Suggest 2-3 flight options in JSON format. Be concise. "
            "Format: {\"flights\": [{\"airline\": \"...\", \"departure_time\": \"...\", "
            "\"arrival_time\": \"...\", \"duration\": \"...\", \"price\": ...}]}"
        )
    )
    
    # Stay Agent
    stay_agent = Agent(
        name="stay_agent",
        model=Gemini(model="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY, temperature=0.3, max_output_tokens=500),
        description="Hotel recommender",
        instruction=(
            "Suggest 2-3 hotel options in JSON format. Be concise. "
            "Format: {\"stays\": [{\"name\": \"...\", \"location\": \"...\", \"rating\": ..., "
            "\"price_per_night\": ..., \"amenities\": [...]}]}"
        )
    )
    
    # Activities Agent
    activities_agent = Agent(
        name="activities_agent",
        model=Gemini(model="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY, temperature=0.3, max_output_tokens=500),
        description="Activities recommender",
        instruction=(
            "Suggest 2-3 tourist activities in JSON format. Be concise. "
            "Format: {\"activities\": [{\"name\": \"...\", \"description\": \"...\", "
            "\"price\": ..., \"duration_hours\": ...}]}"
        )
    )
    
    return flight_agent, stay_agent, activities_agent

async def get_recommendations(origin, destination, start_date, end_date, budget):
    """Get travel recommendations from all AI agents"""
    
    flight_agent, stay_agent, activities_agent = get_agents()
    
    # Create runners and sessions
    flight_runner = Runner(agent=flight_agent, app_name="flight_app", session_service=InMemorySessionService())
    stay_runner = Runner(agent=stay_agent, app_name="stay_app", session_service=InMemorySessionService())
    activities_runner = Runner(agent=activities_agent, app_name="activities_app", session_service=InMemorySessionService())
    
    # Prepare prompts
    flight_prompt = f"Flights from {origin} to {destination}, {start_date} to {end_date}, budget ${budget}"
    stay_prompt = f"Hotels in {destination}, {start_date} to {end_date}, budget ${budget}"
    activities_prompt = f"Activities in {destination}, {start_date} to {end_date}, budget ${budget}"
    
    # Run agents in parallel
    async def run_agent(runner, prompt, session_id):
        message = types.Content(role="user", parts=[types.Part(text=prompt)])
        async for event in runner.run_async(user_id="user", session_id=session_id, new_message=message):
            if event.is_final_response():
                return event.content.parts[0].text
        return "{}"
    
    # Execute all agents in parallel
    results = await asyncio.gather(
        run_agent(flight_runner, flight_prompt, "flight_session"),
        run_agent(stay_runner, stay_prompt, "stay_session"),
        run_agent(activities_runner, activities_prompt, "activities_session"),
        return_exceptions=True
    )
    
    return results

# --- UI Rendering Functions ---
def render_flight(flight_data, origin="", destination="", start_date="", end_date=""):
    flight = extract_json_from_markdown(flight_data)
    if not isinstance(flight, dict):
        st.write(flight)
        return

    price = flight.get('price')
    price_str = f"${price:,.2f}" if price else "N/A"
    google_flights_url = f"https://www.google.com/travel/flights?q=flights+from+{quote(origin)}+to+{quote(destination)}+{start_date}+{end_date}"

    st.markdown(f"""
        <div class="card">
            <div class="card-header">
                <img src="{FLIGHT_ICON_URL}" class="card-icon">
                <div class="card-title">{flight.get('airline', 'N/A')}</div>
            </div>
            <div class="card-body">
                <div class="card-text"><strong>From:</strong> {flight.get('departure_time', 'N/A')}</div>
                <div class="card-text"><strong>To:</strong> {flight.get('arrival_time', 'N/A')}</div>
                <div class="card-text"><strong>Duration:</strong> {flight.get('duration', 'N/A')}</div>
            </div>
            <div class="card-footer">
                <div class="price-tag">{price_str}</div>
                <div class="book-now-button-container">
                    <a href="{google_flights_url}" target="_blank" class="book-now-button">Search Flights</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_stay(stay_data, destination="", start_date="", end_date=""):
    stay = extract_json_from_markdown(stay_data)
    if not isinstance(stay, dict):
        st.write(stay)
        return

    price = stay.get('price_per_night')
    price_str = f"${price:,.2f}" if price else "N/A"
    rating = stay.get('rating', 0)
    try:
        rating_stars = '⭐' * int(float(rating))
    except (ValueError, TypeError):
        rating_stars = str(rating)

    location = stay.get('location', destination)
    booking_url = f"https://www.booking.com/searchresults.html?ss={quote(location)}&checkin={start_date}&checkout={end_date}"

    st.markdown(f"""
        <div class="card">
            <div class="card-header">
                <img src="{HOTEL_ICON_URL}" class="card-icon">
                <div class="card-title">{stay.get('name', 'N/A')}</div>
            </div>
            <div class="card-body">
                <div class="card-text"><strong>Location:</strong> {stay.get('location', 'N/A')}</div>
                <div class="card-text"><strong>Rating:</strong> {rating_stars}</div>
                <div class="card-text"><strong>Amenities:</strong> {', '.join(stay.get('amenities', []))}</div>
            </div>
            <div class="card-footer">
                <div class="price-tag">{price_str} / night</div>
                <div class="book-now-button-container">
                    <a href="{booking_url}" target="_blank" class="book-now-button">Search Hotels</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_activity(activity_data, destination=""):
    activity = extract_json_from_markdown(activity_data)
    if not isinstance(activity, dict):
        st.write(activity)
        return

    price = activity.get('price')
    price_str = f"${price:,.2f}" if price else "N/A"
    activity_name = activity.get('name', '')
    search_query = f"{activity_name} {destination}"
    google_search_url = f"https://www.google.com/search?q={quote(search_query)}"

    st.markdown(f"""
        <div class="card">
            <div class="card-header">
                <img src="{ACTIVITY_ICON_URL}" class="card-icon">
                <div class="card-title">{activity.get('name', 'N/A')}</div>
            </div>
            <div class="card-body">
                <div class="card-text">{activity.get('description', 'N/A')}</div>
            </div>
            <div class="card-footer">
                <div class="price-tag">{price_str}</div>
                <div class="book-now-button-container">
                    <a href="{google_search_url}" target="_blank" class="book-now-button">More Info</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Page Configuration ---
st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

# --- Styling ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Poppins', sans-serif; }
        
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-attachment: fixed;
        }
        
        [data-testid="stHeader"] { background-color: transparent; }
        
        .main .block-container { padding: 2rem 3rem; max-width: 1400px; }
        
        .hero-header { text-align: center; margin-bottom: 3rem; padding: 2rem 0; }
        
        .main-title {
            font-size: 4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            text-shadow: 0 4px 6px rgba(0,0,0,0.1);
            letter-spacing: -1px;
        }
        
        .subtitle {
            font-size: 1.3rem;
            color: #ffffff;
            font-weight: 300;
            opacity: 0.95;
        }
        
        .stForm {
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2.5rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 3rem;
        }
        
        .stTextInput > div > div > input,
        .stDateInput > div > div > input,
        .stNumberInput > div > div > input {
            border-radius: 12px;
            border: 2px solid #e0e0e0;
            padding: 0.8rem 1rem;
            font-size: 1.05rem;
            font-weight: 500;
            transition: all 0.3s ease;
            background-color: #ffffff !important;
            color: #1a202c !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stDateInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background-color: #ffffff !important;
            color: #1a202c !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #a0aec0 !important;
            opacity: 1;
        }
        
        .stTextInput label,
        .stDateInput label,
        .stNumberInput label {
            font-weight: 600;
            color: #2d3748;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 1.2rem;
            font-weight: 600;
            padding: 0.9rem 2.5rem;
            border-radius: 12px;
            border: none;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1.5rem;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.5);
        }
        
        .element-container .stAlert {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            border-radius: 12px;
            border: none;
            padding: 1.2rem;
            font-weight: 500;
            box-shadow: 0 10px 25px rgba(17, 153, 142, 0.3);
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 2.5rem;
            margin-top: 2rem;
        }
        
        .column h3 {
            color: #ffffff;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            padding-bottom: 0.8rem;
            border-bottom: 3px solid rgba(255, 255, 255, 0.3);
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .card {
            background: white;
            border-radius: 18px;
            padding: 1.8rem;
            margin-bottom: 1.8rem;
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            display: flex;
            flex-direction: column;
            height: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        .card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 25px 50px rgba(102, 126, 234, 0.25);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.2rem;
        }
        
        .card-icon {
            width: 50px;
            height: 50px;
            margin-right: 1rem;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }
        
        .card-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1a202c;
            line-height: 1.3;
        }
        
        .card-body {
            flex-grow: 1;
            margin-bottom: 1.2rem;
        }
        
        .card-text {
            color: #4a5568;
            margin-bottom: 0.8rem;
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        .card-text strong {
            color: #2d3748;
            font-weight: 600;
        }
        
        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 2px solid #f0f0f0;
            padding-top: 1.2rem;
            margin-top: auto;
        }
        
        .price-tag {
            font-size: 1.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .book-now-button-container {
            text-align: right;
        }
        
        .book-now-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.7rem 1.5rem;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .book-now-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            color: white;
            text-decoration: none;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- Hero Header ---
st.markdown("""
    <div class="hero-header">
        <h1 class="main-title">✈️ AI Travel Planner</h1>
        <p class="subtitle">Plan your perfect trip with AI-powered recommendations</p>
    </div>
""", unsafe_allow_html=True)

# --- Input Form ---
with st.form(key="trip_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        origin = st.text_input("From", placeholder="e.g., New York", value="New York")
        destination = st.text_input("To", placeholder="e.g., Paris")
    with c2:
        from datetime import date
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today())
    with c3:
        budget = st.number_input("Budget (USD)", min_value=100, step=100, value=2000)

    submit_button = st.form_submit_button(label='✨ Plan My Trip', use_container_width=True)

# --- Process Form ---
if submit_button:
    if not all([origin, destination, start_date, end_date, budget]):
        st.warning("⚠️ Please fill in all the details.")
    elif end_date < start_date:
        st.error("❌ End date must be after start date.")
    elif not GOOGLE_API_KEY:
        st.error("❌ Google API Key not configured. Please add it to Streamlit secrets.")
    else:
        with st.spinner("🔮 Planning your perfect trip with AI..."):
            try:
                # Get recommendations from AI agents
                results = asyncio.run(get_recommendations(
                    origin, destination, 
                    str(start_date), str(end_date), 
                    budget
                ))
                
                # Parse results
                flights_text, stays_text, activities_text = results
                
                flights_data = extract_json_from_markdown(flights_text)
                stays_data = extract_json_from_markdown(stays_text)
                activities_data = extract_json_from_markdown(activities_text)
                
                # Extract arrays
                flights = flights_data.get("flights", []) if isinstance(flights_data, dict) else []
                stays = stays_data.get("stays", []) if isinstance(stays_data, dict) else []
                activities = activities_data.get("activities", []) if isinstance(activities_data, dict) else []
                
                st.success("✅ Your travel plan is ready!")
                
                # Display results
                st.markdown('<div class="results-grid">', unsafe_allow_html=True)
                
                # Flights
                if flights and isinstance(flights, list):
                    st.markdown('<div class="column"><h3>✈️ Flights</h3>', unsafe_allow_html=True)
                    for flight in flights:
                        render_flight(flight, origin, destination, str(start_date), str(end_date))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Stays
                if stays and isinstance(stays, list):
                    st.markdown('<div class="column"><h3>🏨 Accommodations</h3>', unsafe_allow_html=True)
                    for stay in stays:
                        render_stay(stay, destination, str(start_date), str(end_date))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Activities
                if activities and isinstance(activities, list):
                    st.markdown('<div class="column"><h3>🗺️ Activities</h3>', unsafe_allow_html=True)
                    for activity in activities:
                        render_activity(activity, destination)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.error("Please make sure your Google API key is configured correctly.")

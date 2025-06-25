

import streamlit as st
import json
import os
from serpapi import GoogleSearch
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini
from datetime import datetime

# Set up Streamlit UI with a travel-friendly theme
st.set_page_config(page_title="🐝GooBee", layout="wide")
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ff5733;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #555;
        }
        .stSlider > div {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and subtitle
st.markdown('<h1 class="title"> 🐝GooBee: buzz the world, Honey-sweet savings, every trip 💰  </h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle" style="color:#fff;">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities within your budget.</p>', unsafe_allow_html=True)
# User Inputs Section
st.markdown("### 🌍 Where are you headed?")
departure_city = st.text_input("🏙️ Departure City:", "Mumbai")
destination_city = st.text_input("🏙️ Destination City:", "Delhi")

# Budget Input
budget = st.number_input("💰 Total Trip Budget (INR):", min_value=0, value=50000, step=1000)

# Travel Theme
travel_theme = st.selectbox(
    "🎭 Select Your Travel Theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"]
)






# Helper to format datetime
def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")
    except:
        return "N/A"


departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

activity_preferences = st.text_area(
    "🌍 What activities do you enjoy? (e.g., relaxing on the beach, exploring historical sites, nightlife, adventure)",
    "Relaxing on the beach, exploring historical sites"
)


# Sidebar Setup

logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
st.sidebar.image(logo_path, use_container_width=True)

st.sidebar.subheader("Personalize Your Trip")

# Preferred hotel rating
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

# Packing Checklist
st.sidebar.subheader("🎒 Packing Checklist")
packing_list = {
    "👕 Clothes": True,
    "🩴 Comfortable Footwear": True,
    "🕶️ Sunglasses & Sunscreen": False,
    "📖 Travel Guidebook": False,
    "💊 Medications & First-Aid": True
}
for item, checked in packing_list.items():
    st.sidebar.checkbox(item, value=checked)

# Travel Essentials
st.sidebar.subheader("🛂 Travel Essentials")
visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")

# API Keys
SERPAPI_KEY = "402dad71388beeed3b78e7c73032c6ecf626f440b8bbb98de907ef38d09fb7c9"
GOOGLE_API_KEY = "AIzaSyC7KTV5yTKgkrcluw_5MHOL0YNHQYN47WU"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["SERPAPI_KEY"] = SERPAPI_KEY

# Divider for aesthetics
st.markdown("---")

# Option to travel by flight
travel_by_flight = st.checkbox("✈️ Do you want us to find the best flight deals ?", value=True)
if travel_by_flight:
    iata_departure = st.text_input("🛫 Departure IATA Code: ( eg : BOM for Mumbai)")
    iata_destination = st.text_input("🛬 Destination IATA Code: (eg: DEL for DELHI)" )

# Divider for aesthetics
st.markdown("---")

# Banner
st.markdown(
    f"""
    <div style="
        text-align: center;
        padding: 15px;
        background-color: #ffecd1;
        color: #333;
        border-radius: 10px;
        margin-top: 20px;
    ">
        <h3 style="margin:0;">🌟 Your {travel_theme} to {destination_city} is about to begin! 🌟</h3>
        <p style="margin:5px 0;">Budget: INR {budget}</p>
        <p style="margin:5px 0; font-style: italic;">Let us find the best recommendations for your unforgettable journey.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Functions to fetch and process flights
def fetch_flights(dep, arr, dep_date, ret_date):
    params = {
        "engine": "google_flights",
        "departure_id": dep,
        "arrival_id": arr,
        "outbound_date": str(dep_date),
        "return_date": str(ret_date),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    return GoogleSearch(params).get_dict()

def extract_cheapest_flights(flight_data):
    best = flight_data.get("best_flights", [])
    return sorted(best, key=lambda x: x.get("price", float("inf")))[:3]

# AI Agents setup
researcher = Agent(
    name="Researcher",
    instructions=[
        "Identify the travel destination specified by the user.",
        "Gather detailed information on the destination, including climate, culture, and safety tips.",
        "Find popular attractions, landmarks, and must-visit places.",
        "Search for activities that match the user’s interests and travel style.",
        "Prioritize information from reliable sources and official travel guides.",
        "Provide well-structured summaries with key insights and recommendations."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
    add_datetime_to_instructions=True,
)

planner = Agent(
    name="Planner",
    instructions=[
        "Gather details about the user's travel preferences and budget.",
        "Create a detailed itinerary with scheduled activities and estimated costs.",
        "Ensure the itinerary includes transportation options and travel time estimates.",
        "Optimize the schedule for convenience and enjoyment.",
        "Present the itinerary in a structured format."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    add_datetime_to_instructions=True,
)

hotel_restaurant_finder = Agent(
    name="Hotel & Restaurant Finder",
    instructions=[
        "Identify key locations in the user's travel itinerary.",
        "Search for highly rated hotels near those locations.",
        "Search for top-rated restaurants based on cuisine preferences and proximity.",
        "Prioritize results based on user preferences, ratings, and availability.",
        "Provide direct booking links or reservation options where possible."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
    add_datetime_to_instructions=True,
)

# Generate Travel Plan
if st.button("🚀 Generate Travel Plan"):
    cheapest_flights = []
    # Fetch flights if opted
    if travel_by_flight:
        if iata_departure and iata_destination:
            with st.spinner("✈️ Fetching best flight options..."):
                data = fetch_flights(iata_departure, iata_destination, departure_date, return_date)
                cheapest_flights = extract_cheapest_flights(data)
                cheapest_flights = [f for f in cheapest_flights if f.get("price", 0) <= budget]
        else:
            st.warning("Please enter both departure and destination IATA codes for flights.")

    # AI Research
    with st.spinner("🔍 Researching best attractions & activities..."):
        research_prompt = (
            f"Research the best attractions and activities in {destination_city} for a {travel_theme.lower()} trip. "
            f"The traveler enjoys: {activity_preferences}. Budget: INR {budget}. "
            f"Hotel Rating: {hotel_rating}."
        )
        research_results = researcher.run(research_prompt, stream=False)

    # Hotel & Restaurant Search
    with st.spinner("🏨 Searching for hotels & restaurants..."):
        hotel_restaurant_prompt = (
            f"Find the best hotels and restaurants near popular attractions in {destination_city} for a {travel_theme.lower()} trip. "
            f"Budget: INR {budget}. Hotel Rating: {hotel_rating}. Preferred activities: {activity_preferences}."
        )
        hotel_restaurant_results = hotel_restaurant_finder.run(hotel_restaurant_prompt, stream=False)

    # Itinerary Planning
    with st.spinner("🗺️ Creating your personalized itinerary..."):
        planning_prompt = (
            f"Based on the following data, create an itinerary for a {travel_theme.lower()} trip to {destination_city} within a budget of INR {budget}. "
            f"The traveler enjoys: {activity_preferences}. Hotel Rating: {hotel_rating}. "
            f"Research: {research_results.content}. Flights: {json.dumps(cheapest_flights)}. "
            f"Hotels & Restaurants: {hotel_restaurant_results.content}."
            f"Using this and your own knowledge, create a well-structured travel itinerary including: Visa and weather advice, Transportation, **Any major local events**"
            f"Include: a short city intro , a **Detailed** Day-wise **WITH DATE** plan with time blocks and ensure places are not repeated,Tips on transport, food, and events,Budget breakdown under {budget} Rupees"
            f"Use markdown formatting."
            
            
        )
        itinerary = planner.run(planning_prompt, stream=False)

    # Display Flight Options
    if travel_by_flight:
        st.subheader("✈️ Cheapest Flight Options Within Budget")
        if cheapest_flights:
            cols = st.columns(len(cheapest_flights))
            for idx, flight in enumerate(cheapest_flights):
                with cols[idx]:
                    logo = flight.get("airline_logo", "")
                    info = flight.get("flights", [{}])
                    dep = info[0].get("departure_airport", {})
                    arr = info[-1].get("arrival_airport", {})
                    dep_time = format_datetime(dep.get("time", "N/A"))
                    arr_time = format_datetime(arr.get("time", "N/A"))
                    price = flight.get("price", "Not Available")
                    duration = flight.get("total_duration", "N/A")
                    token = flight.get("departure_token", "")
                    booking_token = None
                    if token:
                        out = GoogleSearch({**{
                            "engine": "google_flights",
                            "departure_id": iata_departure,
                            "arrival_id": iata_destination,
                            "outbound_date": str(departure_date),
                            "return_date": str(return_date),
                            "currency": "INR",
                            "hl": "en",
                            "api_key": SERPAPI_KEY
                        }, "departure_token": token}).get_dict()
                        booking_token = out['best_flights'][idx].get('booking_token')
                    link = f"https://www.google.com/travel/flights?tfs={booking_token}" if booking_token else "#"
                    st.markdown(
                        f"""
                        <div style="border:2px solid #ddd;border-radius:10px;padding:15px;text-align:center;color:#333;box-shadow:2px 2px 10px rgba(0,0,0,0.1);background-color:#f9f9f9;margin-bottom:20px;">
                            <img src="{logo}" width="100" alt="Logo" />
                            <h3 style="margin:10px 0;color:#333;">{flight.get('airline','Unknown')}</h3>
                            <p><strong>Departure:</strong> {dep_time}</p>
                            <p><strong>Arrival:</strong> {arr_time}</p>
                            <p><strong>Duration:</strong> {duration} min</p>
                            <h2 style="color:#008000;">💰 {price}</h2>
                            <a href="{link}" target="_blank" style="display:inline-block;padding:10px 20px;font-size:16px;font-weight:bold;color:#fff;background-color:#007bff;text-decoration:none;border-radius:5px;margin-top:10px;">🔗 Book Now</a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.warning("⚠️ No flights found within your budget.")

    # Display Hotels & Itinerary
    st.subheader("🏨 Hotels & Restaurants")
    st.write(hotel_restaurant_results.content)

    st.subheader("🗺️ Your Personalized Itinerary")
    st.write(itinerary.content)

    st.success("✅ Travel plan generated successfully!")

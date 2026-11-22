from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import date
import requests
import os

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0
)

class EventDetails(BaseModel):
    event_type: str = Field(description="Type of event")
    event_date: str = Field(description="Date in YYYY-MM-DD format, or 'not specified'")
    location: str = Field(description="City or location, or 'not specified'")
    indoor_outdoor_preference: str = Field(description="Indoor, outdoor, or flexible")

class WeatherData(BaseModel):
    temperature: str = Field(description="Forecast temperature and unit")
    precipitation_chance: str = Field(description="Chance of precipitation as a percentage or unavailable")
    conditions: str = Field(description="Weather conditions or unavailable")

event_parser = PydanticOutputParser(pydantic_object=EventDetails)
event_prompt = PromptTemplate(
    template="""Extract the event details from the description. Do not guess missing values.
Use YYYY-MM-DD for a clear date; otherwise use 'not specified'.

Event description:
{event_description_text}

{format_instructions}
""",
    input_variables=["event_description_text"],
    partial_variables={"format_instructions": event_parser.get_format_instructions()}
)
event_chain = event_prompt | llm | event_parser

weather_parser = PydanticOutputParser(pydantic_object=WeatherData)

# Open-Meteo provides a public forecast API. Forecast availability depends on the date.
weather_query_prompt = PromptTemplate.from_template(
    "Create a weather lookup query for location '{location}' on date '{event_date}'."
)

def get_weather(event):
    if event.location.lower() == "not specified" or event.event_date.lower() == "not specified":
        return WeatherData(
            temperature="Unavailable: event location or date was not specified",
            precipitation_chance="Unavailable",
            conditions="Please provide a location and date"
        )

    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": event.location, "count": 1, "language": "en", "format": "json"},
            timeout=15
        )
        geo.raise_for_status()
        places = geo.json().get("results", [])
        if not places:
            raise ValueError("Location not found")
        place = places[0]

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "daily": "temperature_2m_max,precipitation_probability_max,weather_code",
                "timezone": "auto",
                "start_date": event.event_date,
                "end_date": event.event_date
            },
            timeout=15
        )
        weather_response.raise_for_status()
        daily = weather_response.json().get("daily", {})
        if not daily.get("time"):
            raise ValueError("Forecast is not available for this date")

        temp = daily.get("temperature_2m_max", [None])[0]
        rain = daily.get("precipitation_probability_max", [None])[0]
        code = daily.get("weather_code", [None])[0]
        descriptions = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
            55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 80: "Rain showers",
            81: "Moderate rain showers", 82: "Violent rain showers", 95: "Thunderstorm"
        }
        return WeatherData(
            temperature=f"{temp} °C" if temp is not None else "Unavailable",
            precipitation_chance=f"{rain}%" if rain is not None else "Unavailable",
            conditions=descriptions.get(code, f"Weather code {code}" if code is not None else "Unavailable")
        )
    except Exception as error:
        return WeatherData(
            temperature="Unavailable",
            precipitation_chance="Unavailable",
            conditions=f"Could not retrieve forecast: {error}"
        )

recommendation_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an event planning assistant. Give a practical recommendation: proceed as planned, reschedule, or move indoors. Consider event preference and weather data. If weather is unavailable, clearly say so and do not pretend to know the forecast."),
    ("human", "Event details:\n{event_data}\n\nWeather data:\n{weather_data}\n\nWrite a concise recommendation for the organizer.")
])
recommendation_chain = recommendation_prompt | llm | StrOutputParser()

event_description_text = "We are planning an outdoor community picnic in Pune on 2026-10-25. Moving indoors is possible."
event = event_chain.invoke({"event_description_text": event_description_text})
print("Step 1 - Event Details:")
print(event.model_dump_json(indent=2))

weather = get_weather(event)
print("\nStep 2 - Weather Data:")
print(weather.model_dump_json(indent=2))

recommendation = recommendation_chain.invoke({
    "event_data": event.model_dump_json(),
    "weather_data": weather.model_dump_json()
})
print("\nStep 3 - Recommendation:")
print(recommendation)

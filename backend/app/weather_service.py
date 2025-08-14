import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    async def get_current_weather(self, lat: float, lng: float) -> Dict:
        """Get current weather for coordinates"""
        if not self.api_key:
            return {"error": "Weather API key not configured"}
            
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lng,
                "appid": self.api_key,
                "units": "imperial"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 10000) / 1000,
                "conditions": data["weather"][0]["main"]
            }
            
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return {"error": "Failed to fetch weather data"}

    async def get_route_weather_impact(self, route_stops: List[Dict]) -> Dict:
        """Analyze weather impact on route"""
        if not self.api_key:
            return {"impact": "unknown", "message": "Weather service unavailable"}
            
        try:
            if not route_stops:
                return {"impact": "none", "message": "No stops to analyze"}
                
            first_stop = route_stops[0]
            coords = first_stop.get("coordinates", {})
            if not coords:
                return {"impact": "unknown", "message": "No coordinates available"}
                
            weather = await self.get_current_weather(coords["lat"], coords["lng"])
            
            if "error" in weather:
                return {"impact": "unknown", "message": weather["error"]}
            
            temp = weather["temperature"]
            conditions = weather["conditions"].lower()
            wind_speed = weather["wind_speed"]
            
            impact_level = "none"
            delay_minutes = 0
            messages = []
            
            if temp > 90:
                impact_level = "high"
                delay_minutes += 15
                messages.append("High temperature may accelerate ice melting")
            elif temp > 80:
                impact_level = "medium"
                delay_minutes += 5
                messages.append("Warm weather - monitor ice integrity")
            
            if any(cond in conditions for cond in ["rain", "snow", "storm"]):
                impact_level = "high"
                delay_minutes += 20
                messages.append("Adverse weather conditions - drive carefully")
            
            if wind_speed > 25:
                impact_level = "medium" if impact_level == "none" else "high"
                delay_minutes += 10
                messages.append("High winds - secure loads properly")
            
            return {
                "impact": impact_level,
                "delay_minutes": delay_minutes,
                "messages": messages,
                "weather_summary": f"{weather['description']}, {temp}°F"
            }
            
        except Exception as e:
            logger.error(f"Route weather analysis error: {e}")
            return {"impact": "unknown", "message": "Weather analysis failed"}

router = APIRouter()
weather_service = WeatherService()

@router.get("/current/{lat}/{lng}")
async def get_current_weather_endpoint(lat: float, lng: float):
    """Get current weather for coordinates"""
    return await weather_service.get_current_weather(lat, lng)

@router.get("/route-impact")
async def get_route_weather_impact_endpoint(route_stops: List[Dict]):
    """Analyze weather impact on route"""
    return await weather_service.get_route_weather_impact(route_stops)

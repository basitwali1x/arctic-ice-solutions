from fastapi import FastAPI, APIRouter, HTTPException
import requests
import os
from typing import Dict, List, Any

app = FastAPI(title="Arctic Ice Weather Service")
router = APIRouter()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
API_URL = "https://api.yourchoiceice.com/weather"

@router.get("/forecast")
async def get_forecast(lat: float, lon: float) -> Dict[str, Any]:
    """Get weather forecast for route optimization"""
    if not OPENWEATHER_KEY:
        raise HTTPException(status_code=500, detail="OpenWeather API key not configured")
    
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=imperial"
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "current": data.get("current", {}),
            "hourly": data.get("hourly", [])[:24],
            "daily": data.get("daily", [])[:7],
            "alerts": data.get("alerts", [])
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")

@router.get("/route-impact")
async def get_route_impact(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Dict[str, Any]:
    """Analyze weather impact on delivery routes"""
    try:
        start_weather = await get_forecast(start_lat, start_lon)
        end_weather = await get_forecast(end_lat, end_lon)
        
        impact_score = 0
        warnings = []
        
        for weather in [start_weather["current"], end_weather["current"]]:
            temp = weather.get("temp", 70)
            if temp > 90:
                impact_score += 2
                warnings.append("High temperature may affect ice quality")
            elif temp < 32:
                impact_score += 1
                warnings.append("Freezing conditions - drive carefully")
            
            if weather.get("weather", [{}])[0].get("main") in ["Rain", "Snow", "Thunderstorm"]:
                impact_score += 3
                warnings.append("Severe weather conditions")
        
        return {
            "impact_score": min(impact_score, 10),
            "warnings": warnings,
            "recommendation": "normal" if impact_score < 3 else "caution" if impact_score < 6 else "delay",
            "start_weather": start_weather["current"],
            "end_weather": end_weather["current"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route impact analysis error: {str(e)}")

app.include_router(router, prefix="/weather")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

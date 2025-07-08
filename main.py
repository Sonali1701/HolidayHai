from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dateutil import parser
from datetime import datetime, timedelta
import httpx

app = FastAPI(
    title="Long Weekend API Service",
    description="Returns long weekends for a given country and year",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

HOLIDAY_API_URL = "https://date.nager.at/api/v3/PublicHolidays"

def get_consecutive_non_working_days(holidays, year):
    weekends = []
    holiday_dates = set(parser.parse(h["date"]).date() for h in holidays)
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()
    current = start_date

    while current <= end_date:
        if current.weekday() == 5:
            day1 = current
            day2 = current + timedelta(days=1)
            day3 = current + timedelta(days=2)
            if any(d in holiday_dates for d in [day1, day2, day3]):
                weekends.append({"start_date": str(day1), "end_date": str(day3), "length": 3})
            prev_day = current - timedelta(days=1)
            if prev_day >= start_date and any(d in holiday_dates for d in [prev_day, current, day2]):
                weekends.append({"start_date": str(prev_day), "end_date": str(day2), "length": 3})
            day4 = current + timedelta(days=2)
            if prev_day >= start_date and any(d in holiday_dates for d in [prev_day, current, day2, day4]):
                weekends.append({"start_date": str(prev_day), "end_date": str(day4), "length": 4})
        current += timedelta(days=1)
    unique = {(w["start_date"], w["end_date"]): w for w in weekends}
    return list(unique.values())

@app.get("/long-weekends/{country_code}")
async def get_all_long_weekends(country_code: str):
    current_year = datetime.utcnow().year
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{HOLIDAY_API_URL}/{current_year}/{country_code.upper()}")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Error fetching holidays")
        holidays = resp.json()
    long_weekends = get_consecutive_non_working_days(holidays, current_year)
    return {"year": current_year, "country": country_code.upper(), "long_weekends": long_weekends}

@app.get("/next-long-weekend/{country_code}")
async def get_next_long_weekend(country_code: str):
    now = datetime.utcnow().date()
    current_year = now.year
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{HOLIDAY_API_URL}/{current_year}/{country_code.upper()}")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Error fetching holidays")
        holidays = resp.json()
    long_weekends = get_consecutive_non_working_days(holidays, current_year)
    future = [w for w in long_weekends if parser.parse(w["start_date"]).date() >= now]
    if not future:
        return {"message": "No upcoming long weekends found"}
    next_one = sorted(future, key=lambda x: x["start_date"])[0]
    return {"next_long_weekend": next_one}

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, country_code: str = None, action: str = None):
    context = {"request": request}
    if country_code and action:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{HOLIDAY_API_URL}/{datetime.utcnow().year}/{country_code.upper()}"
                )
                if resp.status_code != 200:
                    context["error"] = f"Error fetching holidays (status {resp.status_code})"
                    return templates.TemplateResponse("index.html", context)
                holidays = resp.json()
            long_weekends = get_consecutive_non_working_days(
                holidays, datetime.utcnow().year
            )
            if action == "all":
                if long_weekends:
                    context["long_weekends"] = long_weekends
                else:
                    context["message"] = "No long weekends found."
            elif action == "next":
                now = datetime.utcnow().date()
                future = [w for w in long_weekends if parser.parse(w["start_date"]).date() >= now]
                if future:
                    next_one = sorted(future, key=lambda x: x["start_date"])[0]
                    context["long_weekends"] = [next_one]
                else:
                    context["message"] = "No upcoming long weekends."
        except Exception as e:
            context["error"] = f"Unexpected error: {e}"
    return templates.TemplateResponse("index.html", context)

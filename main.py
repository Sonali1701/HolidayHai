from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from dateutil import parser
import httpx

app = FastAPI(
    title="Long Weekend API Service",
    description="Returns long weekends for a given country and year",
    version="1.0.0"
)

# Directory containing index.html
templates = Jinja2Templates(directory="templates")

# API base URL
HOLIDAY_API_URL = "https://date.nager.at/api/v3/PublicHolidays"


def find_long_weekends(holidays, year):
    """
    long weekends:
    - Friday–Sunday (3 days)
    - Friday–Monday (4 days)
    - Saturday–Monday (3 days)
    Must include at least one public holiday.
    """
    weekends = []

    # Convert holiday strings to set of date objects
    holiday_dates = set(parser.parse(h["date"]).date() for h in holidays)

    # Scan through the whole year
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()

    current = start_date

    while current <= end_date:
        weekday = current.weekday()

        if weekday == 4:  # Friday
            friday = current
            saturday = friday + timedelta(days=1)
            sunday = friday + timedelta(days=2)
            monday = friday + timedelta(days=3)

            # Friday–Sunday
            if any(d in holiday_dates for d in [friday, saturday, sunday]):
                weekends.append({"start_date": str(friday), "end_date": str(sunday), "length": 3})

            # Friday–Monday
            if any(d in holiday_dates for d in [friday, saturday, sunday, monday]):
                weekends.append({"start_date": str(friday), "end_date": str(monday), "length": 4})

        if weekday == 5:  # Saturday
            saturday = current
            sunday = saturday + timedelta(days=1)
            monday = saturday + timedelta(days=2)

            # Saturday–Monday
            if any(d in holiday_dates for d in [saturday, sunday, monday]):
                weekends.append({"start_date": str(saturday), "end_date": str(monday), "length": 3})

        current += timedelta(days=1)

    # Remove duplicates by start and end date
    unique_weekends = {(w["start_date"], w["end_date"]): w for w in weekends}
    return list(unique_weekends.values())


@app.get("/long-weekends/{country_code}")
async def get_long_weekends(country_code: str):
    current_year = datetime.utcnow().year
    async with httpx.AsyncClient() as client:
        url = f"{HOLIDAY_API_URL}/{current_year}/{country_code.upper()}"
        resp = await client.get(url)

        if resp.status_code == 204:
            raise HTTPException(status_code=404, detail=f"No holiday data for {country_code.upper()}")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Error fetching holidays")

        holidays = resp.json()

    long_weekends = find_long_weekends(holidays, current_year)

    return {
        "year": current_year,
        "country": country_code.upper(),
        "long_weekends": long_weekends
    }


@app.get("/next-long-weekend/{country_code}")
async def get_next_long_weekend(country_code: str):
    today = datetime.utcnow().date()
    current_year = today.year
    async with httpx.AsyncClient() as client:
        url = f"{HOLIDAY_API_URL}/{current_year}/{country_code.upper()}"
        resp = await client.get(url)

        if resp.status_code == 204:
            raise HTTPException(status_code=404, detail=f"No holiday data for {country_code.upper()}")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Error fetching holidays")

        holidays = resp.json()

    long_weekends = find_long_weekends(holidays, current_year)

    future = [w for w in long_weekends if parser.parse(w["start_date"]).date() >= today]

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
                url = f"{HOLIDAY_API_URL}/{datetime.utcnow().year}/{country_code.upper()}"
                resp = await client.get(url)

                if resp.status_code == 204:
                    context["error"] = f"No holiday data for '{country_code.upper()}'"
                    return templates.TemplateResponse("index.html", context)
                if resp.status_code != 200:
                    context["error"] = f"Error fetching holidays (status {resp.status_code})"
                    return templates.TemplateResponse("index.html", context)

                holidays = resp.json()

            long_weekends = find_long_weekends(holidays, datetime.utcnow().year)

            if action == "all":
                if long_weekends:
                    context["long_weekends"] = long_weekends
                else:
                    context["message"] = "No long weekends found."
            elif action == "next":
                today = datetime.utcnow().date()
                future = [w for w in long_weekends if parser.parse(w["start_date"]).date() >= today]
                if future:
                    next_one = sorted(future, key=lambda x: x["start_date"])[0]
                    context["long_weekends"] = [next_one]
                else:
                    context["message"] = "No upcoming long weekends."
        except Exception as e:
            context["error"] = f"Unexpected error: {e}"

    return templates.TemplateResponse("index.html", context)

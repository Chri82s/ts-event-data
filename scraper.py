import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# Publieke REST API zoekroute van TicketSwap
SEARCH_API_URL = "https://api.ticketswap.com/search/events"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://www.ticketswap.nl",
    "Referer": "https://www.ticketswap.nl/"
}

# Zoektermen om een actueel aanbod van evenementen op te halen
SEARCH_QUERIES = ["festival", "amsterdam", "rotterdam", "utrecht", "eindhoven", "dance"]

def fetch_ticketswap_events():
    today_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    events = []

    print("Feesten ophalen via TicketSwap Search Service...")

    for query in SEARCH_QUERIES:
        params = urllib.parse.urlencode({"q": query})
        full_url = f"{SEARCH_API_URL}?{params}"

        try:
            req = urllib.request.Request(full_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as response:
                print(f"Zoekterm '{query}' - HTTP Status Code: {response.status}")
                
                if response.status == 200:
                    raw_data = response.read().decode('utf-8')
                    data = json.loads(raw_data)
                    
                    # De API geeft een lijst of dict met 'events' of 'results' terug
                    results = data if isinstance(data, list) else data.get("events", data.get("results", []))

                    for item in results:
                        event_id = item.get("id")
                        title = item.get("title") or item.get("name")
                        slug = item.get("slug") or ""
                        
                        location = item.get("location") or {}
                        venue = location.get("name", "Onbekende locatie") if isinstance(location, dict) else "Onbekende locatie"
                        city = "Nederland"
                        if isinstance(location, dict) and "city" in location:
                            city_data = location.get("city")
                            if isinstance(city_data, dict):
                                city = city_data.get("name", "Nederland")

                        start_date = item.get("startDate") or item.get("start_date") or today_date
                        event_url = f"https://www.ticketswap.nl/event/{slug}/{event_id}" if slug else f"https://www.ticketswap.nl/event/{event_id}"

                        if title and event_id:
                            events.append({
                                "id": str(event_id),
                                "title": title,
                                "url": event_url,
                                "start_date": start_date,
                                "venue": venue,
                                "city": city
                            })

        except Exception as e:
            print(f"Fout bij opvragen van zoekterm '{query}': {e}")

    # Ontdubbelen op event ID
    unique_events = list({ev['id']: ev for ev in events}.values())
    unique_events.sort(key=lambda x: x.get('start_date') or '')

    print(f"\n--- Totaal unieke feesten verwerkt: {len(unique_events)} ---")

    os.makedirs("data", exist_ok=True)
    output_path = "data/events.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": today_date,
            "total": len(unique_events),
            "events": unique_events
        }, f, ensure_ascii=False, indent=2)

    print(f"Data succesvol opgeslagen in {output_path}")

if __name__ == "__main__":
    fetch_ticketswap_events()

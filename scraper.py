import json
import os
import re
import urllib.request
from datetime import datetime, timezone

TARGET_URL = "https://www.ticketswap.com/event-tickets"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7"
}

def fetch_ticketswap_events():
    today_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    events = []

    print(f"Ophalen van TicketSwap-pagina: {TARGET_URL}...")

    try:
        req = urllib.request.Request(TARGET_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as response:
            html_content = response.read().decode('utf-8')
            print(f"HTTP Status Code: {response.status}")

            # Extract JSON-LD blokken via Regex
            json_ld_matches = re.findall(
                r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', 
                html_content, 
                re.DOTALL
            )

            for match in json_ld_matches:
                try:
                    data = json.loads(match.strip())
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if isinstance(item, dict) and item.get("@type") in ["Event", "MusicEvent", "Festival"]:
                            event_url = item.get("url", TARGET_URL)
                            event_id = event_url.rstrip("/").split("/")[-1]
                            
                            location = item.get("location") or {}
                            venue = location.get("name", "Onbekend") if isinstance(location, dict) else "Onbekend"
                            city = "Nederland"
                            if isinstance(location, dict) and isinstance(location.get("address"), dict):
                                city = location.get("address").get("addressLocality", "Nederland")

                            events.append({
                                "id": event_id,
                                "title": item.get("name"),
                                "url": event_url,
                                "start_date": item.get("startDate", ""),
                                "venue": venue,
                                "city": city
                            })
                except json.JSONDecodeError:
                    continue

            # Fallback: extract event links rechtstreeks uit de HTML
            if not events:
                event_links = re.findall(r'href=["\'](/event/[^"\'\?]+)["\']', html_content)
                for link in set(event_links):
                    parts = link.rstrip("/").split("/")
                    if len(parts) >= 3:
                        title_slug = parts[-2].replace("-", " ").title()
                        event_id = parts[-1]
                        events.append({
                            "id": event_id,
                            "title": title_slug,
                            "url": f"https://www.ticketswap.com{link}",
                            "start_date": today_date,
                            "venue": "TicketSwap Event",
                            "city": "Nederland"
                        })

    except Exception as e:
        print(f"Fout tijdens het scrapen: {e}")

    # Ontdubbelen op ID
    unique_events = list({ev['id']: ev for ev in events if ev.get('id')}.values())
    unique_events.sort(key=lambda x: x.get('title') or '')

    print(f"\n--- Totaal unieke feesten gevonden: {len(unique_events)} ---")

    os.makedirs("data", exist_ok=True)
    output_path = "data/events.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": today_date,
            "total": len(unique_events),
            "events": unique_events
        }, f, ensure_ascii=False, indent=2)

    print(f"Data opgeslagen in {output_path}")

if __name__ == "__main__":
    fetch_ticketswap_events()

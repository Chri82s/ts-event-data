import json
import os
import re
import requests
from bs4 import BeautifulSoup
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

    print(f"Ophalen via TicketSwap HTML Webpage: {TARGET_URL}...")

    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=20)
        print(f"HTTP Status Code: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # 1. Probeer JSON-LD gestructureerde data op te halen
            json_ld_scripts = soup.find_all("script", {"type": "application/ld+json"})
            for script in json_ld_scripts:
                if script.string:
                    try:
                        data = json.loads(script.string)
                        items = data if isinstance(data, list) else [data]
                        for item in items:
                            if item.get("@type") in ["Event", "MusicEvent", "Festival"]:
                                events.append({
                                    "id": item.get("url", "").split("/")[-1] or item.get("name"),
                                    "title": item.get("name"),
                                    "url": item.get("url", TARGET_URL),
                                    "start_date": item.get("startDate", ""),
                                    "venue": item.get("location", {}).get("name", "Onbekend") if isinstance(item.get("location"), dict) else "Onbekend",
                                    "city": item.get("location", {}).get("address", {}).get("addressLocality", "Nederland") if isinstance(item.get("location"), dict) else "Nederland"
                                })
                    except json.JSONDecodeError:
                        continue

            # 2. Fallback: vind event links direct in de HTML structure
            if not events:
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"]
                    if "/event/" in href:
                        title = a_tag.get_text(strip=True)
                        if title and len(title) > 2:
                            full_url = href if href.startswith("http") else f"https://www.ticketswap.com{href}"
                            events.append({
                                "id": href.rstrip("/").split("/")[-1],
                                "title": title,
                                "url": full_url,
                                "start_date": today_date,
                                "venue": "TicketSwap Event",
                                "city": "Nederland"
                            })

        else:
            print(f"Fout bij ophalen pagina. Status: {response.status_code}")

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

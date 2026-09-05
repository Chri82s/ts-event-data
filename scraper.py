import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

SITEMAP_URL = "https://www.ticketswap.nl/sitemap-events.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def fetch_ticketswap_events():
    today_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    events = []

    print(f"Sitemap ophalen van TicketSwap: {SITEMAP_URL}...")

    try:
        req = urllib.request.Request(SITEMAP_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"HTTP Status Code: {response.status}")

            if response.status == 200:
                xml_data = response.read()
                root = ET.fromstring(xml_data)

                # Sitemap namespace afhandelen
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

                for url_element in root.findall('ns:url', namespace):
                    loc = url_element.find('ns:loc', namespace)
                    if loc is not None and loc.text:
                        full_url = loc.text
                        
                        # Filter op event URLs
                        if "/event/" in full_url:
                            parts = full_url.rstrip("/").split("/")
                            if len(parts) >= 2:
                                event_id = parts[-1]
                                raw_slug = parts[-2] if len(parts) >= 3 else "event"
                                
                                # Titel netjes formatteren vanuit de url slug
                                title = raw_slug.replace("-", " ").title()

                                events.append({
                                    "id": str(event_id),
                                    "title": title,
                                    "url": full_url,
                                    "start_date": today_date,
                                    "venue": "TicketSwap Event",
                                    "city": "Nederland"
                                })

            else:
                print(f"Fout bij ophalen sitemap. Status: {response.status}")

    except Exception as e:
        print(f"Fout bij verwerken sitemap: {e}")

    # Ontdubbelen op ID en beperken tot de eerste 100 actuele feesten
    unique_events = list({ev['id']: ev for ev in events}.values())[:100]
    unique_events.sort(key=lambda x: x.get('title') or '')

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

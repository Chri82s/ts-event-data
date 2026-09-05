import json
import os
import requests
from datetime import datetime, timezone

TICKETSWAP_GRAPHQL_URL = "https://api.ticketswap.com/graphql"

# Mimic browser headers voor TicketSwap
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Origin": "https://www.ticketswap.com",
    "Referer": "https://www.ticketswap.com/event-tickets",
    "x-client-type": "WEB",
    "x-client-version": "1.0.0"
}

# De actuele GraphQL query die de event-tickets pagina gebruikt
QUERY = """
query GetEventTicketsPage($first: Int, $after: String) {
  popularEvents(first: $first, after: $after) {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        id
        title
        slug
        startDate
        endDate
        location {
          id
          name
          city {
            id
            name
            country {
              id
              name
            }
          }
        }
      }
    }
  }
}
"""

def fetch_ticketswap_events():
    today_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    events = []

    print("Feesten ophalen van TicketSwap...")

    payload = {
        "operationName": "GetEventTicketsPage",
        "variables": {
            "first": 50
        },
        "query": QUERY
    }

    try:
        response = requests.post(TICKETSWAP_GRAPHQL_URL, json=payload, headers=HEADERS, timeout=20)
        print(f"HTTP Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                print(f"GraphQL Foutmeldingen: {data['errors']}")

            edges = data.get("data", {}).get("popularEvents", {}).get("edges", [])
            print(f"Aantal evenementen ontvangen via API: {len(edges)}")

            for edge in edges:
                node = edge.get("node", {})
                if not node:
                    continue

                event_id = node.get("id")
                title = node.get("title")
                slug = node.get("slug")
                start_date = node.get("startDate")
                
                location_info = node.get("location") or {}
                venue = location_info.get("name", "Onbekende locatie")
                city = location_info.get("city", {}).get("name", "Nederland")

                full_url = f"https://www.ticketswap.com/event/{slug}/{event_id}" if slug else f"https://www.ticketswap.com/event/{event_id}"

                events.append({
                    "id": str(event_id),
                    "title": title,
                    "url": full_url,
                    "start_date": start_date,
                    "venue": venue,
                    "city": city
                })

        else:
            print(f"Fout bij opvragen data: {response.status_code} - {response.text[:200]}")

    except Exception as e:
        print(f"Fout tijdens het scrapen van TicketSwap: {e}")

    # Ontdubbelen op ID en sorteren op datum
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

import json
import os
import requests
from datetime import datetime, timezone

TICKETSWAP_GRAPHQL_URL = "https://api.ticketswap.com/graphql"

HEADERS = {
    "User-Agent": "TicketSwap/7.41.0 (Android; NL)",
    "Content-Type": "application/json",
    "Accept-Language": "nl-NL"
}

QUERY = """
query GetPopularEvents($query: String!) {
  search(query: $query, type: EVENTS, first: 50) {
    events {
      edges {
        node {
          id
          title
          slug
          startDate
          endDate
          location {
            name
            city {
              name
              country {
                name
              }
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
    search_terms = ["Amsterdam", "Rotterdam", "Utrecht", "Festival", "Party"]

    print("Evenementen ophalen via TicketSwap GraphQL API...")

    for term in search_terms:
        payload = {
            "query": QUERY,
            "variables": {"query": term}
        }

        try:
            response = requests.post(TICKETSWAP_GRAPHQL_URL, json=payload, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                data = response.json()
                edges = data.get("data", {}).get("search", {}).get("events", {}).get("edges", [])

                for edge in edges:
                    node = edge.get("node", {})
                    if not node:
                        continue

                    title = node.get("title")
                    slug = node.get("slug")
                    start_date = node.get("startDate")
                    location_info = node.get("location") or {}
                    venue = location_info.get("name", "Onbekende locatie")
                    city = location_info.get("city", {}).get("name", "Nederland")

                    full_url = f"https://www.ticketswap.nl/event/{slug}/{node.get('id')}"

                    events.append({
                        "id": node.get("id"),
                        "title": title,
                        "url": full_url,
                        "start_date": start_date,
                        "venue": venue,
                        "city": city
                    })
        except Exception as e:
            print(f"Fout bij zoekterm '{term}': {e}")

    unique_events = list({ev['id']: ev for ev in events}.values())
    
    # Sorteer op datum
    unique_events.sort(key=lambda x: x.get('start_date') or '')

    print(f"Totaal aantal unieke feesten gevonden: {len(unique_events)}")

    os.makedirs("data", exist_ok=True)
    
    # Exporteer als vaste events.json voor het front-end
    with open("data/events.json", "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": today_date,
            "total": len(unique_events),
            "events": unique_events
        }, f, ensure_ascii=False, indent=2)

    print("Data succesvol opgeslagen in data/events.json")

if __name__ == "__main__":
    fetch_ticketswap_events()

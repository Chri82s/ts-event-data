# TicketSwap Events Navigator 🎟️

Een geautomatiseerde scraper en dashboard om actuele feesten, festivals en evenementen in Nederland op te halen via de TicketSwap GraphQL API en te tonen op een overzichtelijke webpagina.

## 🚀 Features

- **Automatische Scraper:** Draait dagelijks via GitHub Actions.
- **Geen IP-blocks:** Maakt rechtstreeks gebruik van de mobiele GraphQL API van TicketSwap.
- **Live Dashboard:** Responsive front-end met zoekbalk en filters (gehost via GitHub Pages).

## 🛠️ Projectstructuur

```text
├── .github/
│   └── workflows/
│       └── daily_scrape.yml   # GitHub Actions workflow (dagelijkse run)
├── data/
│   └── events.json            # Gegenereerde data door de scraper
├── index.html                 # Front-end dashboard
├── scraper.py                 # Python script voor het scrapen van de API
└── README.md                  # Projectdocumentatie

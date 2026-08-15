import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from google import genai

# RSS-Feeds, die du abrufen möchtest
FEEDS = {
    "Tagesschau": "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml"
}

# Initialisiert den Gemini-Client automatisch mit GEMINI_API_KEY aus den Umgebungsvariablen
client = genai.Client()

def fetch_rss(url):
    """Holt die neusten 3 Artikel aus einem RSS-Feed."""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    xml_data = urllib.request.urlopen(req).read()
    root = ET.fromstring(xml_data)
    
    items = []
    for item in root.findall('.//item')[:3]:
        title = item.find('title').text if item.find('title') is not None else ""
        link = item.find('link').text if item.find('link') is not None else ""
        description = item.find('description').text if item.find('description') is not None else ""
        items.append({"title": title, "link": link, "description": description})
    return items

def summarize_with_gemini(title, content):
    """Nutzt das offizielle Gemini SDK zur Zusammenfassung."""
    prompt = (
        f"Fasse folgenden Artikel in 2 prägnanten Bullet Points auf Deutsch zusammen. "
        f"Antworte nur mit den Stichpunkten:\nTitel: {title}\nInhalt: {content}"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Fehler bei Gemini API: {e}")
        return f"Zusammenfassung derzeit nicht verfügbar. Fehler: {e}"

def main():
    all_news = []
    
    for source, url in FEEDS.items():
        print(f"Hole Nachrichten von {source}...")
        articles = fetch_rss(url)
        for article in articles:
            print(f"Fasse zusammen: {article['title']}")
            summary = summarize_with_gemini(article['title'], article['description'])
            all_news.append({
                "source": source,
                "title": article['title'],
                "link": article['link'],
                "summary": summary
            })

    # Speichert das Ergebnis als news.json für das Frontend
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print("news.json wurde erfolgreich erstellt!")

if __name__ == "__main__":
    main()

import os
import json
import urllib.request
import xml.etree.ElementTree as ET

# RSS-Feeds, die du abrufen möchtest
FEEDS = {
    "Tagesschau": "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml"
}

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def fetch_rss(url):
    """Holt die neusten 3 Artikel aus einem RSS-Feed."""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    xml_data = urllib.request.urlopen(req).read()
    root = ET.fromstring(xml_data)
    
    items = []
    # RSS-Standard durchsuchen
    for item in root.findall('.//item')[:3]:
        title = item.find('title').text if item.find('title') is not None else ""
        link = item.find('link').text if item.find('link') is not None else ""
        description = item.find('description').text if item.find('description') is not None else ""
        items.append({"title": title, "link": link, "description": description})
    return items

def summarize_with_gemini(title, content):
    """Ruft die Gemini API auf, um eine Zusammenfassung zu generieren."""
    if not GEMINI_API_KEY:
        return "Kein API-Key vorhanden."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"Fasse folgenden Artikel in 2 prägnanten Bullet Points auf Deutsch zusammen. Antworte nur mit den Stichpunkten:\nTitel: {title}\nInhalt: {content}"
    
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=payload,
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Fehler bei Gemini API: {e}")
        return "Zusammenfassung derzeit nicht verfügbar."

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

    # Speichere die Ergebnisse als news.json
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print("news.json wurde erfolgreich erstellt!")

if __name__ == "__main__":
    main()

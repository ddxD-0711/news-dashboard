def summarize_with_gemini(title, content):
    if not GEMINI_API_KEY:
        return "Fehler: GEMINI_API_KEY wurde nicht gefunden."

    # Aktualisierter v1beta Endpunkt für gemini-1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"Fasse folgenden Artikel in 2 prägnanten Bullet Points auf Deutsch zusammen. Antworte nur mit den Stichpunkten:\nTitel: {title}\nInhalt: {content}"
    
    payload = json.dumps({
        "contents": [{
            "parts": [{"text": prompt}]
        }]
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
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Fehler {e.code}: {error_body}")
        # Falls gemini-1.5-flash nicht gefunden wird, versuche den Fallback auf gemini-pro
        if e.code == 404:
            return try_fallback_model(title, content)
        return f"API-Fehler ({e.code})"
    except Exception as e:
        print(f"Fehler: {e}")
        return f"Fehler bei Anfrage: {e}"

def try_fallback_model(title, content):
    """Fallback-Funktion auf gemini-pro, falls flash in der Region/Key-Kombination 404 wirft."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Fasse folgenden Artikel in 2 prägnanten Bullet Points auf Deutsch zusammen. Antworte nur mit den Stichpunkten:\nTitel: {title}\nInhalt: {content}"
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Fallback-Fehler: {e}")
        return "Zusammenfassung nicht verfügbar."

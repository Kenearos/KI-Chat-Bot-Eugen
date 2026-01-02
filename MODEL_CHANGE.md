# Perplexity Modell ändern

Du kannst das Perplexity-Modell jederzeit ändern, ohne den Bot neu zu konfigurieren.

## Methode 1: .env Datei bearbeiten

1. Öffne die `.env` Datei in einem Texteditor
2. Finde die Zeile `PERPLEXITY_MODEL=...`
3. Ändere den Wert zu einem der verfügbaren Modelle:
   ```
   PERPLEXITY_MODEL=sonar-pro
   ```
4. Speichern und Bot neu starten

## Methode 2: Setup Wizard neu ausführen

1. Lösche die `.env` Datei
2. Starte den Bot: `python chatbot.py`
3. Der Setup Wizard startet automatisch
4. Wähle dein gewünschtes Modell aus der Dropdown-Liste

## Verfügbare Modelle

### Empfohlen für Chat Bots:

**sonar-pro** (Standard)
- Beste Qualität und Reasoning
- Ideal für Chat-Interaktionen
- Gutes Preis-Leistungs-Verhältnis

### Alternative Modelle:

**sonar**
- Schneller, günstiger
- Für einfache Anfragen
- Weniger komplex

**sonar-reasoning**
- Erweitertes Reasoning
- Für komplexe Probleme
- Langsamer, aber durchdachter

**llama-3.1-sonar-small-128k-online**
- Kleinster, schnellster Llama
- 128k Kontext
- Beste für schnelle, einfache Antworten

**llama-3.1-sonar-large-128k-online**
- Größeres Llama-Modell
- Bessere Qualität als small
- Guter Kompromiss

**llama-3.1-sonar-huge-128k-online**
- Größtes Llama-Modell
- Beste Qualität, aber langsamer
- Höhere Kosten

## Beispiel .env Datei

```env
TWITCH_OAUTH_TOKEN=oauth:xxxxx
TWITCH_BOT_NICKNAME=Eugen
TWITCH_CHANNEL=#channel_name
PERPLEXITY_API_KEY=pplx-xxxxx
PERPLEXITY_MODEL=sonar-pro
MAX_TOKENS=450
DEBUG_MODE=true
```

## Tipp

Wenn du verschiedene Modelle testen möchtest, erstelle eine Backup-Kopie deiner `.env` Datei vor dem Ändern.

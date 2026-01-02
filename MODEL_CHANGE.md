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

## Verfügbare Modelle (Perplexity API 2026)

### Empfohlen für Chat Bots:

**sonar-pro** (Standard) ⭐
- Tieferes Inhaltsverständnis
- 2x mehr Suchergebnisse als sonar
- Verbesserte Suchgenauigkeit
- Ideal für komplexe, mehrstufige Anfragen
- Basiert auf Llama 3.3 70B
- **Beste Wahl für Twitch Chat Bots!**

### Alternative Modelle:

**sonar**
- Leichtgewichtig und schnell
- Niedrigere Kosten
- Einfache Frage-Antwort-Features
- Gut für geschwindigkeitsoptimierte Anwendungen
- Basiert auf Llama 3.3 70B

**sonar-reasoning**
- Echtzeit-Reasoning mit Suche
- Zeigt Denkprozess
- Gut für Problemlösung
- Moderate Geschwindigkeit

**sonar-reasoning-pro**
- Powered by DeepSeek-R1
- Erweiterte Reasoning-Fähigkeiten
- Sichtbarer Reasoning-Content via API
- Beste für komplexe logische Aufgaben
- Höhere Kosten

**sonar-deep-research**
- Lange, ausführliche Research-Reports
- Quellenreiche Ausgabe
- Beste für detaillierte Analysen
- Langsamer, umfassende Antworten

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

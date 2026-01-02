# LICENSE - Eugen Twitch Bot

## Empfohlene Lizenz: MIT License

Für ein öffentliches Gaming & 3D-Druck Twitch-Bot-Projekt empfehlen wir die **MIT License**.

### Warum MIT?

| Aspekt | MIT | GPL | Apache 2.0 |
|--------|-----|-----|-----------|
| **Einfachheit** | ✅ Sehr kurz & verständlich | ⚠️ Komplex | ⚠️ 200+ Zeilen |
| **Commercial Use** | ✅ Erlaubt | ✅ Erlaubt | ✅ Erlaubt |
| **Modifikation** | ✅ Erlaubt | ✅ Erlaubt | ✅ Erlaubt |
| **Private Use** | ✅ Erlaubt | ✅ Erlaubt | ✅ Erlaubt |
| **Distribution** | ✅ Erlaubt | ⚠️ Nur unter GPL | ✅ Erlaubt |
| **Copyleft** | ❌ Nein | ✅ Ja (striktes Copyleft) | ❌ Nein (file-level) |
| **Patent Protection** | ❌ Nein | ❌ Nein | ✅ Ja |
| **Liability Disclaimer** | ✅ Ja | ✅ Ja | ✅ Ja |

---

## MIT License (Volltext)

Erstelle eine Datei `LICENSE` im Root-Verzeichnis mit folgendem Inhalt:

```
MIT License

Copyright (c) 2026 Eugen Twitch Bot Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Was die MIT License bedeutet

### ✅ Erlaubt

- **Commercial Use**: Jemand kann den Bot für Profit verwenden
- **Modification**: Code kann verändert werden
- **Distribution**: Code kann weitergegeben werden
- **Private Use**: Privat nutzen ohne Einschränkung
- **Sublicense**: Unter einer anderen Lizenz weitergeben (mit Bedingungen)

### ❌ Nicht erlaubt

- **Liability**: Deine Haftung ist ausgeschlossen
- **Warranty**: Keine Garantie für Funktionalität

### ⚠️ Bedingungen

- **Lizenz & Copyright Notice** muss mitgegeben werden
- **Disclaimer** muss in allen Kopien stehen

---

## Lizenz in GitHub aktivieren

### Option 1: GitHub Web-UI (Einfachste Methode)

1. Gehe zu deinem GitHub Repo
2. **Settings** → **License**
3. Wähle **MIT License** aus Dropdown
4. GitHub erstellt automatisch die `LICENSE` Datei
5. Commit & Push

### Option 2: Lokal hinzufügen

```powershell
# LICENSE Datei erstellen (siehe oben)
# Dann committen:
git add LICENSE
git commit -m "Add MIT License"
git push
```

---

## README Badge hinzufügen

In deiner `README.md` oben hinzufügen:

```markdown
# Eugen Twitch Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Intelligenter Gaming & 3D-Druck Twitch-Chat-Agent mit Perplexity AI Integration.
```

Ergebnis: Goldener Badge mit "License: MIT" 🏆

---

## Lizenz-Vergleich für andere Use-Cases

### GPL 3.0 (Für Open Source Puristen)

```
Nutzbar, wenn:
- Du willst dass Derivate auch Open Source bleiben (Copyleft)
- Dein Projekt bereits GPL ist
- Community über Commercial Use nicht hinwegkommt

Nicht, wenn:
- Kommerzielle Nutzung problemlos sein soll
- Du simplify willst
```

### Apache 2.0 (Für Enterprise)

```
Nutzbar, wenn:
- Patent-Schutz wichtig ist
- Enterprise-Unternehmen nutzen sollen
- Längere, formale Lizenz okay ist

Nicht, wenn:
- Du es einfach hast
- Kleine Open-Source-Projekte
```

---

## Setup Checkliste

- [ ] `LICENSE` Datei erstellen (MIT Text oben kopieren)
- [ ] In `README.md` Badge hinzufügen
- [ ] In `.gitignore` nichts Wichtiges ignorieren
- [ ] `.env.example` committen (keine echten Keys!)
- [ ] GitHub Repo Settings → License → MIT
- [ ] First commit mit License-Info

---

## Dateistruktur nach Lizenz-Setup

```
eugen/
├── LICENSE              ← MIT Text
├── README.md            ← Mit Badge
├── .env.example         ← Template ohne Keys
├── .gitignore
├── requirements.txt
├── chatbot.py
├── config.py
├── gui.py
├── ai_provider.py
├── memory.py
└── data/
    └── conversations/
```

---

## Copyright-Zeile anpassen

Je nachdem wer dein "Owner" ist:

**Dein Name:**
```
Copyright (c) 2026 Dein Name
```

**Team/Org:**
```
Copyright (c) 2026 Eugen Bot Team
```

**Community:**
```
Copyright (c) 2026 Eugen Twitch Bot Contributors
```

---

## Legal Quick Reference

| Question | MIT Answer |
|----------|------------|
| Darf ich das kommerziell nutzen? | ✅ Ja |
| Muss ich den Code offen halten? | ❌ Nein |
| Muss ich Original nennen? | ✅ Ja |
| Kann ich Änderungen machen? | ✅ Ja, ohne mir zu sagen |
| Haftung? | ❌ Nein (Disclaimer) |

---

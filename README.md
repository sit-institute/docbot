# DocBot - Agenten-Basiertes Forschungsprojekt-Management

DocBot ist ein VS Code MCP-basiertes System zur Verwaltung und Verarbeitung von Forschungsprojekt-Dokumenten für Principal Investigators. Das System nutzt Claude's Agenten-Architektur mit Skills, um aus heterogenen Projektdokumenten Informationen zu extrahieren, Projekte zu verstehen und neue Dokumente wie Berichte zu erstellen.

## 🎯 Hauptfunktionen

- **Projekt-Indexierung**: Automatisches Scannen und Indexieren von Forschungsprojekten
- **Metadaten-Extraktion**: Intelligente Extraktion von Projektinformationen aus Dokumenten
- **Semantische Suche**: Local RAG für schnelle Dokumentensuche ohne Cloud
- **Portfolio-Übersichten**: Automatische Generierung von Projekt-Übersichten
- **Dokument-Generierung**: Erstellung von Berichten und Zusammenfassungen

## 🚀 Quick Start

### VS Code Copilot

Der **Project Visitor Agent** ist installiert und wird automatisch von VS Code erkannt.

1. Öffne VS Code in diesem Repository
2. Öffne Copilot Chat (Cmd/Ctrl + Shift + I)
3. Wähle `@project-visitor` aus der Agents-Dropdown-Liste

### Erstes Projekt indexieren

```
@project-visitor Indexiere Projekt ki-gesundheit-2024
```

## 📁 Repository-Struktur

```
docbot/
├── .github/
│   ├── agents/                        # Custom VS Code Copilot Agents
│   │   └── project-visitor.agent.md  # Project Visitor Agent
│   └── skills/                        # Agent Skills
│       ├── local-rag-pipeline/        # Local RAG Pipeline (siehe SKILL.md)
│       └── project-visitor/           # Project Visitor Skills
│
├── projects/                          # Projekt-Index-Dateien
│   └── [projekt-id].md               # Ein Projekt-Index
│
├── documents/                         # Lokale Dokumente (BASE_DIR für Local RAG)
│   └── [projekt-id]/                 # Dokumente eines Projekts
│       ├── antrag/                   # Antragsunterlagen
│       ├── berichte/                 # Projektberichte
│       ├── publikationen/            # Papers
│       ├── meetings/                 # Meeting-Notizen
│       ├── deliverables/             # Projektergebnisse
│       ├── correspondence/           # E-Mail-Anhänge
│       └── data/                     # CSV, Rohdaten
│
├── templates/                         # Vorlagen
│   └── projekt-index-template.md     # Projekt-Index Template
│
├── reports/                           # Generierte Berichte
│   └── portfolio-overview.md         # Portfolio-Übersicht
│
├── knowledge/                         # Wissensdatenbank
│   ├── glossar.md
│   ├── partner.md
│   └── foerderer.md
│
└── AGENTS.md                         # Vollständige Dokumentation
```

## 🤖 Verfügbare Agents

### Project Visitor Agent

**Aufgabe**: Projekte durchsuchen, indexieren und Portfolio-Übersichten erstellen

**Verwendung**:
```
@project-visitor Indexiere Projekt [projekt-id]
@project-visitor Erstelle Portfolio-Übersicht
@project-visitor Extrahiere Metadaten aus documents/[projekt-id]/
```

**Features**:
- ✅ Automatische Dokument-Ingestion in Local RAG
- ✅ Intelligente Metadaten-Extraktion
- ✅ Projekt-Index-Erstellung
- ✅ Portfolio-Übersichten
- ✅ Fehlerbehandlung und Reporting

**Handoffs**:
- → Summarizer: Zusammenfassungen erstellen
- → Reporter: Statusberichte generieren

### Weitere Agents (in Planung)

- **Summarizer Agent**: Zusammenfassungen und Executive Summaries
- **Reporter Agent**: Statusberichte und Zwischenberichte
- **Similarity Agent**: Projekt-Ähnlichkeiten und Synergien
- **Generator Agent**: Neue Dokumente (Anträge, Protokolle)
- **Analyzer Agent**: Budget-Analysen, Risiken, Timelines

## 📖 Dokumentation

### Für Nutzer
- **AGENTS.md**: Vollständige Projekt-Dokumentation
- **.github/skills/local-rag-pipeline/SKILL.md**: Local RAG Pipeline Anleitung

### Für Agent-Entwicklung
- **.github/skills/project-visitor/SKILL.md**: Workflow und Best Practices
- **references/projekt-index-format.md**: Projekt-Index Format

## 🔧 Workflows

### Neues Projekt anlegen

1. Erstelle Ordner `documents/[projekt-id]/`
2. Lege Dokumente in Unterordner ab (antrag/, berichte/, etc.)
3. Nutze Project Visitor Agent:
   ```
   @project-visitor Indexiere Projekt [projekt-id]
   ```
4. Prüfe generierte Datei `projects/[projekt-id].md`

### Portfolio-Analyse erstellen

```
@project-visitor Erstelle Portfolio-Übersicht
```

Der Agent:
- Liest alle Projekt-Index-Dateien in `projects/`
- Erstellt Tabelle mit allen Projekten
- Berechnet Statistiken (Budget, Status, etc.)
- Identifiziert fehlende Informationen

### Dokument durchsuchen

```
@project-visitor Finde alle Informationen über Budget in Projekt ki-2024
```

Der Agent nutzt Local RAG für semantische Suche in allen ingestierten Dokumenten.

## 🤝 Contributing

Neue Agents oder Skills erstellen:

1. **Neuer Agent**: Erstelle `.github/agents/[name].agent.md`
2. **Neuer Skill**: Erstelle `.github/skills/[name]/SKILL.md`
3. Siehe `.github/README.md` für Details

## 📝 Benennungskonventionen

### Projekt-IDs
- Kleinbuchstaben, Bindestriche
- Format: `[akronym]-[jahr]`
- Beispiel: `ki-gesundheit-2024`

### Dateinamen
- Kleinbuchstaben, Bindestriche
- Datum in ISO: `YYYY-MM-DD`
- Beispiel: `2024-01-15-kickoff-meeting.md`

### Dokument-Referenzen
- Lokale Dokumente: Relative Pfade `../documents/...` + `(lokal)`
- Externe Dokumente: Volle URL + Plattform `(Confluence)`

## 🔒 Datenschutz

- ✅ **Lokal**: Alle Dokumente bleiben auf deinem Rechner
- ✅ **Offline**: Nach Modell-Download keine Internet-Verbindung nötig
- ✅ **Privat**: Keine Daten werden an externe APIs gesendet

## 📚 Weitere Ressourcen

- [VS Code Custom Agents Dokumentation](https://code.visualstudio.com/docs/copilot/customization/custom-agents)

## 📄 Lizenz

[Füge Lizenz hinzu]

## 👥 Autoren

SIT Institute - Software Innovation & Technology

---

**Tipp**: Starte mit `@project-visitor` in VS Code Copilot Chat für interaktive Hilfe!

# DocBot - Agenten-Basiertes Forschungsprojekt-Management

## Projekt-Übersicht

DocBot ist ein VS Code MCP-basiertes System zur Verwaltung und Verarbeitung von Forschungsprojekt-Dokumenten für Principal Investigators. Das System nutzt Claude's Agenten-Architektur mit Skills, um aus heterogenen Projektdokumenten Informationen zu extrahieren, Projekte zu verstehen und neue Dokumente wie Berichte zu erstellen.

## Zweck und Anwendungsfall

**Zielnutzer**: Principal Investigator, der mehrere Forschungsprojekte koordiniert

**Hauptaufgaben**:
- Projektdokumente verstehen und durchsuchen
- Informationen aus verschiedenen Dokumenttypen extrahieren
- Ähnlichkeiten zwischen Projekten identifizieren
- Statusberichte und Zusammenfassungen erstellen
- Neue Projektdokumente generieren (Anträge, Reports, etc.)

## Kernkonzepte

### Dokumente
- Heterogene Projektdokumentation (PDF, Markdown, DOCX, HTML, TXT, Excel, PowerPoint)
- Verschiedene Dokumenttypen: Anträge, Berichte, Publikationen, Meeting-Notizen, Protokolle
- Strukturierte und unstrukturierte Inhalte
- Metadaten-basierte Organisation (Projekt, Datum, Typ, Status)

### Agenten (VS Code MCP)
- Nutzen Claude's Skill-basierte Architektur
- Jeder Agent hat spezialisierte Aufgaben
- Verwenden MCP-Tools für Dokumentenzugriff
- Arbeiten mit vorhandenen VS Code Extensions

### Skills
- Basieren auf Claude MCP Skills
- Modulare, wiederverwendbare Funktionen
- Können Scripts aufrufen (z.B. Python für spezielle Analysen)
- Kombinierbar für komplexe Workflows

## Dokumenten-Quellen

Projektdokumente können sich an verschiedenen Speicherorten befinden:

### Lokal
- Dateisystem-Ordner
- Lokale Datenbanken

### Version Control
- **GitHub**: Repositories, Issues, Pull Requests, Wikis

### Kollaborations-Plattformen
- **Confluence**: Wiki-Pages, Dokumentation, Meeting-Notizen
- **SharePoint**: Dokument-Libraries, Listen
- **Notion**: Pages, Databases
- **Google Drive**: Docs, Sheets, Slides
- **OneDrive**: Office-Dokumente

### Projektmanagement
- **Jira**: Tickets, Epics, Sprint-Dokumentation
- **Trello**: Boards, Cards

### Kommunikation
- **Slack**: Channel-Nachrichten, geteilte Dateien
- **Microsoft Teams**: Nachrichten, geteilte Dokumente
- **E-Mail**: Archivierte Korrespondenz

## Repository-Struktur

Das Repository organisiert sowohl lokale Dokumente als auch Index-Dateien mit Links zu externen Quellen:

```
docbot/
├── projects/                          # Projekt-Index-Dateien
│   ├── [projekt-id].md                # Projekt-Metadaten mit Dokumenten-Links
│   └── [weiteres-projekt].md
│
├── documents/                         # Lokale Dokumente (alle Projekte)
│   ├── [projekt-id]/                  # Dokumente eines spezifischen Projekts
│   │   ├── antrag/                    # Antragsunterlagen
│   │   │   ├── vollantrag.pdf
│   │   │   ├── budget.xlsx
│   │   │   └── anlagen/
│   │   ├── berichte/                  # Projektberichte
│   │   │   ├── zwischenbericht-2024.pdf
│   │   │   └── jahresbericht-2024.docx
│   │   ├── publikationen/             # Papers und Veröffentlichungen
│   │   │   ├── paper-2024-01.pdf
│   │   │   └── preprints/
│   │   ├── meetings/                  # Meeting-Protokolle und Notizen
│   │   │   ├── 2024-01-15-kickoff.pdf
│   │   │   └── 2024-03-20-review.md
│   │   ├── deliverables/              # Projektergebnisse
│   │   │   ├── d1-requirements.pdf
│   │   │   └── d2-prototype.zip
│   │   ├── correspondence/            # E-Mail-Anhänge, wichtige Korrespondenz
│   │   │   ├── foerderer/
│   │   │   └── partner/
│   │   └── data/                      # Datensätze, CSV, Rohdaten
│   │       ├── survey-results.csv
│   │       └── measurements/
│   │
│   └── [weiteres-projekt]/
│
├── templates/                         # Vorlagen für neue Dokumente
│   ├── projekt-index-template.md
│   ├── zwischenbericht-template.md
│   ├── jahresbericht-template.md
│   └── meeting-notiz-template.md
│
├── reports/                           # Generierte Überblicksberichte
│   ├── portfolio-overview.md
│   └── analytics/
│       └── projekt-similarities.md
│
├── knowledge/                         # Wissensdatenbank
│   ├── glossar.md
│   ├── partner.md
│   └── foerderer.md
│
├── scripts/                           # Hilfs-Scripts (optional)
│   ├── extract-budget.py
│   └── similarity-analysis.py
│
└── .mcp/                              # MCP Konfiguration
    └── config.json
```

**Wichtig**: 
- Der `documents/` Ordner ist das `BASE_DIR` für Local RAG und enthält alle lokalen Dokumente
- Dokumente die bereits in anderen Systemen (Confluence, SharePoint, GitHub, etc.) gespeichert sind, werden nur in der Projekt-Index-Datei verlinkt
- `.rag/` wird automatisch von Local RAG erstellt und sollte in `.gitignore` stehen

## Projekt-Index Format

Jedes Projekt sollte als Markdown-Datei im `projects/` Ordner indexiert werden. Die Datei enthält Metadaten und Links zu den verteilten Dokumenten:

```markdown
# [Projekt-Titel]

## Basis-Informationen
- **Projekt-ID**: [eindeutige-id]
- **Akronym**: [Kurz-Akronym]
- **Laufzeit**: YYYY-MM-DD bis YYYY-MM-DD
- **Status**: [In Vorbereitung | Laufend | Abgeschlossen | Abgebrochen]
- **Budget**: [Betrag] EUR
- **Förderer**: [Name des Förderers]
- **Förderprogramm**: [Programmname]

## Projektteam
- **PI**: [Name]
- **Co-PIs**: [Namen]
- **Mitarbeiter**: [Namen]
- **Partner**: [Organisationen]

## Inhalt
[Kurzbeschreibung des Projekts in 2-3 Sätzen]

## Ziele
1. [Hauptziel 1]
2. [Hauptziel 2]
3. [Hauptziel 3]

## Arbeitspakete
- **WP1**: [Name] - [Status]
- **WP2**: [Name] - [Status]
- **WP3**: [Name] - [Status]

## Deliverables
- **D1**: [Name] - Fällig: YYYY-MM-DD - Status: [✓/○]
- **D2**: [Name] - Fällig: YYYY-MM-DD - Status: [✓/○]

## Meilensteine
- **M1**: [Name] - Datum - Status
- **M2**: [Name] - Datum - Status

## Schlagworte
[keyword1], [keyword2], [keyword3], [themenbereich]

## Verwandte Projekte
- [projekt-id-1]: [Beziehung/Überschneidung]
- [projekt-id-2]: [Beziehung/Überschneidung]

## Dokumente
### Antrag
- [Vollantrag PDF](../documents/ki-2024/antrag/vollantrag.pdf) (lokal)
- [Budget Excel](../documents/ki-2024/antrag/budget.xlsx) (lokal)
- [Projektbeschreibung](https://gitlab.example.com/ki-projekt/wiki/beschreibung) (GitLab)

### Berichte
- [Zwischenbericht 2024](https://confluence.example.com/projects/KI-2024/zwischenbericht) (Confluence)
- [Meeting-Notizen](https://notion.so/ki-projekt/meetings) (Notion)
- [Jahresbericht 2024](../documents/ki-2024/berichte/jahresbericht-2024.pdf) (lokal)

### Daten & Analysen
- [Survey Results CSV](../documents/ki-2024/data/survey-results.csv) (lokal)
- [Measurement Data](../documents/ki-2024/data/measurements/) (lokal)

### Kommunikation
- [Slack Channel](https://example.slack.com/archives/C123456) (Slack)
- [Jira Board](https://jira.example.com/projects/KI2024) (Jira)
- [E-Mail Korrespondenz](../documents/ki-2024/correspondence/foerderer/) (lokal)

## Wichtige Links
- Projektwebsite: [URL]
- Repository: [URL]
- Förderer-Portal: [URL]
```

## Agent-Typen und Aufgaben

### 1. Project Visitor Agent
**Aufgabe**: Projekte durchsuchen und indexieren
- Liest alle Dokumente eines Projekts
- Extrahiert Metadaten
- Aktualisiert Portfolio-Übersicht
- Identifiziert fehlende Informationen

### 2. Summarizer Agent
**Aufgabe**: Zusammenfassungen erstellen
- Erstellt Projekt-Summaries
- Fasst lange Dokumente zusammen
- Generiert Executive Summaries für Berichte
- Extrahiert Key Points aus Meetings

### 3. Reporter Agent
**Aufgabe**: Berichte generieren
- Erstellt Statusberichte aus Templates
- Kombiniert Informationen aus mehreren Quellen
- Generiert Portfolio-Übersichten
- Erstellt Zwischenberichte für Förderer

### 4. Similarity Agent
**Aufgabe**: Ähnlichkeiten finden
- Identifiziert thematische Überschneidungen zwischen Projekten
- Findet potenzielle Synergien
- Schlägt Kooperationsmöglichkeiten vor
- Erkennt Wiederverwendbare Ansätze

### 5. Generator Agent
**Aufgabe**: Neue Dokumente erstellen
- Generiert Anträge basierend auf Templates und früheren Projekten
- Erstellt Meeting-Agendas und Protokolle
- Verfasst Korrespondenz
- Entwickelt Publikations-Entwürfe

### 6. Analyzer Agent
**Aufgabe**: Dokumente analysieren
- Extrahiert Budget-Informationen
- Analysiert Projektstatus und Fortschritt
- Identifiziert Risiken und Probleme
- Erstellt Timeline-Visualisierungen

## Arbeiten mit dem System

### Neues Projekt anlegen
1. Projekt-Index-Datei unter `projects/[projekt-id].md` erstellen
2. Template verwenden und Basis-Informationen ausfüllen
3. Links zu allen relevanten Dokumenten hinzufügen (SharePoint, Confluence, etc.)
4. Schlagworte und verwandte Projekte eintragen
5. Visitor Agent zur Validierung und Vervollständigung ausführen

### Bericht erstellen
1. Template aus `templates/` auswählen
2. Reporter Agent mit Projekt-ID und Template aufrufen
3. Agent sammelt Informationen aus verlinkten Dokumenten (auch externe Quellen)
4. Generierter Bericht lokal in `reports/` ablegen oder in Zielsystem hochladen
5. Manuelle Überprüfung und Anpassung

### Portfolio-Analyse
1. Similarity Agent auf alle Projekt-Indexe anwenden
2. Agent analysiert Metadaten und ggf. verlinkte Dokumente
3. Report in `reports/analytics/` generieren
4. Erkenntnisse für strategische Planung nutzen

### Dokument verstehen
1. Summarizer Agent mit Dokument-URL oder Pfad aufrufen
2. Agent greift auf Dokument zu (lokal oder remote)
3. Relevante Informationen extrahieren
4. In Kontext anderer Projekt-Dokumente setzen

## Benennungskonventionen

### Projekt-IDs
- Kleinbuchstaben, Bindestriche
- Format: `[akronym]-[jahr]` z.B. `ki-gesundheit-2024`
- Kurz und aussagekräftig

### Dateinamen
- Kleinbuchstaben, Bindestriche
- Datum in ISO-Format: `YYYY-MM-DD`
- Beschreibend: `2024-01-15-kickoff-meeting.md`
- Versionierung wenn nötig: `zwischenbericht-v2.md`

### Dokument-Referenzen
- URLs vollständig und mit Zugriffsdatum
- Für externe Systeme: Authentifizierung dokumentieren
- Bei lokalem Zugriff: Relative Pfade vom Repository-Root
- Versionierung bei Cloud-Dokumenten beachten

## Markdown-Konventionen

### Projekt-Dokumente
- YAML Frontmatter für Metadaten verwenden
- Überschriften-Hierarchie einhalten (H1 für Titel)
- Links relativ zum Projekt-Root
- Tags/Keywords für Durchsuchbarkeit

### Beispiel Frontmatter:
```yaml
---
type: meeting-notes
date: 2024-01-15
project: ki-gesundheit-2024
participants: [Name1, Name2]
topics: [Budget, Milestone-1, Publikation]
---
```

## Best Practices

### Dokumenten-Management
- Regelmäßig `meta.md` aktualisieren
- Konsistente Ordner-Struktur über alle Projekte
- Wichtige Dokumente als Markdown oder PDF
- Originaldokumente (z.B. Excel) zusätzlich zu extrahierten Infos behalten

### Arbeiten mit Agenten
- Klare, spezifische Anfragen stellen
- Context durch Referenz auf Projekt-ID oder Dokument-Pfad geben
- Generierte Dokumente immer manuell prüfen
- Templates kontinuierlich verbessern basierend auf Ergebnissen

### Informations-Extraktion
- Strukturierte Daten in Markdown-Tabellen
- Wichtige Zahlen und Daten hervorheben
- Querverweise zwischen Dokumenten nutzen
- Glossar für Fachbegriffe pflegen

### Datenschutz und Sicherheit
- Keine personenbezogenen Daten ohne Einwilligung
- Vertrauliche Informationen kennzeichnen
- Sensitive Dokumente ggf. lokal halten (nicht in Cloud-Sync)
- Zugriffsrechte auf Repository beachten

## Sprach-Konventionen

- **Dokumentation**: Deutsch (meta.md, Berichte, Meeting-Notizen)
- **Struktur-Elemente**: Englisch (Ordnernamen, Datei-Typen)
- **Code/Scripts**: Englisch (Variablen, Kommentare)
- **Agent-Prompts**: Deutsch oder Englisch je nach Präferenz

# DocBot Custom Agents & Skills

Dieses Verzeichnis enthält Custom Agents und Skills für GitHub Copilot in VS Code.

## Struktur

```
.github/
├── agents/                           # Custom Agent Definitionen
│   └── project-visitor.agent.md     # Project Visitor Agent
│
└── skills/                           # Agent Skills
    ├── mcp-local-rag/                # Local RAG Skills (automatisch)
    └── project-visitor/              # Project Visitor Skills
        ├── SKILL.md                  # Haupt-Skill-Definition
        └── references/               # Detaillierte Referenzen
            ├── projekt-index-format.md
            ├── metadata-extraction.md
            └── document-ingestion.md
```

## Verfügbare Agents

### Project Visitor Agent

**Zweck**: Durchsucht und indexiert Forschungsprojekte, extrahiert Metadaten aus Dokumenten und erstellt Portfolio-Übersichten.

**Verwendung in VS Code**:
1. Öffne Copilot Chat
2. Wähle `@project-visitor` aus der Agents-Dropdown-Liste
3. Gib einen Befehl ein, z.B.:
   - "Indexiere Projekt ki-gesundheit-2024"
   - "Erstelle Portfolio-Übersicht"
   - "Extrahiere Metadaten aus documents/ki-2024/"

**Tools**:
- Local RAG (alle Tools: ingest_file, query_documents, list_files, etc.)
- File Operations (readFiles, writeFiles)
- Code Search (search, fetch)

**Handoffs**:
- → Summarizer: Zusammenfassung erstellen
- → Reporter: Statusbericht generieren

## Skills

### Project Visitor Skill

Detaillierte Anweisungen für den Project Visitor Agent:

- **Workflow**: 5 Phasen (Discovery, Ingestion, Extraktion, Index-Erstellung, Portfolio-Update)
- **Best Practices**: Do's & Don'ts für effektive Projekt-Indexierung
- **Fehlerbehandlung**: Umgang mit häufigen Problemen

**Referenzen**:
- `projekt-index-format.md`: Format und Struktur von Projekt-Index-Dateien
- `metadata-extraction.md`: Strategien zur Metadaten-Extraktion mit Local RAG
- `document-ingestion.md`: Best Practices für Dokument-Ingestion in Local RAG

### MCP Local RAG Skill (automatisch)

Skills für die Verwendung des Local RAG MCP-Servers (wurde automatisch installiert).

## Agent hinzufügen

Um einen neuen Custom Agent zu erstellen:

1. Erstelle `.github/agents/[agent-name].agent.md`
2. Füge YAML Frontmatter hinzu:
   ```yaml
   ---
   name: Agent Name
   description: Kurzbeschreibung
   tools: ['tool1', 'tool2']
   ---
   ```
3. Schreibe Anweisungen im Markdown-Body
4. Optional: Erstelle Skills in `.github/skills/[agent-name]/`

Siehe [VS Code Dokumentation](https://code.visualstudio.com/docs/copilot/customization/custom-agents) für Details.

## Skill hinzufügen

Um einen neuen Skill zu erstellen:

1. Erstelle `.github/skills/[skill-name]/SKILL.md`
2. Füge YAML Frontmatter hinzu:
   ```yaml
   ---
   name: skill-name
   description: Beschreibung wann dieser Skill verwendet wird
   ---
   ```
3. Schreibe detaillierte Anweisungen
4. Optional: Erstelle Referenz-Dateien in `references/`

Siehe [Agent Skills Dokumentation](https://code.visualstudio.com/docs/copilot/customization/agent-skills) für Details.

## Verwendung

### In VS Code Copilot Chat

1. **Agent wählen**: Tippe `@` in Chat und wähle den Agent aus der Liste
2. **Befehl geben**: Beschreibe was der Agent tun soll
3. **Handoff**: Nutze Handoff-Buttons um zu anderen Agents zu wechseln

### Skills werden automatisch geladen

Skills werden automatisch aktiviert wenn:
- Der Agent den Skill benötigt
- Du explizit einen Skill erwähnst
- Die Aufgabe zur Skill-Beschreibung passt

## Weitere Informationen

- **AGENTS.md**: Vollständige Projekt-Dokumentation und Richtlinien
- **templates/**: Vorlagen für Projekt-Index-Dateien und Berichte
- **VS Code Docs**: https://code.visualstudio.com/docs/copilot/customization/custom-agents

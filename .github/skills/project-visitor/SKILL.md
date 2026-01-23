---
name: project-visitor
description: Indexiert Forschungsprojekte, extrahiert Metadaten aus Dokumenten, erstellt Projekt-Index-Dateien und Portfolio-Übersichten. Nutzt Local RAG für semantische Dokumentensuche.
---

# Project Visitor Agent Skills

## Zweck
Dieser Skill unterstützt den Project Visitor Agent beim systematischen Indexieren von Forschungsprojekten, der Extraktion von Metadaten und der Erstellung von Portfolio-Übersichten.

## Workflow

### Phase 1: Projekt-Discovery
1. Prüfe ob Projekt-ID vorhanden
2. Scanne `documents/{projekt-id}/` nach Dokumenten
3. Prüfe ob bereits `projects/{projekt-id}.md` existiert

### Phase 2: Dokument-Ingestion
**Reihenfolge**:
1. Antragsunterlagen (`antrag/`)
2. Berichte (`berichte/`)
3. Publikationen (`publikationen/`)
4. Meeting-Notizen (`meetings/`)
5. Sonstige Dokumente

**Pro Dokument**:
- Prüfe Dateityp (nur PDF, DOCX, TXT, MD)
- Nutze `ingest_file` mit absolutem Pfad
- Warte auf Bestätigung vor nächster Datei
- Notiere Fehler

### Phase 3: Metadaten-Extraktion
**Strategie**: Nutze `query_documents` mit spezifischen Queries

**Standard-Queries**:
```
1. "Was ist der vollständige Titel und das Akronym dieses Projekts?"
2. "Wann beginnt und endet dieses Projekt? Was ist die Projektlaufzeit?"
3. "Wer ist der Principal Investigator und wer sind die Co-PIs?"
4. "Was ist das Gesamtbudget des Projekts in Euro?"
5. "Was sind die Hauptziele dieses Projekts?"
6. "Welche Arbeitspakete gibt es und was ist deren Status?"
7. "Welche Deliverables und Meilensteine sind definiert?"
8. "Welche Schlagworte oder Forschungsthemen beschreiben dieses Projekt?"
```

**Query-Optimierung**:
- Limit 5-10 je nach Fragetyp
- Bei schlechten Scores (> 0.5): Query mit Synonymen erweitern
- Beispiel: "Budget" → "Budget Förderung Finanzierung Mittel Kosten"

### Phase 4: Index-Erstellung
Erstelle `projects/{projekt-id}.md` mit extrahierten Metadaten und Dokumenten-Links.

**Template-Struktur**: Siehe `templates/projekt-index-template.md`

**Hinweise**:
- Fehlende Informationen mit Platzhaltern füllen: `[nicht gefunden]`
- Relative Pfade für lokale Dokumente: `../documents/...`
- Markierung `(lokal)` hinter lokalen Dokumenten

### Phase 5: Portfolio-Update
Aktualisiere `reports/portfolio-overview.md`:

**Format**:
```markdown
# Portfolio-Übersicht - Stand: [Datum]

## Projekte gesamt: [Anzahl]

## Projektliste

| Projekt-ID | Titel | Status | Laufzeit | Budget | PI |
|------------|-------|--------|----------|--------|----|
| ki-2024 | [Titel] | Laufend | 2024-2027 | 500.000 EUR | [Name] |

## Statistiken
- Laufende Projekte: [Anzahl]
- Abgeschlossene Projekte: [Anzahl]
- Gesamtbudget aktiver Projekte: [Summe] EUR

## Fehlende Informationen
[Liste von Projekten mit unvollständigen Daten]
```

## Fehlerbehandlung

### Häufige Probleme

| Problem | Lösung |
|---------|--------|
| Datei nicht gefunden | Absoluten Pfad prüfen, Datei existiert? |
| Datei zu groß (> 100MB) | Nutzer informieren, ggf. Datei aufteilen |
| Keine RAG-Ergebnisse | Query umformulieren, Synonyme hinzufügen |
| Excel/PowerPoint-Dateien | Hinweis: Nicht unterstützt, Konvertierung nötig |
| Encoding-Fehler | Prüfe Zeichensatz, ggf. Datei neu speichern |

## Best Practices

### Do's ✅
- Immer absolute Pfade für `ingest_file` verwenden
- Dokumente sequenziell ingestieren (nicht parallel)
- Spezifische, fokussierte Queries verwenden
- Metadaten validieren bevor in Index schreiben
- Fehlende Informationen explizit markieren

### Don'ts ❌
- Nicht alle Dokumente auf einmal ingestieren
- Nicht mit zu breiten Queries arbeiten ("Alles über Projekt")
- Nicht Excel/PowerPoint direkt ingestieren versuchen
- Nicht ohne Fehlerprüfung weitermachen
- Nicht vergessen Portfolio-Übersicht zu aktualisieren

## Local RAG Integration

### Score-Interpretation
Nutze die mcp-local-rag Skill Guidelines für Score-Interpretation:

| Score | Bedeutung | Aktion |
|-------|-----------|--------|
| < 0.3 | Sehr relevant | Direkt verwenden |
| 0.3-0.5 | Möglicherweise relevant | Prüfen, ob Konzept/Entity passt |
| > 0.5 | Wahrscheinlich irrelevant | Überspringen, Query erweitern |

### Query-Formulierung
- **Spezifisch**: "Was ist das Budget?" statt "Erzähl mir über Finanzen"
- **Kontext**: "Projektlaufzeit Start Ende Datum" statt nur "Datum"
- **Synonyme**: Bei schlechten Ergebnissen erweitern

### Limit-Auswahl
- **Spezifische Fakten** (Budget, Datum): Limit 5
- **Allgemeine Info** (Ziele, Team): Limit 10
- **Umfassende Übersicht**: Limit 20

## Referenzen

Für detaillierte Informationen siehe:
- [projekt-index-format.md](references/projekt-index-format.md) - Projekt-Index-Format und Beispiele
- [metadata-extraction.md](references/metadata-extraction.md) - Extraktions-Strategien für verschiedene Metadaten
- [document-ingestion.md](references/document-ingestion.md) - Local RAG Integration Details

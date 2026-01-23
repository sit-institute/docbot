# Local RAG Dokument-Ingestion

## Übersicht

Diese Referenz beschreibt Best Practices für die Ingestion von Projektdokumenten in Local RAG.

## Local RAG Konfiguration

### BASE_DIR
Alle Dokumente müssen innerhalb des konfigurierten `BASE_DIR` liegen.

**Standard-Konfiguration für DocBot**:
```
BASE_DIR=/home/peter/Dokumente/Repositories/docbot/documents
```

**Struktur**:
```
documents/
├── projekt-1/
│   ├── antrag/
│   ├── berichte/
│   └── ...
└── projekt-2/
    └── ...
```

### Wichtig
- **Absolute Pfade** verwenden für `ingest_file`
- Relative Pfade funktionieren **nicht**
- Dateien außerhalb `BASE_DIR` werden abgelehnt

## Unterstützte Dateiformate

### ✅ Vollständig unterstützt

| Format | Erkennung | Hinweise |
|--------|-----------|----------|
| **PDF** | `.pdf` | Via pdfjs-dist, Text-Layer erforderlich |
| **DOCX** | `.docx` | Via mammoth, moderne Word-Dokumente |
| **TXT** | `.txt` | Plain text, alle Encodings |
| **Markdown** | `.md`, `.markdown` | Native Unterstützung |

### ❌ Nicht unterstützt

| Format | Warum nicht | Alternative |
|--------|-------------|-------------|
| **Excel** | `.xlsx`, `.xls` | Keine automatische Extraktion | Manuelle Konvertierung zu CSV oder PDF |
| **PowerPoint** | `.pptx`, `.ppt` | Keine Text-Extraktion | Export als PDF |
| **Bilder** | `.jpg`, `.png`, `.gif` | Kein OCR verfügbar | OCR extern durchführen |
| **Archive** | `.zip`, `.tar`, `.gz` | Nicht entpackt | Manuell entpacken |
| **RTF** | `.rtf` | Nicht implementiert | Konvertierung zu DOCX |

## Ingestion-Workflow

### 1. Dokumente scannen

```markdown
Schritt 1: Liste alle Dateien in documents/{projekt-id}/
Schritt 2: Filtere nach unterstützten Formaten
Schritt 3: Priorisiere nach Ordner-Typ
```

**Prioritäts-Reihenfolge**:
1. `antrag/` - Antragsunterlagen (wichtigste Metadaten)
2. `berichte/` - Projektberichte (aktueller Status)
3. `publikationen/` - Papers (wissenschaftlicher Kontext)
4. `meetings/` - Meeting-Notizen (laufende Entwicklung)
5. Rest - Sonstige Dokumente

### 2. Dateityp prüfen

```python
# Pseudocode für Dateityp-Prüfung
supported_extensions = ['.pdf', '.docx', '.txt', '.md', '.markdown']
unsupported_extensions = ['.xlsx', '.xls', '.pptx', '.ppt', '.jpg', '.png', '.zip']

if file.extension in supported_extensions:
    ingest_file(file)
elif file.extension in unsupported_extensions:
    log_warning(f"Übersprungen: {file} - Format nicht unterstützt")
else:
    log_info(f"Übersprungen: {file} - Unbekannter Typ")
```

### 3. Ingestion durchführen

**Tool**: `ingest_file`

**Syntax**:
```
ingest_file({
  "filePath": "/absolute/path/to/document.pdf"
})
```

**Beispiel**:
```
ingest_file({
  "filePath": "/home/peter/Dokumente/Repositories/docbot/documents/ki-2024/antrag/vollantrag.pdf"
})
```

### 4. Ingestion bestätigen

Nach jeder Ingestion:
- ✅ Erfolg: Anzahl der erstellten Chunks notieren
- ❌ Fehler: Fehlertyp und Datei notieren
- ⏱️ Warten: Kurze Pause vor nächster Datei (Ressourcen)

**Erfolgreiche Ingestion**:
```
Successfully ingested vollantrag.pdf (47 chunks created)
```

**Fehlgeschlagene Ingestion**:
```
Error ingesting vollantrag.pdf: File too large (>100MB)
```

## Chunk-Strategie

Local RAG verwendet **semantisches Chunking**:
- Dokumente werden in sinnvolle Abschnitte geteilt
- Chunk-Größe: typisch 500-1000 Zeichen
- Code-Blöcke bleiben intakt (nicht mitten im Code splitten)
- Natürliche Topic-Grenzen werden erkannt

**Implikation für Queries**:
- Queries sollten spezifisch genug sein um relevante Chunks zu finden
- Breite Queries ("Was ist das Projekt über?") funktionieren schlechter als spezifische ("Was ist das Budget?")

## Re-Ingestion

**Wann re-ingestieren?**
- Dokument wurde aktualisiert
- Erste Ingestion fehlgeschlagen (nach Korrektur)
- Dokument soll neu indexiert werden

**Wie**:
Einfach gleiche Datei erneut mit `ingest_file` ingestieren
→ Alte Version wird automatisch überschrieben

**Beispiel**:
```
1. Ingest vollantrag.pdf → 47 chunks
2. Vollantrag wird aktualisiert
3. Re-ingest vollantrag.pdf → 52 chunks (alt gelöscht, neu erstellt)
```

## Fehlerbehandlung

### Datei nicht gefunden

**Fehler**: `File not found: /path/to/file.pdf`

**Lösungen**:
1. Pfad prüfen (absolut? korrekt?)
2. Datei existiert?
3. Schreibrechte?

### Datei zu groß

**Fehler**: `File too large (>100MB)`

**Standard-Limit**: 100MB (konfigurierbar via `MAX_FILE_SIZE`)

**Lösungen**:
1. Große PDFs aufteilen
2. Limit erhöhen (nicht empfohlen für Performance)
3. Nur relevante Seiten extrahieren

### Encoding-Fehler

**Fehler**: `Encoding error: ...`

**Lösungen**:
1. Datei mit UTF-8 neu speichern
2. Bei PDFs: Mit anderer Software neu generieren
3. Bei TXT: Encoding explizit konvertieren

### PDF ohne Text-Layer

**Problem**: PDF enthält nur Bilder, kein extrahierbarer Text

**Erkennung**: Ingestion erfolgreich, aber 0 oder sehr wenige Chunks

**Lösung**: OCR extern durchführen, dann neu speichern

### Path outside BASE_DIR

**Fehler**: `Path outside BASE_DIR`

**Ursache**: Datei liegt nicht unter `documents/`

**Lösung**: 
1. Datei nach `documents/` verschieben
2. `BASE_DIR` anpassen (nicht empfohlen)

## Performance-Überlegungen

### Ingestion-Geschwindigkeit

**Typische Zeiten** (MacBook Pro M1, 16GB RAM):
- 10MB PDF: ~8s Parsing + ~30s Embedding + ~5s DB
- 100 Seiten DOCX: ~2s Parsing + ~25s Embedding + ~4s DB
- 1MB TXT: <1s Parsing + ~10s Embedding + ~2s DB

### Memory-Nutzung
- Idle: ~200MB
- Peak (50MB Datei): ~800MB

### Parallele Ingestion
**Nicht empfohlen**: Local RAG ist für sequenzielle Verarbeitung optimiert
- Parallele Ingestion kann zu Memory-Problemen führen
- Ressourcen-Contention verschlechtert Performance

**Best Practice**: Dokumente sequenziell ingestieren mit kurzer Pause

## Ingestion-Log erstellen

### Format

```markdown
## Ingestion-Log: {Projekt-ID}

### Erfolgreich ingestiert
- ✅ antrag/vollantrag.pdf (47 chunks, 8.2s)
- ✅ berichte/zwischenbericht-2024.md (23 chunks, 2.1s)
- ✅ publikationen/paper-2024.pdf (65 chunks, 12.4s)

### Übersprungen
- ⚠️ antrag/budget.xlsx (Excel nicht unterstützt)
- ⚠️ deliverables/d1-prototype.zip (Archive nicht unterstützt)
- ⚠️ meetings/2024-01-15-slides.pptx (PowerPoint nicht unterstützt)

### Fehlgeschlagen
- ❌ berichte/jahresbericht-2024.pdf (Datei zu groß: 125MB)

### Statistik
- Gesamt: 15 Dateien gescannt
- Ingestiert: 3 (100 chunks)
- Übersprungen: 11
- Fehlgeschlagen: 1
- Dauer: 22.7s
```

## Post-Ingestion Checks

Nach erfolgreicher Ingestion:

### 1. Status prüfen
```
status()
```
Prüft:
- Anzahl Chunks gesamt
- DB-Größe
- Modell-Info

### 2. Liste ingestierte Dateien
```
list_files()
```
Zeigt alle erfolgreich ingestierten Dateien

### 3. Test-Query
```
query_documents({
  "query": "Projekttitel",
  "limit": 5
})
```
Validiert dass Dokumente durchsuchbar sind

## Ingestion-Checklist

Vor der Ingestion:
- [ ] `BASE_DIR` korrekt konfiguriert
- [ ] Projekt-Ordner `documents/{projekt-id}/` existiert
- [ ] Dateien liegen in korrekter Struktur
- [ ] Absolute Pfade bereit

Während der Ingestion:
- [ ] Nur unterstützte Formate (PDF, DOCX, TXT, MD)
- [ ] Sequenzielle Verarbeitung (nicht parallel)
- [ ] Fehler-Logging aktiviert
- [ ] Progress-Tracking

Nach der Ingestion:
- [ ] Status prüfen (`status()`)
- [ ] Ingestierte Dateien listen (`list_files()`)
- [ ] Test-Query durchführen
- [ ] Ingestion-Log erstellen

## Beispiel: Vollständiger Ingestion-Workflow

```markdown
## Projekt: ki-gesundheit-2024

### 1. Scan
documents/ki-gesundheit-2024/
├── antrag/
│   ├── vollantrag.pdf ✅
│   ├── budget.xlsx ⚠️
│   └── kooperation.pdf ✅
├── berichte/
│   ├── zwischenbericht-2024.md ✅
│   └── praesentation.pptx ⚠️
└── publikationen/
    └── paper-2024.pdf ✅

### 2. Priorisierung
1. antrag/vollantrag.pdf (höchste Priorität)
2. antrag/kooperation.pdf
3. berichte/zwischenbericht-2024.md
4. publikationen/paper-2024.pdf

### 3. Ingestion

**Datei 1**: vollantrag.pdf
- Pfad: /home/.../documents/ki-gesundheit-2024/antrag/vollantrag.pdf
- Tool: ingest_file
- Result: ✅ 47 chunks, 8.2s

**Datei 2**: kooperation.pdf
- Pfad: /home/.../documents/ki-gesundheit-2024/antrag/kooperation.pdf
- Tool: ingest_file
- Result: ✅ 15 chunks, 3.1s

**Datei 3**: zwischenbericht-2024.md
- Pfad: /home/.../documents/ki-gesundheit-2024/berichte/zwischenbericht-2024.md
- Tool: ingest_file
- Result: ✅ 23 chunks, 2.1s

**Datei 4**: paper-2024.pdf
- Pfad: /home/.../documents/ki-gesundheit-2024/publikationen/paper-2024.pdf
- Tool: ingest_file
- Result: ✅ 65 chunks, 12.4s

### 4. Validation
```
status() → 150 chunks total, 4 files
query_documents("Projekttitel") → Score 0.08 ✓
```

### 5. Summary
- ✅ 4 Dokumente erfolgreich ingestiert (150 chunks)
- ⚠️ 2 Dokumente übersprungen (Excel, PowerPoint)
- Gesamt-Dauer: 25.8s
- Bereit für Metadaten-Extraktion
```

## Troubleshooting Guide

### Problem: Keine Chunks erstellt

**Symptom**: Ingestion erfolgreich, aber 0 chunks

**Mögliche Ursachen**:
1. PDF ohne Text-Layer (nur Bilder)
2. DOCX leer oder korrupt
3. TXT-Datei leer

**Lösung**:
- PDF: OCR durchführen
- DOCX: Datei öffnen und prüfen
- TXT: Datei-Inhalt prüfen

### Problem: Sehr wenige Chunks

**Symptom**: Große Datei, aber nur 1-2 chunks

**Mögliche Ursachen**:
1. Dokument enthält wenig Text (viele Grafiken)
2. Text ist in Bildern (OCR fehlt)
3. Encoding-Probleme

**Lösung**:
- Dokument manuell prüfen
- OCR wenn nötig
- Encoding korrigieren

### Problem: Query findet nichts

**Symptom**: Dokumente ingestiert, aber Queries liefern keine Ergebnisse

**Mögliche Ursachen**:
1. Query zu spezifisch
2. Falsche Sprache (Modell auf Englisch trainiert)
3. Zu hoher Score-Threshold

**Lösung**:
- Query erweitern
- Synonyme nutzen
- Limit erhöhen
- Score-Threshold senken

# Metadaten-Extraktion aus Projektdokumenten

## Übersicht

Diese Referenz beschreibt Strategien zur Extraktion von Metadaten aus Forschungsprojekt-Dokumenten mittels Local RAG.

## Allgemeine Prinzipien

### 1. Query-Formulierung
- **Spezifisch**: Fokussierte Fragen stellen
- **Kontextreich**: Relevante Synonyme einbeziehen
- **Strukturiert**: Eine Frage pro Metadatum

### 2. Limit-Auswahl
| Metadatum-Typ | Empfohlenes Limit | Begründung |
|---------------|-------------------|------------|
| Fakten (Budget, Datum) | 5 | Präzise Antwort erwartet |
| Listen (Ziele, Team) | 10 | Mehrere Items erwartet |
| Beschreibungen | 10-15 | Umfassender Kontext nötig |

### 3. Score-Interpretation
- **< 0.3**: Direkt verwenden
- **0.3-0.5**: Validieren ob Kontext passt
- **> 0.5**: Query erweitern oder als "nicht gefunden" markieren

## Metadaten-Typen und Extraktions-Strategien

### 1. Projekt-Titel und Akronym

**Query**:
```
"Was ist der vollständige Titel und das Akronym dieses Forschungsprojekts?"
```

**Limit**: 5

**Erwartetes Format**: 
- Titel: Vollständiger Name
- Akronym: Kurzform in Großbuchstaben

**Fallbacks**:
- Wenn nur Titel gefunden: Akronym aus Anfangsbuchstaben generieren
- Wenn nur Akronym: Query erweitern: "Projekttitel Projektname vollständiger Name"

**Beispiel-Extraktion**:
```
Query: "Was ist der vollständige Titel und das Akronym dieses Projekts?"
Result: "Das Projekt 'KI-gestützte Diagnose in der Gesundheitsversorgung' (KI-Diagnose) entwickelt..."
→ Titel: "KI-gestützte Diagnose in der Gesundheitsversorgung"
→ Akronym: "KI-Diagnose"
```

### 2. Projektlaufzeit (Start- und Enddatum)

**Query**:
```
"Wann beginnt und endet dieses Projekt? Was ist die Projektlaufzeit Start- und Enddatum?"
```

**Limit**: 5

**Erwartetes Format**: ISO-Datum (YYYY-MM-DD)

**Query-Varianten bei schlechten Ergebnissen**:
```
- "Projektbeginn Projektstart Startdatum Datum Beginn"
- "Projektende Abschlussdatum Enddatum Laufzeit"
- "Laufzeit Dauer von bis Zeitraum"
```

**Parsing-Logik**:
- Extrahiere Datumsangaben aus Text
- Konvertiere in ISO-Format
- Wenn nur Jahr: Verwende 01.01. bzw. 31.12.

**Beispiele**:
```
"Das Projekt läuft von Januar 2024 bis Dezember 2026"
→ Laufzeit: 2024-01-01 bis 2026-12-31

"Projektstart: 01.03.2024, Projektende: 28.02.2027"
→ Laufzeit: 2024-03-01 bis 2027-02-28

"36 Monate ab 2024"
→ Laufzeit: 2024-01-01 bis 2026-12-31 (berechnet)
```

### 3. Budget

**Query**:
```
"Was ist das Gesamtbudget des Projekts in Euro? Wie hoch ist die Fördersumme Finanzierung?"
```

**Limit**: 5

**Query-Erweiterung bei schlechten Ergebnissen**:
```
"Budget Fördersumme Finanzierung Mittel Kosten Gesamtkosten Förderung EUR Euro"
```

**Parsing-Logik**:
- Extrahiere Zahlen mit EUR/Euro
- Konvertiere Tausender-Trennzeichen
- Beachte Einheiten: Tausend, Mio., etc.

**Beispiele**:
```
"Das Projekt wird mit 500.000 EUR gefördert"
→ Budget: 500.000 EUR

"Gesamtkosten: 1,2 Mio. Euro"
→ Budget: 1.200.000 EUR

"Budget: 250k EUR"
→ Budget: 250.000 EUR
```

**Hinweis**: Wenn Budget nur als Excel-Tabelle verfügbar → `[nicht in Textform verfügbar]`

### 4. Status

**Query**:
```
"Was ist der aktuelle Status des Projekts? Ist das Projekt laufend abgeschlossen in Vorbereitung?"
```

**Limit**: 5

**Mapping zu Standard-Status**:
| Gefundener Text | Standard-Status |
|-----------------|-----------------|
| "in Vorbereitung", "geplant", "beantragt" | In Vorbereitung |
| "laufend", "aktiv", "in Bearbeitung" | Laufend |
| "abgeschlossen", "beendet", "finalisiert" | Abgeschlossen |
| "abgebrochen", "eingestellt" | Abgebrochen |

**Fallback**: Wenn kein expliziter Status → Aus Laufzeit ableiten:
- Start > Heute → In Vorbereitung
- Start ≤ Heute < Ende → Laufend
- Ende < Heute → Abgeschlossen

### 5. Förderer und Förderprogramm

**Query**:
```
"Wer ist der Förderer und was ist das Förderprogramm dieses Projekts?"
```

**Limit**: 5

**Häufige Förderer** (zur Normalisierung):
- BMBF → Bundesministerium für Bildung und Forschung
- DFG → Deutsche Forschungsgemeinschaft
- EU, H2020, Horizon Europe
- BMWi → Bundesministerium für Wirtschaft

**Beispiele**:
```
"Gefördert durch das BMBF im Rahmen des Programms 'Digitalisierung im Gesundheitswesen'"
→ Förderer: BMBF
→ Förderprogramm: Digitalisierung im Gesundheitswesen
```

### 6. Projektteam

**Queries** (sequenziell):
```
1. "Wer ist der Principal Investigator PI Projektleiter dieses Projekts?"
2. "Wer sind die Co-PIs Co-Principal-Investigators Co-Projektleiter?"
3. "Welche Mitarbeiter Doktoranden PostDocs arbeiten in diesem Projekt?"
4. "Welche Partner Kooperationspartner Institutionen sind beteiligt?"
```

**Limit**: 10 pro Query

**Parsing-Logik**:
- Extrahiere Namen mit Titeln (Prof., Dr., etc.)
- Trenne Personen und Organisationen
- Bei Partnern: Nur Organisationen, keine Personen

**Beispiele**:
```
"Das Projekt wird geleitet von Prof. Dr. Maria Schmidt (UKB) zusammen mit Dr. Thomas Müller"
→ PI: Prof. Dr. Maria Schmidt
→ Co-PIs: Dr. Thomas Müller
→ Partner: UKB (wenn Organisation gemeint)
```

### 7. Inhalt/Beschreibung

**Query**:
```
"Was ist der Inhalt und die Zielsetzung dieses Projekts? Worum geht es in diesem Forschungsprojekt?"
```

**Limit**: 15

**Verarbeitung**:
- Extrahiere 2-3 prägnanteste Sätze
- Fokus auf "Was" und "Warum", nicht "Wie"
- Entferne Floskeln und administrative Details

### 8. Ziele

**Query**:
```
"Was sind die Hauptziele und Forschungsziele dieses Projekts?"
```

**Limit**: 15

**Verarbeitung**:
- Extrahiere nummerierte oder aufgelistete Ziele
- Konvertiere in klare, nummerierte Liste
- Fokus auf messbare Outcomes

**Beispiel**:
```
RAG-Result: "Das Projekt verfolgt folgende Ziele: (1) Entwicklung eines ML-Modells, 
(2) Integration in Krankenhaus-IT, (3) Klinische Validierung"
→ 
1. Entwicklung eines ML-Modells
2. Integration in Krankenhaus-IT
3. Klinische Validierung
```

### 9. Arbeitspakete

**Query**:
```
"Welche Arbeitspakete Work Packages WP gibt es in diesem Projekt und was ist deren Status?"
```

**Limit**: 15

**Format**:
```
- **WP1**: [Name] - [Status]
```

**Status-Mapping**:
- Nicht begonnen → In Vorbereitung
- Ongoing, laufend → Laufend
- Completed, done → Abgeschlossen
- Delayed → Verzögert

### 10. Deliverables

**Query**:
```
"Welche Deliverables Ergebnisse Projektergebnisse gibt es mit Fälligkeitsdatum?"
```

**Limit**: 15

**Format**:
```
- **D1.1**: [Name] - Fällig: YYYY-MM-DD - Status: ✓/○
```

**Status-Symbol**:
- ✓ = Abgeschlossen
- ○ = Ausstehend
- ⚠ = Verzögert

### 11. Meilensteine

**Query**:
```
"Welche Meilensteine Milestones gibt es in diesem Projekt mit Datum?"
```

**Limit**: 10

**Format**:
```
- **M1**: [Name] - [Datum] - [Status]
```

### 12. Schlagworte

**Query**:
```
"Welche Schlagworte Keywords Forschungsthemen beschreiben dieses Projekt?"
```

**Limit**: 15

**Verarbeitung**:
- Extrahiere Fachbegriffe
- Entferne generische Begriffe ("Projekt", "Forschung")
- Komma-separierte Liste

## Umgang mit fehlenden Informationen

### Strategie 1: Query-Erweiterung
Bei Score > 0.5 oder keinen Ergebnissen:
1. Synonyme hinzufügen
2. Limit erhöhen auf 20
3. Verwandte Begriffe nutzen

### Strategie 2: Alternative Quellen
- Prüfe Dateinamen: `zwischenbericht-2024.pdf` → Jahr extrahieren
- Prüfe Ordnerstruktur: `antrag/` → Antragsunterlagen
- Nutze Metadaten aus anderen Projekten als Template

### Strategie 3: Platzhalter
Wenn nach 2 Versuchen keine Daten:
```markdown
- **Budget**: [nicht gefunden]
- **Förderprogramm**: [nicht in Dokumenten verfügbar]
```

## Validierung extrahierter Metadaten

### Plausibilitätsprüfungen
- **Laufzeit**: Start < Ende, nicht mehr als 10 Jahre
- **Budget**: Positiv, typisch 50k-10M EUR für Forschungsprojekte
- **Daten**: Valides Format (ISO)
- **Namen**: Titel (Prof., Dr.) konsistent

### Cross-Referenzierung
Wenn möglich, Informationen aus mehreren Dokumenten abgleichen:
- Budget im Antrag vs. im Bericht
- Laufzeit im Antrag vs. tatsächliche Laufzeit
- Teammitglieder in verschiedenen Dokumenten

## Beispiel-Workflow

```markdown
## Extraktion für Projekt: ki-gesundheit-2024

### 1. Dokumente ingestiert
- vollantrag.pdf
- zwischenbericht-2024.pdf
- projektbeschreibung.md

### 2. Metadaten-Extraktion

**Titel & Akronym**
Query: "Was ist der vollständige Titel und das Akronym dieses Projekts?"
Result (Score 0.12): "KI-gestützte Diagnose in der Gesundheitsversorgung (KI-Diagnose)"
✓ Extrahiert

**Laufzeit**
Query: "Wann beginnt und endet dieses Projekt?"
Result (Score 0.25): "Das Projekt läuft von Januar 2024 bis Dezember 2026"
✓ Extrahiert: 2024-01-01 bis 2026-12-31

**Budget**
Query: "Was ist das Gesamtbudget des Projekts in Euro?"
Result (Score 0.68): [Zu hoher Score]
Query erweitert: "Budget Fördersumme Finanzierung Mittel Kosten EUR"
Result (Score 0.32): "Gesamtförderung 500.000 EUR"
✓ Extrahiert: 500.000 EUR

**Status**
Query: "Was ist der aktuelle Status des Projekts?"
Result (Score 0.78): [Kein gutes Ergebnis]
Fallback: Aus Laufzeit → Laufend (Start < Heute < Ende)
✓ Abgeleitet

[...weitere Metadaten...]
```

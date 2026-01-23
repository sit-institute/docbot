# Projekt-Index Format

## Übersicht

Das Projekt-Index-Format ist eine standardisierte Markdown-Datei, die alle wichtigen Metadaten und Links zu Dokumenten eines Forschungsprojekts enthält.

## Dateiname

`projects/{projekt-id}.md`

**Projekt-ID Konventionen**:
- Kleinbuchstaben, Bindestriche
- Format: `[akronym]-[jahr]`
- Beispiele: `ki-gesundheit-2024`, `horizon-digitalisierung-2025`

## Struktur

### 1. Titel (H1)
Vollständiger Projekt-Titel

```markdown
# KI-gestützte Diagnose in der Gesundheitsversorgung
```

### 2. Basis-Informationen

```markdown
## Basis-Informationen
- **Projekt-ID**: ki-gesundheit-2024
- **Akronym**: KI-Diagnose
- **Laufzeit**: 2024-01-01 bis 2026-12-31
- **Status**: Laufend
- **Budget**: 500.000 EUR
- **Förderer**: BMBF
- **Förderprogramm**: Digitalisierung im Gesundheitswesen
```

**Felder**:
- **Projekt-ID**: Eindeutiger Identifier (Pflicht)
- **Akronym**: Kurz-Akronym (optional)
- **Laufzeit**: Start- und Enddatum im ISO-Format (Pflicht)
- **Status**: Einer von: `In Vorbereitung`, `Laufend`, `Abgeschlossen`, `Abgebrochen`
- **Budget**: Gesamtbudget in EUR (optional)
- **Förderer**: Name des Förderers (optional)
- **Förderprogramm**: Programmname (optional)

### 3. Projektteam

```markdown
## Projektteam
- **PI**: Prof. Dr. Maria Schmidt
- **Co-PIs**: Dr. Thomas Müller, Dr. Anna Weber
- **Mitarbeiter**: Sarah Klein (Doktorandin), Max Fischer (PostDoc)
- **Partner**: Universitätsklinikum Berlin, Fraunhofer Institut
```

**Felder**:
- **PI**: Principal Investigator (Pflicht)
- **Co-PIs**: Co-Principal Investigators (optional, komma-separiert)
- **Mitarbeiter**: Projektmitarbeiter (optional, komma-separiert)
- **Partner**: Kooperationspartner (optional, komma-separiert)

### 4. Inhalt

```markdown
## Inhalt
Entwicklung eines KI-basierten Systems zur Unterstützung der medizinischen Diagnostik. 
Das Projekt kombiniert Machine Learning mit klinischer Expertise um Diagnose-Genauigkeit 
zu verbessern und Ärzte im Arbeitsalltag zu entlasten.
```

**Beschreibung**: 2-3 Sätze Kurzbeschreibung des Projekts

### 5. Ziele

```markdown
## Ziele
1. Entwicklung eines ML-Modells zur Diagnose-Unterstützung mit 95% Genauigkeit
2. Integration in bestehende Krankenhaus-Informationssysteme
3. Klinische Evaluierung mit 1000 Patienten
4. Erstellung von Best-Practice-Leitlinien für KI in der Diagnostik
```

**Format**: Nummerierte Liste der Hauptziele

### 6. Arbeitspakete

```markdown
## Arbeitspakete
- **WP1**: Anforderungsanalyse - Abgeschlossen
- **WP2**: Datensammlung und -aufbereitung - Laufend
- **WP3**: Modellentwicklung - Laufend
- **WP4**: Klinische Validierung - In Vorbereitung
- **WP5**: Dissemination - In Vorbereitung
```

**Format**: Liste mit Name und Status
**Status-Optionen**: `In Vorbereitung`, `Laufend`, `Abgeschlossen`, `Verzögert`, `Abgebrochen`

### 7. Deliverables

```markdown
## Deliverables
- **D1.1**: Anforderungsdokument - Fällig: 2024-06-30 - Status: ✓
- **D2.1**: Datensatz (anonymisiert) - Fällig: 2024-12-31 - Status: ○
- **D3.1**: ML-Modell v1.0 - Fällig: 2025-06-30 - Status: ○
- **D4.1**: Evaluationsbericht - Fällig: 2026-06-30 - Status: ○
- **D5.1**: Abschlussbericht - Fällig: 2026-12-31 - Status: ○
```

**Format**: Liste mit ID, Name, Fälligkeitsdatum, Status
**Status-Symbole**: `✓` (abgeschlossen), `○` (ausstehend), `⚠` (verzögert)

### 8. Meilensteine

```markdown
## Meilensteine
- **M1**: Projektstart - 2024-01-01 - Erreicht
- **M2**: Datensammlung abgeschlossen - 2024-12-31 - Geplant
- **M3**: Modell trainiert - 2025-06-30 - Geplant
- **M4**: Klinische Tests abgeschlossen - 2026-06-30 - Geplant
- **M5**: Projektende - 2026-12-31 - Geplant
```

**Format**: Liste mit Name, Datum, Status
**Status-Optionen**: `Erreicht`, `Geplant`, `Verzögert`, `Gefährdet`

### 9. Schlagworte

```markdown
## Schlagworte
Künstliche Intelligenz, Machine Learning, Medizinische Diagnostik, Deep Learning, 
Gesundheitswesen, Bildverarbeitung, Klinische Validierung
```

**Format**: Komma-separierte Liste von Keywords/Tags

### 10. Verwandte Projekte

```markdown
## Verwandte Projekte
- [ki-radiologie-2023](ki-radiologie-2023.md): Gemeinsame Dateninfrastruktur
- [digital-klinik-2024](digital-klinik-2024.md): Ähnliche Technologie-Stack
- [ml-medizin-2025](ml-medizin-2025.md): Potenzielle Zusammenarbeit bei Dissemination
```

**Format**: Liste mit Link zum Projekt-Index und Beschreibung der Beziehung

### 11. Dokumente

```markdown
## Dokumente

### Antrag
- [Vollantrag PDF](../documents/ki-gesundheit-2024/antrag/vollantrag.pdf) (lokal)
- [Budget-Kalkulation](../documents/ki-gesundheit-2024/antrag/budget.xlsx) (lokal)
- [Kooperationsvereinbarung UKB](../documents/ki-gesundheit-2024/antrag/kooperation-ukb.pdf) (lokal)
- [Projektbeschreibung](https://gitlab.example.com/ki-gesundheit/wiki/beschreibung) (GitLab)

### Berichte
- [Zwischenbericht 2024](https://confluence.example.com/projects/KI-Gesundheit/zwischenbericht-2024) (Confluence)
- [Jahresbericht 2024](../documents/ki-gesundheit-2024/berichte/jahresbericht-2024.pdf) (lokal)
- [Meeting-Notizen](https://notion.so/ki-gesundheit/meetings) (Notion)

### Publikationen
- [Paper: ML in Medical Diagnosis](../documents/ki-gesundheit-2024/publikationen/paper-2024-ml-diagnosis.pdf) (lokal)
- [Conference Abstract](../documents/ki-gesundheit-2024/publikationen/abstract-medinfo-2025.md) (lokal)

### Daten & Analysen
- [Anonymisierter Datensatz](../documents/ki-gesundheit-2024/data/dataset-anonymized.csv) (lokal)
- [Evaluationsergebnisse](../documents/ki-gesundheit-2024/data/evaluation-results.csv) (lokal)
- [Modell-Metriken](../documents/ki-gesundheit-2024/data/model-metrics/) (lokal)

### Meetings
- [Kickoff Meeting 2024-01-15](../documents/ki-gesundheit-2024/meetings/2024-01-15-kickoff.pdf) (lokal)
- [Review Meeting Q2](../documents/ki-gesundheit-2024/meetings/2024-06-20-review.md) (lokal)

### Deliverables
- [D1.1 Anforderungsdokument](../documents/ki-gesundheit-2024/deliverables/d1-1-requirements.pdf) (lokal)

### Kommunikation
- [Slack Channel #ki-gesundheit](https://example.slack.com/archives/C123456) (Slack)
- [Jira Board](https://jira.example.com/projects/KIGES2024) (Jira)
- [E-Mail Korrespondenz Förderer](../documents/ki-gesundheit-2024/correspondence/foerderer/) (lokal)
```

**Format**: 
- Gruppiert nach Dokumenttyp (Antrag, Berichte, etc.)
- Markdown-Links mit Beschreibung
- Lokale Dokumente: Relative Pfade `../documents/{projekt-id}/...` + `(lokal)` Markierung
- Externe Dokumente: Vollständige URL + Plattform-Name in Klammern

### 12. Wichtige Links

```markdown
## Wichtige Links
- Projektwebsite: https://ki-gesundheit.example.com
- GitHub Repository: https://github.com/example/ki-gesundheit
- Förderer-Portal: https://foerderportal.bmbf.de/projects/ki-gesundheit-2024
- Zenodo Record: https://zenodo.org/record/123456
```

**Format**: Liste mit Beschreibung und URL

## Vollständiges Beispiel

Siehe Datei: `templates/projekt-index-template.md` für ein vollständiges ausgefülltes Beispiel.

## Fehlende Informationen

Wenn Informationen nicht extrahiert werden können, nutze Platzhalter:

```markdown
- **Budget**: [nicht gefunden]
- **Förderprogramm**: [nicht in Dokumenten verfügbar]
```

## Optionale Abschnitte

Folgende Abschnitte können bei Bedarf hinzugefügt werden:

### Risiken
```markdown
## Risiken
- **R1**: Datenschutz-Compliance - Wahrscheinlichkeit: Mittel - Impact: Hoch - Mitigation: Juristische Prüfung
- **R2**: Rekrutierung Patienten - Wahrscheinlichkeit: Hoch - Impact: Mittel - Mitigation: Erweiterte Ansprache
```

### Zeitplan
```markdown
## Zeitplan
- Q1 2024: Anforderungsanalyse, Datensammlung Start
- Q2 2024: Datensammlung, Erste Modell-Experimente
- Q3 2024: Modelltraining, Validierung
- Q4 2024: Zwischenbericht, Anpassungen
```

### Budget-Übersicht
```markdown
## Budget-Übersicht
- Personal: 350.000 EUR (70%)
- Sachmittel: 100.000 EUR (20%)
- Reisen: 30.000 EUR (6%)
- Verwaltung: 20.000 EUR (4%)
```

## Validierung

Eine gültige Projekt-Index-Datei muss enthalten:
- ✅ Titel (H1)
- ✅ Projekt-ID in Basis-Informationen
- ✅ Laufzeit (Start- und Enddatum)
- ✅ Status
- ✅ Principal Investigator
- ✅ Mindestens ein Ziel oder eine Inhaltsbeschreibung

Empfohlen:
- Budget
- Arbeitspakete
- Deliverables
- Dokumente-Links

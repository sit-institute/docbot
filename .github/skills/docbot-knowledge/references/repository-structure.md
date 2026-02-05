# Repository Structure

DocBot organizes local documents and index files with links to external sources:

```
docbot/
├── projects/                          # Project index files
│   ├── [project-id].md                # Project metadata with document links
│   └── [another-project].md
│
├── documents/                         # Local documents (all projects)
│   ├── [project-id]/                  # Documents for a specific project
│   │   ├── application/              # Grant application documents
│   │   │   ├── full-application.pdf
│   │   │   ├── budget.xlsx
│   │   │   └── attachments/
│   │   ├── reports/                  # Project reports
│   │   │   ├── interim-report-2024.pdf
│   │   │   └── annual-report-2024.docx
│   │   ├── publications/              # Papers and publications
│   │   │   ├── paper-2024-01.pdf
│   │   │   └── preprints/
│   │   ├── meetings/                  # Meeting protocols and notes
│   │   │   ├── 2024-01-15-kickoff.pdf
│   │   │   └── 2024-03-20-review.md
│   │   ├── deliverables/             # Project deliverables
│   │   │   ├── d1-requirements.pdf
│   │   │   └── d2-prototype.zip
│   │   ├── correspondence/            # Email attachments, important correspondence
│   │   │   ├── funders/
│   │   │   └── partners/
│   │   └── data/                      # Datasets, CSV, raw data
│   │       ├── survey-results.csv
│   │       └── measurements/
│   │
│   └── [another-project]/
│
├── templates/                         # Templates for new documents
│   ├── project-index-template.md
│   ├── interim-report-template.md
│   ├── annual-report-template.md
│   └── meeting-notes-template.md
│
├── reports/                           # Generated overview reports
│   ├── portfolio-overview.md
│   └── analytics/
│       └── project-similarities.md
│
├── knowledge/                         # Knowledge base
│   ├── glossary.md
│   ├── partners.md
│   └── funders.md
│
├── scripts/                           # Helper scripts (optional)
│   ├── extract-budget.py
│   └── similarity-analysis.py
│
└── .mcp/                              # MCP configuration
    └── config.json
```

## Key Points

- **BASE_DIR**: The `documents/` folder is the BASE_DIR for Local RAG and contains all local documents
- **External documents**: Documents stored in other systems (Confluence, SharePoint, GitHub, etc.) are only linked in the project index file
- **.rag/**: Automatically created by Local RAG and should be in .gitignore

## Document Sources

### Local
- File system folders
- Local databases

### Version Control
- **GitHub**: Repositories, Issues, Pull Requests, Wikis

### Collaboration Platforms
- **Confluence**: Wiki pages, documentation, meeting notes
- **SharePoint**: Document libraries, lists
- **Notion**: Pages, databases
- **Google Drive**: Docs, Sheets, Slides
- **OneDrive**: Office documents

### Project Management
- **Jira**: Tickets, Epics, Sprint documentation
- **Trello**: Boards, cards

### Communication
- **Slack**: Channel messages, shared files
- **Microsoft Teams**: Messages, shared documents
- **E-mail**: Archived correspondence

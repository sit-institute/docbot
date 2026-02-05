# Project Index Format

Each project should be indexed as a Markdown file in the `projects/` folder. The file contains metadata and links to distributed documents:

```markdown
# [Project Title]

## Basic Information
- **Project ID**: [unique-id]
- **Acronym**: [short-acronym]
- **Duration**: YYYY-MM-DD to YYYY-MM-DD
- **Status**: [In Preparation | Running | Completed | Cancelled]
- **Budget**: [amount] EUR
- **Funder**: [funder name]
- **Funding Program**: [program name]

## Project Team
- **PI**: [name]
- **Co-PIs**: [names]
- **Team Members**: [names]
- **Partners**: [organizations]

## Content
[Short description of the project in 2-3 sentences]

## Goals
1. [Main goal 1]
2. [Main goal 2]
3. [Main goal 3]

## Work Packages
- **WP1**: [Name] - [Status]
- **WP2**: [Name] - [Status]
- **WP3**: [Name] - [Status]

## Deliverables
- **D1**: [Name] - Due: YYYY-MM-DD - Status: [✓/○]
- **D2**: [Name] - Due: YYYY-MM-DD - Status: [✓/○]

## Milestones
- **M1**: [Name] - Date - Status
- **M2**: [Name] - Date - Status

## Keywords
[keyword1], [keyword2], [keyword3], [topic-area]

## Related Projects
- [project-id-1]: [relationship/overlap]
- [project-id-2]: [relationship/overlap]

## Documents
### Application
- [Full Application PDF](../documents/ki-2024/application/full-application.pdf) (local)
- [Budget Excel](../documents/ki-2024/application/budget.xlsx) (local)
- [Project Description](https://gitlab.example.com/ki-projekt/wiki/description) (GitLab)

### Reports
- [Interim Report 2024](https://confluence.example.com/projects/KI-2024/interim-report) (Confluence)
- [Meeting Notes](https://notion.so/ki-projekt/meetings) (Notion)
- [Annual Report 2024](../documents/ki-2024/reports/annual-report-2024.pdf) (local)

### Data & Analysis
- [Survey Results CSV](../documents/ki-2024/data/survey-results.csv) (local)
- [Measurement Data](../documents/ki-2024/data/measurements/) (local)

### Communication
- [Slack Channel](https://example.slack.com/archives/C123456) (Slack)
- [Jira Board](https://jira.example.com/projects/KI2024) (Jira)
- [Email Correspondence](../documents/ki-2024/correspondence/funders/) (local)

## Important Links
- Project website: [URL]
- Repository: [URL]
- Funder portal: [URL]
```

## YAML Frontmatter Example

```yaml
---
type: meeting-notes
date: 2024-01-15
project: ki-gesundheit-2024
participants: [Name1, Name2]
topics: [Budget, Milestone-1, Publication]
---
```

## Document References

- URLs: Complete and with access date
- External systems: Document authentication
- Local access: Relative paths from repository root
- Cloud documents: Note versioning

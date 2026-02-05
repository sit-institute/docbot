# DocBot - Agent-Based Research Project Management

## DocBot Knowledge

### For DocBot-specific knowledge
- repository structure, project index format, conventions
- Use `skill:docbot-knowledge`

### For seaching the documents in the repository
- Use `skill:local-rag-pipeline` (if the documents are indexed in ChromaDB)
- scripts are in `.github/skills/local-rag-pipeline/scripts`


## Markdown Formatting

- Never use horizontal lines (---)
- Use headings (#, ##, ###) for structure
- **Bold** only for really important points
- Emojis are not allowed
- Use lists (-, 1.) for enumerations
- Always add a blank line before unordered lists
- Filenames are kebab-case unless the project requires otherwise

## Tool Usage

Prioritize specialized tools over bash/terminal commands:

1. Use dedicated tools first (create_file, replace_string_in_file, edit_notebook_file)
2. Use bash/run_in_terminal only as last option
3. Prefer precise, context-aware tools over shell commands

Examples:
- Create files: create_file instead of `echo > file`
- Edit code: replace_string_in_file instead of `sed`
- Search: grep or semantic_search instead of `grep`
- Read files: read instead of `cat/head/tail`

# Query Expansion Use Case

**When to use:** Improve search recall by automatically expanding user queries before searching. This is handled automatically by the agent before every search.

## Overview

Query expansion generates multiple alternative search queries from the original user query, then searches with all expanded queries and merges the results. This improves recall by capturing documents that use different terminology.

## Workflow

```
User Query → [LLM: Expand Query] → Multiple Queries → Parallel Search → Merge Results → Reranking
```

## Agent Prompt Template

**Use exactly this format when expanding queries:**

```
Du bist ein Suchexperte für Dokumentensuche.
Generiere 4 alternative Suchanfragen für das Dokumentensystem.

Original-Query: {query}

Regeln:
1. Füge Synonyme und verwandte Fachbegriffe hinzu
2. Übersetze zwischen DE/EN wo sinnvoll
3. Variiere die Formulierung (Frage vs. Statement)
4. Gib NUR eine JSON-Liste zurück: ["query1", "query2", "query3", "query4"]

Beispiel:
- Input: "Zahlungsbedingungen"
- Output: ["Zahlungsbedingungen", "payment terms", "Zahlungsmodalitäten", "billing conditions"]
```

## Example Expansion

| Original Query | Expanded Queries |
|----------------|------------------|
| "Zahlungsbedingungen" | ["Zahlungsbedingungen", "payment terms", "Zahlungsmodalitäten", "billing conditions"] |
| "deadline application" | ["deadline application", "submission deadline", "application deadline", "截止日期"] |
| "eligibility criteria" | ["eligibility criteria", "admission requirements", "qualification criteria", "参加条件"] |

## Steps for Agent

1. Receive original query from user
2. Call LLM with the prompt template above
3. Parse JSON response to get 4 expanded queries
4. Search with EACH expanded query in parallel
5. Merge all results and deduplicate
6. Run reranking on merged results

## Important

- **Automatic**: Expansion happens before EVERY search
- **Fixed Template**: Use exactly the prompt above
- **4 Queries**: Always generate exactly 4 alternatives
- **No Flag**: Always enabled, no configuration needed

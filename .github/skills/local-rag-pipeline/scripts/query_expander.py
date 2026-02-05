#!/usr/bin/env python3
"""
Step 7: Query Expansion Module.

Hybrid query expansion using NLTK WordNet synonyms and domain-specific expansions.
Default: 5 expanded queries (1 original + 4 expanded).

Usage:
    from query_expander import QueryExpander
    expander = QueryExpander()
    expanded = expander.expand("Zahlungsbedingungen")
"""

import re
import json
from typing import List

try:
    import nltk
    from nltk.corpus import wordnet

    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

DOMAIN_SYNONYMS = {
    "zahlung": ["payment", "zahlung", "zahlen", "betrag", "billing", "begleichung"],
    "vertrag": ["contract", "vertrag", "vereinbarung", "agreement", "kontrakt"],
    "bedingung": ["condition", "bedingung", "kondition", "voraussetzung", "klausel"],
    "dokument": ["document", "dokument", "unterlage", "akte", "papier"],
    "rechnung": ["invoice", "rechnung", "facture", "abrechnung"],
    "datei": ["file", "datei", "dokument"],
    "suche": ["search", "suche", "suchen", "finden"],
    "information": ["information", "info", "daten", "angaben"],
    "recht": ["legal", "recht", "gesetzlich", "juristisch"],
    "pflicht": ["obligation", "pflicht", "verpflichtung"],
    "frist": ["deadline", "frist", "termin", "zeitrahmen"],
    "kosten": ["cost", "kosten", "gebuehr", "preis", "aufwand"],
    "leistung": ["service", "leistung", "service", "erbringung"],
    "agb": ["terms", "agb", "allgemeine bedingungen", "general terms"],
    "datenschutz": ["privacy", "datenschutz", "data protection", "dsgvo"],
    "haftung": ["liability", "haftung", "verantwortung"],
    "kuendigung": ["termination", "kuendigung", "beendigung", "cancellation"],
    "aenderungen": ["changes", "aenderungen", "aendern", "modifications"],
    "genehmigung": ["approval", "genehmigung", "freigabe", "authorization"],
    "anhaenge": ["attachments", "anhaenge", "anlagen", "appendices"],
}

STOPWORDS = {
    "der",
    "die",
    "das",
    "den",
    "dem",
    "des",
    "ein",
    "eine",
    "einer",
    "einem",
    "und",
    "oder",
    "aber",
    "auch",
    "als",
    "an",
    "auf",
    "aus",
    "bei",
    "durch",
    "für",
    "gegen",
    "in",
    "mit",
    "nach",
    "ohne",
    "um",
    "unter",
    "von",
    "vor",
    "zu",
    "zum",
    "zur",
    "über",
    "the",
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
    "what",
    "which",
}

EXPAND_PROMPT = """Generiere 4 alternative Suchanfragen für das folgende Dokumentensuchsystem.
Die Alternativen sollen:
1. Synonyme und verwandte Begriffe enthalten
2. Verschiedene Formulierungen der Originalfrage bieten
3. Fachbegriffe aus dem Kontext nutzen

Original: {query}

Antworte NUR mit einer JSON-Liste von 4 Strings, keine Erklärungen:"""


def _ensure_nltk_data():
    """Download required NLTK data if available."""
    if not NLTK_AVAILABLE:
        return False
    try:
        wordnet.synsets("test")
        return True
    except LookupError:
        try:
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-1.4", quiet=True)
            return True
        except Exception:
            return False


class QueryExpander:
    def __init__(self, num_expansions: int = 5, method: str = "hybrid"):
        self.num_expansions = num_expansions
        self.method = method
        self.nltk_ready = _ensure_nltk_data() if NLTK_AVAILABLE else False

    def expand(self, query: str) -> list[str]:
        if self.method == "synonyms":
            return self._expand_with_synonyms(query)
        elif self.method == "hybrid":
            return self._hybrid_expansion(query)
        else:
            return [query]

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        tokens = re.findall(r"\b[a-zäöüß]+\b", text, re.IGNORECASE)
        return [t for t in tokens if t not in STOPWORDS and len(t) > 2]

    def _get_synonyms_wordnet(self, word: str) -> list[str]:
        if not self.nltk_ready:
            return []
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonym = lemma.name().replace("_", " ").lower()
                if synonym != word and len(synonym) > 2:
                    synonyms.add(synonym)
        return list(synonyms)

    def _get_domain_synonyms(self, word: str) -> list[str]:
        word_lower = word.lower()
        for key, synonyms in DOMAIN_SYNONYMS.items():
            if key in word_lower or word_lower in key:
                return [s for s in synonyms if s != word]
        return []

    def _expand_with_synonyms(self, query: str) -> list[str]:
        tokens = self._tokenize(query)
        expanded = [query]

        for token in tokens:
            synonyms = []
            domain_syns = self._get_domain_synonyms(token)
            if domain_syns:
                synonyms.extend(domain_syns[:3])
            wordnet_syns = self._get_synonyms_wordnet(token)
            if wordnet_syns:
                synonyms.extend(wordnet_syns[:2])
            expanded.extend(synonyms)

        unique = list(dict.fromkeys(expanded))
        return unique[: self.num_expansions]

    def _hybrid_expansion(self, query: str) -> list[str]:
        queries = [query]
        tokens = self._tokenize(query)

        for token in tokens[:3]:
            synonyms = []
            domain_syns = self._get_domain_synonyms(token)
            if domain_syns:
                synonyms.extend(domain_syns[:2])
            wordnet_syns = self._get_synonyms_wordnet(token)
            if wordnet_syns:
                synonyms.extend(wordnet_syns[:2])
            if synonyms:
                queries.append(f"{query} {' '.join(synonyms[:3])}")

        for token in tokens[:2]:
            domain_syns = self._get_domain_synonyms(token)
            if domain_syns:
                alt_query = f"{token} {' '.join(domain_syns[:2])}"
                if alt_query not in queries:
                    queries.append(alt_query)

        if len(tokens) >= 2:
            reordered = f"{tokens[1]} {tokens[0]} {' '.join(tokens[2:])}"
            if reordered not in queries:
                queries.append(reordered)

        unique = list(dict.fromkeys(queries))
        return unique[: self.num_expansions]


def expand_query(query: str, num_expansions: int = 5) -> list[str]:
    expander = QueryExpander(num_expansions=num_expansions)
    return expander.expand(query)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python 7_query_expander.py <query>")
        sys.exit(1)

    query = sys.argv[1]
    expander = QueryExpander(num_expansions=5)
    expanded = expander.expand(query)

    print(f"Original: {query}")
    print(f"Expanded ({len(expanded)}):")
    for i, q in enumerate(expanded, 1):
        print(f"  {i}. {q}")

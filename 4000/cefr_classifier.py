# -*- coding: utf-8 -*-
"""
Clasificador CEFR para palabra o frase (CLI y librería)

- Usa cefrpy y spaCy cuando están disponibles.
- Si faltan dependencias, usa una heurística simple como respaldo.
- Diseñado para ejecutarse en tu env de conda llamado "Word".

Uso (ejemplos):
  python cefr_classifier.py --word "apple"
  python cefr_classifier.py --text "I have a red apple"
  python cefr_classifier.py --text "I have a red apple" --json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ----- Intento de importar dependencias reales -----
HAS_DEPS = True
try:
    from cefrpy import CEFRAnalyzer, CEFRSpaCyAnalyzer  # type: ignore
    import spacy  # type: ignore
except Exception:
    HAS_DEPS = False
    CEFRAnalyzer = None  # type: ignore
    CEFRSpaCyAnalyzer = None  # type: ignore
    spacy = None  # type: ignore

# ----- Mapeos de niveles -----
LEVEL_NUM_TO_LABEL: Dict[int, str] = {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}
LEVEL_LABEL_TO_NUM: Dict[str, int] = {v: k for k, v in LEVEL_NUM_TO_LABEL.items()}

# ----- Abreviaciones comunes para análisis con spaCy -----
ABBREVIATION_MAP: Dict[str, str] = {
    "'m": "am",
    "n't": "not",
    "'re": "are",
    "'s": "is",
    "'ve": "have",
    "'ll": "will",
    "'d": "would",
}

@dataclass
class TokenCEFR:
    text: str
    pos: Optional[str]
    level_num: Optional[int]

    @property
    def level_label(self) -> Optional[str]:
        if self.level_num is None:
            return None
        return LEVEL_NUM_TO_LABEL.get(self.level_num)


# ==================== Núcleo de Clasificación ====================

def _load_nlp():
    """Carga el pipeline de spaCy si está disponible."""
    if not HAS_DEPS:
        return None
    try:
        return spacy.load("en_core_web_sm")  # type: ignore
    except Exception:
        # Modelo no instalado
        return None


def classify_word(word: str) -> Tuple[str, Dict[str, object]]:
    """Clasifica una palabra en su nivel CEFR.

    Retorna (level_label, detalles_json_amigable)
    """
    word_clean = (word or "").strip()
    if not word_clean:
        return ("UNKNOWN", {"error": "empty input"})

    if HAS_DEPS:
        try:
            analyzer = CEFRAnalyzer()  # type: ignore
            lvl = analyzer.get_average_word_level_CEFR(word_clean)
            # cefrpy puede devolver None o número 1..6
            if isinstance(lvl, (int, float)):
                # redondear por si viene float
                lvl_n = int(round(lvl))
                label = LEVEL_NUM_TO_LABEL.get(lvl_n, "UNKNOWN")
                return (
                    label,
                    {
                        "input": word_clean,
                        "method": "cefrpy",
                        "level_num": lvl_n,
                        "level_label": label,
                    },
                )
        except Exception:
            pass

    # Respaldo heurístico
    label = _heuristic_word_level(word_clean)
    return (
        label,
        {
            "input": word_clean,
            "method": "heuristic",
            "level_label": label,
        },
    )


def classify_text(text: str) -> Tuple[str, Dict[str, object]]:
    """Clasifica un texto/frase: retorna el nivel global y detalle por tokens."""
    txt = (text or "").strip()
    if not txt:
        return ("UNKNOWN", {"error": "empty input"})

    tokens: List[TokenCEFR] = []

    if HAS_DEPS:
        nlp = _load_nlp()
        if nlp is not None:
            try:
                cefr_word_analyzer = CEFRAnalyzer()  # type: ignore
                analyzer = CEFRSpaCyAnalyzer(
                    cefr_word_analyzer, abbreviation_mapping=ABBREVIATION_MAP
                )  # type: ignore
                doc = nlp(txt)
                analized = analyzer.analize_doc(doc)  # returns token details aligned to doc

                for token, info in zip(doc, analized):
                    # Basado en ejemplos de uso de cefrpy: info = (text, pos, something, level_num, ...)
                    lvl_num = None
                    try:
                        if len(info) >= 4 and isinstance(info[3], (int, float)):
                            lvl_num = int(round(info[3]))
                    except Exception:
                        lvl_num = None
                    tokens.append(
                        TokenCEFR(text=token.text, pos=token.pos_, level_num=lvl_num)
                    )
            except Exception:
                # Si falla el camino "real", usa heurística
                tokens = _heuristic_tokenize_and_level(txt)
        else:
            tokens = _heuristic_tokenize_and_level(txt)
    else:
        tokens = _heuristic_tokenize_and_level(txt)

    # Determinar nivel global (estrategia simple: máximo nivel entre tokens encontrados)
    level_nums = [t.level_num for t in tokens if t.level_num is not None]
    if level_nums:
        global_num = max(level_nums)
        global_label = LEVEL_NUM_TO_LABEL.get(global_num, "UNKNOWN")
    else:
        # Si nadie tuvo nivel, aplicar heurística por longitud total
        global_label = _heuristic_text_level(txt)

    # Construir detalle
    details = {
        "input": txt,
        "global_level": global_label,
        "tokens": [
            {
                "text": t.text,
                "pos": t.pos,
                "level_num": t.level_num,
                "level_label": t.level_label,
            }
            for t in tokens
        ],
        "method": "cefrpy+spacy" if HAS_DEPS else "heuristic",
    }
    return global_label, details


# ==================== Heurísticas de respaldo ====================

def _heuristic_word_level(word: str) -> str:
    w = word.lower()
    a1 = {
        "the",
        "a",
        "an",
        "and",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "good",
        "bad",
        "big",
        "small",
        "new",
        "old",
        "hot",
        "cold",
        "time",
        "day",
        "year",
        "go",
        "come",
        "eat",
        "drink",
        "see",
        "look",
        "like",
        "want",
        "need",
        "home",
        "family",
        "friend",
        "water",
        "food",
        "work",
        "school",
    }
    a2 = {
        "about",
        "after",
        "again",
        "because",
        "between",
        "during",
        "different",
        "important",
        "often",
        "through",
        "young",
        "large",
        "most",
        "write",
        "world",
    }
    if w in a1:
        return "A1"
    if w in a2:
        return "A2"
    L = len(w)
    if L <= 4:
        return "A1"
    if L <= 6:
        return "A2"
    if L <= 8:
        return "B1"
    if L <= 10:
        return "B2"
    return "C1"


def _heuristic_text_level(text: str) -> str:
    words = [x for x in _simple_tokenize(text) if x.isalpha()]
    if not words:
        return "UNKNOWN"
    # nivel global = máximo de niveles heurísticos por palabra
    levels = [LEVEL_LABEL_TO_NUM.get(_heuristic_word_level(w), 1) for w in words]
    num = max(levels) if levels else 1
    return LEVEL_NUM_TO_LABEL.get(num, "A1")


def _simple_tokenize(text: str) -> List[str]:
    # Tokenización simple por espacios y signos comunes
    import re

    return [t for t in re.split(r"([\w']+|[^\w\s])", text) if t and not t.isspace()]


def _heuristic_tokenize_and_level(text: str) -> List[TokenCEFR]:
    tokens: List[TokenCEFR] = []
    for t in _simple_tokenize(text):
        if t.isalpha():
            lvl = LEVEL_LABEL_TO_NUM.get(_heuristic_word_level(t))
        else:
            lvl = None
        tokens.append(TokenCEFR(text=t, pos=None, level_num=lvl))
    return tokens


# ==================== CLI ====================

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Clasificador CEFR (palabra o texto)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--word", type=str, help="Clasificar una palabra")
    g.add_argument("--text", type=str, help="Clasificar una frase/texto")
    p.add_argument("--json", action="store_true", help="Salida en JSON")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)

    if args.word:
        label, details = classify_word(args.word)
    else:
        label, details = classify_text(args.text)

    if args.json:
        print(json.dumps(details, ensure_ascii=False, indent=2))
    else:
        kind = "Palabra" if args.word else "Texto"
        print(f"{kind} → Nivel CEFR: {label}")
        if not HAS_DEPS:
            print("(Usando heurística por falta de dependencias cefrpy/spaCy)")

    # Mensaje breve si faltan dependencias
    if not HAS_DEPS:
        print(
            "Nota: Instala 'cefrpy' y 'spacy' en tu entorno conda 'Word' y el modelo 'en_core_web_sm'."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

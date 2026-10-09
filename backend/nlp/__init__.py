"""Devanagari Natural Language Processing & 3-Tier Clinical Normalization package."""

from backend.nlp.devanagari import fold, fold_orthography, prepare, tokenize
from backend.nlp.lexicon import Concept, Lexicon, get_lexicon
from backend.nlp.normalize import Match, NormalizationResult, normalize
from backend.nlp.correct import correct

__all__ = [
    "fold",
    "fold_orthography",
    "prepare",
    "tokenize",
    "Concept",
    "Lexicon",
    "get_lexicon",
    "Match",
    "NormalizationResult",
    "normalize",
    "correct",
]

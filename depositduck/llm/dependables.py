"""
Callables to use with FastAPI's Dependency Injection system.
Expose LLM-related functionality eg. a tokeniser.

(c) 2024 Alberto Morón Hernández
"""

from functools import cache

from nltk.tokenize.destructive import NLTKWordTokenizer


@cache
def get_treebank_tokenizer() -> NLTKWordTokenizer:
    return NLTKWordTokenizer()

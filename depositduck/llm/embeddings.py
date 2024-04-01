"""
Utilities to generate embeddings for use in vector similarity queries.

(c) 2024 Alberto Morón Hernández
"""

import string

from gensim import corpora as gs_corpora
from nltk.data import load

from depositduck import BASE_DIR
from depositduck.llm import STOPWORDS
from depositduck.llm.dependables import get_treebank_tokenizer

TOKENIZER = get_treebank_tokenizer()


# inspired by NLTK's tokenizer - avoids having to download irrelevant models
# https://github.com/nltk/nltk/blob/3.8.1/nltk/tokenize/__init__.py
def tokenize(doc: str, remove_punctuation=True) -> list[str]:
    pickle_path = BASE_DIR / "data" / "punkt_tokenizer_english.pickle"
    sentence_tokenizer = load(pickle_path.as_uri())
    sentences = sentence_tokenizer.tokenize(doc.lower())

    if not remove_punctuation:
        return [token for sent in sentences for token in TOKENIZER.tokenize(sent)]

    return [
        token
        for sentence in sentences
        for token in TOKENIZER.tokenize(sentence)
        if token not in string.punctuation
    ]


def embed_documents(docs: list[str]) -> list[list[float]]:
    # tokenise and remove stopwords
    tokenized_docs = [
        [token for token in tokenize(doc) if token not in STOPWORDS] for doc in docs
    ]

    dictionary = gs_corpora.Dictionary(tokenized_docs)
    corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]
    return corpus

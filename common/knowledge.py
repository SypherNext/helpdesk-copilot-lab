"""Finds the knowledge base articles that best match a question.

A simple word-overlap score is enough for a dozen short articles and keeps the
lab free of an embedding model. The security lessons are about what happens
after an article is found, not about search quality.
"""
import pathlib
import re

from common import config

KNOWLEDGE_DIR = pathlib.Path(__file__).resolve().parent.parent / "knowledge"
WORD = re.compile(r"[a-z0-9]+")
# Words too common to tell articles apart. "order" is here because nearly
# every question and article mentions orders.
STOP_WORDS = {
    "a", "about", "an", "and", "any", "are", "be", "can", "do", "does", "for", "from", "get", "has",
    "have", "how", "i", "in", "is", "it", "me", "my", "of", "on", "or", "order", "orders", "please",
    "the", "this", "that", "to", "what", "when", "where", "will", "with", "you", "your",
}


def _words(text):
    return {word for word in WORD.findall(text.lower()) if word not in STOP_WORDS}


def load_articles(folder=KNOWLEDGE_DIR):
    articles = []
    for path in sorted(folder.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        articles.append({"name": path.stem, "text": text, "words": _words(text)})
    return articles


class KnowledgeBase:
    def __init__(self, articles=None):
        self.articles = articles if articles is not None else load_articles()

    def search(self, question, limit=config.SEARCH_RESULTS):
        question_words = _words(question)
        scored = [(len(question_words & article["words"]), article) for article in self.articles]
        matches = [pair for pair in scored if pair[0] > 0]
        matches.sort(key=lambda pair: pair[0], reverse=True)
        return [article for _, article in matches[:limit]]

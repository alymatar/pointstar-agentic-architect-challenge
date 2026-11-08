from config import load_config
from operator import itemgetter
import re

config = load_config()
document_path = config["document_path"]


def read_file(path):
    if not path:
        raise ValueError("document_path is missing")

    with open(path, "r", encoding="utf-8") as text:
        content = text.read()
        paragraphs = [p.strip() for p in re.split(r'\n{2,}', content) if p.strip()]

        return paragraphs


def search_document(query):
    if not query or not query.strip():
        return []

    paragraphs = read_file(document_path)
    query_words = []
    for word in re.findall(r"\b\w+\b", query.lower()):
        if len(word) >= 3:
            query_words.append(word)

    if not query_words:
        return []

    scored = []
    for paragraph in paragraphs:
        paragraph_words = set(re.findall(r"\b\w+\b", paragraph.lower()))
        score = sum(1 for word in query_words if word in paragraph_words)
        if score > 0:
            scored.append({"score": score, "paragraph": paragraph})

    top_three = sorted(scored, key=itemgetter("score"), reverse=True)[:3]
    return [item["paragraph"] for item in top_three]


if __name__ == "__main__":
    top_three = search_document("monitors electronics ")
    print(top_three)

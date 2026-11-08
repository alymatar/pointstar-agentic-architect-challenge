import os
import re

import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(override=True)

url = os.environ.get("LLM_BASE_URL")
key = os.environ.get("LLM_API_KEY")
model = os.environ.get("LLM_MODEL")


def get_page_text(page, address: str) -> str:
    page.goto(address, wait_until="domcontentloaded", timeout=30000)
    return page.locator("body").inner_text().strip()


def split_text(text: str, chunk_size: int = 4000) -> list[str]:
    text_chunks = []

    for i in range(0, len(text), chunk_size):
        text_chunks.append(text[i:i + chunk_size])

    return text_chunks


def llm_answer(message: str, instruction: str) -> str:
    if not key or not key.strip():
        raise ValueError("LLM_API_KEY is required")
    if not url or not url.strip():
        raise ValueError("LLM_BASE_URL is required")
    if not model or not model.strip():
        raise ValueError("LLM_MODEL is required")
    if not message or not message.strip():
        raise ValueError("Message must not be empty")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{instruction}\n\n{message}"},
        ],
        "temperature": 0.3,
    }

    response = requests.post(url, headers=headers, json=data, timeout=(5, 60))
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("The model returned an empty or invalid answer")

    return answer.strip()


def main():
    address = "https://en.wikipedia.org/wiki/Pythonidae"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            text = get_page_text(page, address)
        finally:
            browser.close()

    if not text:
        raise ValueError("No page text was found")

    text_chunks = split_text(text)
    summaries = []

    for chunk in text_chunks:
        summaries.append(
            llm_answer(chunk, "Summarize this part in a few short sentences.")
        )

    final_summary = llm_answer(
        "\n".join(summaries),
        "Write a concise summary in at most 5 bullet points and no more than 120 words.",
    )

    attempts = 0
    while len(final_summary.split()) > 120 and attempts < 3:
        final_summary = llm_answer(
            final_summary,
            "Shorten this summary to no more than 120 words. Keep complete sentences and no more than 5 bullet points.",
        )
        attempts += 1

    if len(final_summary.split()) > 120:
        sentences = re.split(r"(?<=[.!?])\s+", final_summary)
        short_summary = ""

        for sentence in sentences:
            if len((short_summary + " " + sentence).split()) > 120:
                break
            if short_summary:
                short_summary = short_summary + " " + sentence
            else:
                short_summary = sentence

        final_summary = short_summary
    print(final_summary)


if __name__ == "__main__":
    main()

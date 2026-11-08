# Agentic Architect Challenge: PointStar Developer Intern

My solution to the three-part assessment. Each part lives in its own folder.

| Part | Folder | What it is |
|------|--------|------------|
| 1 | `part1-architecture` | One-page architecture diagram of a customer email support agent |
| 2 | `part2-scraper-summarizer` | Python script that scrapes a web page and summarizes it with an LLM |
| 3 | `part3-support-bot` | Telegram Q&A bot with document search, a calculator tool and conversation memory |

## Setup (Parts 2 and 3)

1. Python 3.11+ and a virtual environment: `python -m venv .venv`
2. Install: `pip install requests python-dotenv playwright python-telegram-bot`
3. For Part 2 only: `playwright install chromium`
4. Copy `.env.example` to `.env` inside the part's folder and fill in the values.

The LLM calls use any OpenAI-compatible chat endpoint (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`).

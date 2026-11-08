# Part 3: NovaDesk support bot (Telegram)

A Telegram bot that answers customer questions from a sample FAQ document, can do basic arithmetic, and remembers the conversation.

## Files
| File | Purpose |
|------|---------|
| `bot.py` | Telegram handlers (`/start`, `/reset`, `/name`, normal messages). Only the allowed user in a private chat is served. |
| `llm.py` | Calls the LLM with two tools (`search_document`, `calculate`), runs the tool, then asks the model for the final answer. |
| `document_search.py` | Splits the document into paragraphs and returns the top 3 by keyword overlap. |
| `calculator.py` | Safe add / subtract / multiply / divide with input checks. |
| `conversation_store.py` | SQLite memory: last 20 messages per user, plus a saved name that /reset does not delete. |
| `config.py` | Loads and validates settings from `.env`. |
| `.env.example` | Template of the settings you need. |

## Run
```
pip install python-telegram-bot requests python-dotenv
copy .env.example .env     (then fill in the values)
python bot.py
```
Set `DOCUMENT_PATH` to the path of the text document the bot should search (paragraphs separated by a blank line). `TELEGRAM_ALLOWED_USER_ID` is your numeric Telegram ID.

## Commands
- `/start` greeting
- `/reset` clears the conversation history
- `/name Your Name` saves your name

## Failure handling
Timeouts, HTTP errors and bad input produce a short message to the user instead of a crash. The model may use at most one tool round per question.

# Part 2: Web page scraper and summarizer

`scraper.py` opens a web page with Playwright and summarizes it with an LLM, using a map-reduce approach.

## How it works
1. Playwright loads the page and reads the body text.
2. The text is split into chunks of 4000 characters (`split_text`).
3. Each chunk is summarized separately (map step).
4. The chunk summaries are joined and summarized again into at most 5 bullet points and 120 words (reduce step).
5. Length guardrail: if the result is over 120 words, the model is asked to shorten it (up to 3 tries). If it is still too long, it is cut at the last full sentence that fits.

## Run
```
pip install requests python-dotenv playwright
playwright install chromium
copy .env.example .env     (then fill in the values)
python scraper.py
```
The page URL is set in `main()`. Default: the Wikipedia page for Pythonidae.

## Known limits
- If the first sentence alone is over 120 words, the fallback cut returns nothing.
- Chunks are cut at fixed positions, so a sentence can be split between two chunks.

import json
import os

import requests
from dotenv import load_dotenv

from calculator import calculate
from conversation_store import add_exchange, clear_history, get_history, get_name
from document_search import search_document

load_dotenv(override=True)

url = os.environ.get("LLM_BASE_URL")
key = os.environ.get("LLM_API_KEY")
model = os.environ.get("LLM_MODEL")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_document",
            "description": "Search the sample document when the user's question needs information from it. Returns relevant passages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's document-related question or search terms.",
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate with two numbers when the user asks for arithmetic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "number1": {"type": "number"},
                    "number2": {"type": "number"},
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                    },
                },
                "required": ["number1", "number2", "operation"],
                "additionalProperties": False,
            },
        },
    },
]


def run_tool(tool_name, arguments):
    if tool_name == "search_document":
        query = arguments.get("query")
        if not isinstance(query, str):
            raise ValueError("search_document query must be text")
        return search_document(query)

    if tool_name == "calculate":
        return calculate(
            arguments.get("number1"),
            arguments.get("number2"),
            arguments.get("operation"),
        )

    raise ValueError("The model requested an unknown tool")


def ask_model(messages, headers):
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "tools": TOOLS,
        "tool_choice": "auto",
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=(5, 60),
    )
    response.raise_for_status()
    result_json = response.json()
    return result_json["choices"][0]["message"]


def llm_answer(message: str, user_id: int) -> str:
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
    history = get_history(user_id)
    saved_name = get_name(user_id)
    name_instruction = ""
    if saved_name:
        name_instruction = (
            f" The user's saved name is {saved_name!r}. Use this name naturally "
            "when appropriate, and do not replace it based on conversation guesses."
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful Q&A assistant. Use search_document only when "
                "the question needs the configured document. Use calculate for "
                "arithmetic and explain the result clearly. If document search "
                "returns no useful passages, say you could not find the answer "
                "in the document instead of making it up." + name_instruction
            ),
        },
    ] + history + [{"role": "user", "content": message}]

    assistant_message = ask_model(messages, headers)
    tool_calls = assistant_message.get("tool_calls") or []

    if tool_calls:
        # Return tool results to the model so it can write the user-facing answer.
        messages.append(assistant_message)
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name")
            try:
                arguments = json.loads(function.get("arguments", "{}"))
            except (TypeError, json.JSONDecodeError) as error:
                raise ValueError("The model returned invalid tool arguments") from error
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be an object")

            tool_result = run_tool(tool_name, arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(tool_result, ensure_ascii=False),
                }
            )

        assistant_message = ask_model(messages, headers)
        if assistant_message.get("tool_calls"):
            raise ValueError("The model requested more than one tool round")

    answer = assistant_message.get("content")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("The model returned an empty or invalid answer")

    add_exchange(user_id, message, answer)
    return answer


def clear_memory(user_id: int):
    clear_history(user_id)

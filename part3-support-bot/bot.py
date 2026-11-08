from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from config import load_config
from llm import llm_answer, clear_memory
from conversation_store import save_name
import asyncio
import requests


def is_authorized(update: Update, allowed_user_id: int) -> bool:
    user = update.effective_user
    chat = update.effective_chat

    if user is None or chat is None:
        return False

    return user.id == allowed_user_id and chat.type == "private"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed_user_id = context.bot_data["allowed_user_id"]
    if not is_authorized(update, allowed_user_id):
        return
    message = update.message
    if message is None:
        return
    await message.reply_text("Hi there")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed_user_id = context.bot_data["allowed_user_id"]
    if not is_authorized(update, allowed_user_id):
        return
    message = update.message
    if message is None:
        return
    await message.reply_text(message.text)


async def llm_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed_user = context.bot_data["allowed_user_id"]
    if not is_authorized(update, allowed_user):
        return
    message = update.message
    if not message:
        return
    try:
        answer = await asyncio.to_thread(
            llm_answer,
            message.text,
            update.effective_user.id,
        )
    except requests.Timeout:
        await message.reply_text("The model is taking longer than expected")
        return
    except requests.HTTPError:
        await message.reply_text("The model service could not complete the request.")
        return
    except requests.RequestException:
        await message.reply_text("I could not connect to the model service.")
        return
    except (ValueError, KeyError, TypeError, ZeroDivisionError):
        await message.reply_text("I could not process that request. Please try again.")
        return

    await message.reply_text(answer)


async def reset_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed_user = context.bot_data["allowed_user_id"]
    if not is_authorized(update, allowed_user):
        return
    message = update.message
    if message is None:
        return

    clear_memory(update.effective_user.id)

    await message.reply_text("Conversation reset.")


async def set_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed_user = context.bot_data["allowed_user_id"]
    if not is_authorized(update, allowed_user):
        return

    message = update.message
    if message is None:
        return
    if not context.args:
        await message.reply_text("Set your saved name with /name Your Name")
        return

    try:
        save_name(update.effective_user.id, " ".join(context.args))
    except ValueError as error:
        await message.reply_text(str(error))
        return

    await message.reply_text("I\u2019ll remember that name.")


def main():
    config = load_config()
    application = Application.builder().token(config["bot_token"]).build()
    application.bot_data["allowed_user_id"] = config["allowed_user_id"]
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, llm_messages))
    application.add_handler(CommandHandler("reset", reset_conversation))
    application.add_handler(CommandHandler("name", set_user_name))
    application.run_polling(bootstrap_retries=3)


if __name__ == "__main__":
    main()

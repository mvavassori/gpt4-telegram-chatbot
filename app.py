import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

# Define a dictionary to store conversation context
context_messages = []

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    # Only respond if the chat ID matches your own
    if chat_id == CHAT_ID:
        context_messages.append({"role": "user", "content": user_message})

        # Send the conversation context to the OpenAI Chat API
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=context_messages
        )

        bot_response = response.choices[0].message["content"]

        # Store the bot's response in the conversation context
        context_messages.append({"role": "assistant", "content": bot_response})

        # Send the AI response to the user
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=bot_response
        )


async def clear_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear the conversation context
    context_messages.clear()

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Conversation context cleared."
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)

    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)

    clear_context_handler = CommandHandler("clear", clear_context)

    application.add_handler(start_handler)
    application.add_handler(chat_handler)
    application.add_handler(clear_context_handler)

    application.run_polling()

from typing import Dict

import telegram
from fastapi import BackgroundTasks
from pymongo import MongoClient

from configs.config import mongo_config, telegram_config
from rest_api.schemas.items import (CustomerChatItem, MessageItem, QueryItem,
                                    Role, WebhookItem)
from rest_api.services.qa_service import answer_question
from utils.logger import Logger

logger = Logger.get_logger()

TELEGRAM_TOKEN = telegram_config["bot_token"]

bot = telegram.Bot(token=telegram_config["bot_token"])
mongo_client = MongoClient(host=mongo_config.URI)
customer_db = mongo_client[mongo_config.DATABASE_NAME]
telegram_chat_collection = customer_db["telegram_chat"]


async def set_webhook(webhook: WebhookItem):
    URL = webhook.webhook

    url = "{URL}/{HOOK}".format(URL=URL, HOOK=TELEGRAM_TOKEN)
    logger.info(url)
    is_set_webhook = await bot.setWebhook(url)

    return is_set_webhook


async def respond(request: Dict, background_tasks: BackgroundTasks):
    is_success = False
    update = telegram.Update.de_json(request, bot)
    logger.info(update)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    user_id = update.message.from_user.id
    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode("utf-8").decode()

    try:
        question = QueryItem(question=text)
        # AI service to generate response
        response = await answer_question(query=question)
        ai_answer = response["answer"]
        logger.info(f"AI: {ai_answer}")
        # send message to user
        message = await bot.sendMessage(
            chat_id=chat_id, text=ai_answer, reply_to_message_id=msg_id
        )

        if message:
            is_success = True

        user_message = MessageItem(role=Role.USER, text=text)
        ai_message = MessageItem(role=Role.AI, text=ai_answer)

        # Save question from user and answer from AI (background tasks) with chat id
        chat = telegram_chat_collection.find_one({"id": str(chat_id)})
        # logger.info(chat)
        if chat:
            message_items = chat["messages"]
            message_items.append(user_message.model_dump())
            message_items.append(ai_message.model_dump())

            # telegram_chat_collection.update_one(filter={"id": chat.chat_id})
            background_tasks.add_task(
                func=telegram_chat_collection.update_one,
                filter={"_id": chat["_id"]},
                update={"$set": {"messages": message_items}},
            )

        else:
            customer_chat = CustomerChatItem(
                messages=[user_message, ai_message],
                userId=str(user_id),
                id=str(chat_id),
            )
            # inserted_chat = telegram_chat_collection.insert_one(document=customer_chat)
            background_tasks.add_task(
                telegram_chat_collection.insert_one, document=customer_chat.model_dump()
            )

    except Exception as e:
        # send error message to user
        logger.warning(e)

    return is_success

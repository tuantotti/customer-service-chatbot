from fastapi import APIRouter, BackgroundTasks, Request, Response

from configs.config import telegram_config
from rest_api.schemas.items import WebhookItem
from rest_api.services import telegram_service

router = APIRouter(tags=["Telegram Webhook"])
TELEGRAM_TOKEN = telegram_config["bot_token"]


@router.post("/setwebhook")
async def set_webhook(webhook: WebhookItem):
    is_set_webhook = await telegram_service.set_webhook(webhook)

    if is_set_webhook:
        return "webhook setup successfully"
    else:
        return "webhook setup failed"


@router.post("/{}".format(TELEGRAM_TOKEN))
async def response(request: Request, background_tasks: BackgroundTasks):
    json_request = await request.json()
    is_success = await telegram_service.respond(
        json_request, background_tasks=background_tasks
    )
    if is_success:
        response = Response(
            content="Send telegram message successfully", status_code=200
        )
    else:
        response = Response(content="Send telegram message fail", status_code=500)
    return response

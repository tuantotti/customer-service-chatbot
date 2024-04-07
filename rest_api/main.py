import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rest_api.routers import telegram_router
import nest_asyncio
from pyngrok import ngrok
# from rest_api.routers import qa_router

app = FastAPI(
    title="Customer Service Chatbot",
    description="API for customer service chatbot application",
)
# app.include_router(qa_router.router)
app.include_router(telegram_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get("/")
async def root():
    try:
        message = "Hello Customer Service Chatbot!"
    except Exception as e:
        message = f"Error: {e}"
    return {"message": f"{message}"}


if __name__ == "__main__":
    port = 8001
    ngrok_tunnel = ngrok.connect(port)
    nest_asyncio.apply()
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

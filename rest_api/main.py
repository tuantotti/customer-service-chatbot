import uvicorn
from fastapi import FastAPI

from rest_api.routers import telegram_router

# from rest_api.routers import qa_router

app = FastAPI(
    title="Customer Service Chatbot",
    description="API for customer service chatbot application",
)
# app.include_router(qa_router.router)
app.include_router(telegram_router.router)


@app.get("/")
async def root():
    try:
        message = "Hello Customer Service Chatbot!"
    except Exception as e:
        message = f"Error: {e}"
    return {"message": f"{message}"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)

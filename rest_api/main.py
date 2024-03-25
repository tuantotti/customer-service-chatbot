import uvicorn
from fastapi import FastAPI

from rest_api.routers import qa_router

app = FastAPI(
    title="Customer Service Chatbot",
    description="API for customer service chatbot application",
)
app.include_router(qa_router.router)


@app.get("/")
async def root():
    try:
        message = "Hello Customer Service Chatbot!"
    except Exception as e:
        message = f"Error: {e}"
    return {"message": f"{message}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

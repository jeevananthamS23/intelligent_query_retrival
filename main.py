import uvicorn
from fastapi import FastAPI
from api.endpoints import router
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Insurance Policy Q&A API")

# Health check root route
@app.get("/")
def root():
    return {"message": "Server is live 🚀"}

# Include your custom API routes
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

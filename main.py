import os
import uvicorn
from fastapi import FastAPI
from api.endpoints import router

app = FastAPI(title="Insurance Policy Q&A API")

@app.get("/")
def root():
    return {"message": "Server is live 🚀"}

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Render's assigned port
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

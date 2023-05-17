import scrapers
from fastapi import FastAPI
app = FastAPI()

@app.get("/{username}")
async def root(username: str):
    return {"Hello ", username}

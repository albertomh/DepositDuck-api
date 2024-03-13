"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"name": "DepositDuck"}

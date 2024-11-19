from fastapi import FastAPI
from transaction import router as transaction_router

app = FastAPI()

# Gắn router từ transaction.py
app.include_router(transaction_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the API!"}

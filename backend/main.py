from fastapi import FastAPI

app = FastAPI(title="Scan & Go API")

@app.get("/")
async def root():
    return {"message": "Welcome to Scan & Go API"}

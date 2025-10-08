from fastapi import FastAPI

app = FastAPI()

@app.get('/presign')
async def presign():
    return {"ok": true, "url": "demo"}

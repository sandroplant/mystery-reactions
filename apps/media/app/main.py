from fastapi import FastAPI

app = FastAPI()

@app.get('/presign')
def read_presign():
    return {"ok": true, "url": "demo"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from challenges.the_eleventh_day.routes import router as eleventh_day_router

app = FastAPI(title="CTF Challenges", version="2.0")

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(eleventh_day_router, prefix="/api/eleventh", tags=["Eleventh Day"])

@app.get("/health")
async def health():
    return {"status": "ok"}

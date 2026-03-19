from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

readings = []
rivers = []

class ReadingCreate(BaseModel):
    river_id: int = 1
    tds_ppm: Optional[float] = None
    water_temp_c: Optional[float] = None
    do_estimate: Optional[str] = None
    water_quality_score: Optional[float] = None
    ai_summary: Optional[str] = None

@app.post("/rivers")
def create_river(name: str, latitude: float = None, longitude: float = None):
    river = {"id": len(rivers) + 1, "name": name, "latitude": latitude, "longitude": longitude}
    rivers.append(river)
    return river

@app.get("/rivers")
def list_rivers():
    return rivers

@app.post("/readings")
def create_reading(body: ReadingCreate):
    reading = body.dict()
    readings.append(reading)
    return {"status": "ok"}

@app.get("/rivers/{river_id}/readings")
def get_readings(river_id: int):
    return [r for r in readings if r.get("river_id") == river_id]

@app.get("/rivers/{river_id}/latest")
def get_latest(river_id: int):
    match = [r for r in readings if r.get("river_id") == river_id]
    return match[-1] if match else {}

app.mount("/", StaticFiles(directory=".", html=True), name="static")

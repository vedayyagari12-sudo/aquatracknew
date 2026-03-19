from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

readings = []
rivers = []

@app.post("/rivers")
def create_river(name: str, latitude: float = None, longitude: float = None):
    river = {"id": len(rivers) + 1, "name": name, "latitude": latitude, "longitude": longitude}
    rivers.append(river)
    return river

@app.get("/rivers")
def list_rivers():
    return rivers

@app.post("/readings")
def create_reading(data: dict):
    readings.append(data)
    return {"status": "ok"}

@app.get("/rivers/{river_id}/readings")
def get_readings(river_id: int):
    return [r for r in readings if r.get("river_id") == river_id]

@app.get("/rivers/{river_id}/latest")
def get_latest(river_id: int):
    match = [r for r in readings if r.get("river_id") == river_id]
    return match[-1] if match else {}
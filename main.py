import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)

class RiverCreate(BaseModel):
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ReadingCreate(BaseModel):
    river_id: int = 1
    tds_ppm: Optional[float] = None
    water_temp_c: Optional[float] = None
    do_estimate: Optional[str] = None
    water_quality_score: Optional[float] = None
    ai_summary: Optional[str] = None

@app.post("/rivers", status_code=201)
def create_river(body: RiverCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO rivers (name, latitude, longitude) VALUES (%s, %s, %s) RETURNING *",
                (body.name, body.latitude, body.longitude))
    river = dict(cur.fetchone())
    conn.commit()
    conn.close()
    return river

@app.get("/rivers")
def list_rivers():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM rivers ORDER BY name")
    rivers = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rivers

@app.post("/readings", status_code=201)
def create_reading(body: ReadingCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO readings (river_id, tds_ppm, water_temp_c, do_estimate, water_quality_score, ai_summary)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING *
    """, (body.river_id, body.tds_ppm, body.water_temp_c, body.do_estimate, body.water_quality_score, body.ai_summary))
    reading = dict(cur.fetchone())
    conn.commit()
    conn.close()
    return reading

@app.get("/rivers/{river_id}/readings")
def get_readings(river_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM readings WHERE river_id=%s ORDER BY recorded_at DESC LIMIT 100", (river_id,))
    readings = [dict(r) for r in cur.fetchall()]
    conn.close()
    return readings

@app.get("/rivers/{river_id}/latest")
def get_latest(river_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM readings WHERE river_id=%s ORDER BY recorded_at DESC LIMIT 1", (river_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "No readings yet")
    return dict(row)

app.mount("/", StaticFiles(directory=".", html=True), name="static")



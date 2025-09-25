from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# load data
BASE = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE, "telemetry.jsonl")
# (Better to read manually JSON lines rather than rely on pandas read_json lines=True for reliability.)
# Example:
import json
rows = []
with open(data_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
DATA = pd.DataFrame(rows)

class TelemetryRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/")
async def check_latency(req: TelemetryRequest):
    result = {}
    for region in req.regions:
        df = DATA[DATA["region"] == region]
        if df.empty:
            continue
        avg_latency = df["latency_ms"].mean()
        p95_latency = np.percentile(df["latency_ms"], 95)
        avg_uptime = df["uptime_pct"].mean()
        breaches = (df["latency_ms"] > req.threshold_ms).sum()
        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 3),
            "breaches": int(breaches),
        }
    return result

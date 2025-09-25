import json
import os
import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Define the path to the telemetry data file
BASE = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE, "telemetry.jsonl")

# Load telemetry data into a DataFrame
rows = []
with open(data_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        
        # obj = json.loads(line)
        # rows.append(line)
        
        # obj = json.loads(line)
        # rows.append(obj)
        # print(line)
        # print(i)
        # if "latency" in line:
        print(line,i)

# rows.append([["lat", 5],["lat",7]])
# print(rows)
if rows:
    DATA = pd.DataFrame(rows)
else:
    DATA = pd.DataFrame()
print(DATA)
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
            "breaches": int(breaches)
        }
    print(result)
    return result

# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester
#
# Term Project Dashboard main python app
# Team C
# ==================================================

from flask import Flask, render_template, jsonify
import requests
import webbrowser
import threading
from dotenv import load_dotenv
import os
import time
from google import genai

# Initialize global variables
INSIGHT_REFRESH_INTERVAL = 300 # 5 minute
ENABLE_AI = True
USE_MOCK_DATA = False

load_dotenv()
FIREBASE_URL = os.getenv("FIREBASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"
client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)
INSIGHT_CACHE = ""
LAST_INSIGHT_TIME = 0

@app.route("/")
def index():
    return render_template("index.html") #./templates/index.html

# get capacity and return status
def get_bin_status(capacity):
    if capacity >= 90:
        return "Critical: bin is almost full"
    elif capacity >= 70:
        return "Warning: bin is getting full"
    else:
        return "Normal: enough space remains"

# Call Gemini API
def call_llm(data):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")
    
    prompt = f"""
Generate concise operational insight for a smart recycling dashboard.

Rules:
- 3 sentence only.
- Maximum 50 words.
- Focus on the most important issue.
- If no issue exists, state that the system is operating normally.
- Waste Types is number of waste. (Not a portion)

Sensor Data:
{data}
"""

    # Send request
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "max_output_tokens": 30
        }
    )

    return response.text.strip()

# Function that calls 'call_llm'
# Prevent excessive API requests
def get_insight(data):
    global INSIGHT_CACHE
    global LAST_INSIGHT_TIME

    if not ENABLE_AI:
        return "AI insight disabled in dev mode."

    # Compare current time and last request time
    now = time.time()
    if now - LAST_INSIGHT_TIME >= INSIGHT_REFRESH_INTERVAL:
        try:
            INSIGHT_CACHE = call_llm(data)
        except Exception as e:
            INSIGHT_CACHE = 'AI insight is currently unavailable'

        finally:
            LAST_INSIGHT_TIME = now

    return INSIGHT_CACHE

# use history data to generate recent detection count
def generate_recent_counts(records):

    if len(records) < 2:
        return {}

    # By subtracting adjacent records, we can estimate
    # the number of detections during each interval.
    recent_counts = {}
    for i in range(1, len(records)):
        prev_count = records[i - 1]["total_count"]
        curr_count = records[i]["total_count"]
        label = records[i]["timestamp"][11:16]
        recent_counts[label] = max(0, curr_count - prev_count)

    return recent_counts

# Main API that JS calls to get data
@app.route("/api/status")
def get_status():
    if not FIREBASE_URL:
        return jsonify({
            "success": False,
            "error": "FIREBASE_URL is not set"
        }), 500
    
    try:
        # get data. use test data if needed
        if USE_MOCK_DATA:
            records = get_mock_data()
        else:
            response = requests.get(FIREBASE_URL, 
                                    params={
                                        "orderBy": '"$key"',
                                        "limitToLast": 10
                                    },
                                    timeout=5)
            response.raise_for_status()
            records_dict = response.json() or {}
            records = list(records_dict.values())

            print(f"[Firebase] Read success: {len(records)} records")

        if not records:
            raise ValueError("No records found")

        # sort by time and get most recent one
        records.sort(key=lambda r: r["timestamp"])
        current = records[-1]

        # Build response payload
        data = {
            "temperature": current["temperature"],
            "humidity": current["humidity"],
            "capacity": current["capacity"],
            "status": get_bin_status(current["capacity"]),
            "total_count": current["total_count"],
            "waste_types": current["waste_types"],
            "recent_counts": generate_recent_counts(records),
            "insight": get_insight(records)
        }

        return jsonify({
            "success": True,
            "data": data
        })

    except Exception as e:
        print(f"[Firebase] Read failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Reset time to generate insight
@app.route("/api/generate-insight", methods=["POST"])
def generate_insight():
    global LAST_INSIGHT_TIME
    LAST_INSIGHT_TIME = 0

    return jsonify({"success": True})

# open default browser
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

# Run server
if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=True
    )

# Mock data for development and testing
def get_mock_data():
    return [
        {
            "timestamp": "2026-06-13T18:00:00",
            "temperature": 22.8,
            "humidity": 57,
            "capacity": 34,
            "total_count": 72,
            "waste_types": {
                "Plastic": 18,
                "Can": 11,
                "Paper": 9,
                "Glass": 4
            }
        },

        {
            "timestamp": "2026-06-13T18:30:00",
            "temperature": 23.6,
            "humidity": 59,
            "capacity": 51,
            "total_count": 90,
            "waste_types": {
                "Plastic": 37,
                "Can": 20,
                "Paper": 15,
                "Glass": 8
            }
        },

        {
            "timestamp": "2026-06-13T19:00:00",
            "temperature": 24.5,
            "humidity": 61,
            "capacity": 72,
            "total_count": 128,
            "waste_types": {
                "Plastic": 56,
                "Can": 31,
                "Paper": 22,
                "Glass": 14
            }
        },

        {
            "timestamp": "2026-06-13T19:30:00",
            "temperature": 25.1,
            "humidity": 63,
            "capacity": 79,
            "total_count": 145,
            "waste_types": {
                "Plastic": 66,
                "Can": 35,
                "Paper": 27,
                "Glass": 17
            }
        },

        {
            "timestamp": "2026-06-13T20:00:00",
            "temperature": 25.7,
            "humidity": 65,
            "capacity": 87,
            "total_count": 163,
            "waste_types": {
                "Plastic": 78,
                "Can": 39,
                "Paper": 30,
                "Glass": 16
            }
        },

        {
            "timestamp": "2026-06-13T20:30:00",
            "temperature": 26.1,
            "humidity": 66,
            "capacity": 92,
            "total_count": 182,
            "waste_types": {
                "Plastic": 90,
                "Can": 43,
                "Paper": 32,
                "Glass": 17
            }
        }
    ]
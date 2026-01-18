import json
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATEGORIES_PATH = Path(__file__).parent / "categories.json"

def load_categories() -> list[str]:
    return json.loads(CATEGORIES_PATH.read_text(encoding="utf-8"))

@app.get("/categories")
def get_categories(q: str = Query(default="", max_length=50), limit: int = 12):
    q = q.strip().lower()
    cats = load_categories()

    if q:
        cats = [c for c in cats if q in c.lower()]

    return {"items": cats[:limit]}
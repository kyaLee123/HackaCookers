import json
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow your Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CATEGORIES_PATH = Path(__file__).parent / "categories.json"

def load_categories() -> list[str]:
    return json.loads(CATEGORIES_PATH.read_text(encoding="utf-8"))

@app.get("/categories")
def get_categories(q: str = Query(default="", max_length=50), limit: int = 12):
    """
    Example:
      /categories?q=da -> ["dance", "dating", ...]
    """
    cats = load_categories()
    q_lower = q.strip().lower()

    if q_lower:
        filtered = [c for c in cats if q_lower in c.lower()]
    else:
        filtered = cats

    return {"items": filtered[:limit]}
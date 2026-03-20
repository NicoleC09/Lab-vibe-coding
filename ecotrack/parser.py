"""
parser.py — Extracts food and transport activities from natural language text.
Supports Spanish and English keywords.
"""

import re

FOOD_KEYWORDS: dict[str, str] = {
    "carne": "beef",
    "res": "beef",
    "hamburguesa": "beef",
    "burger": "beef",
    "bistec": "beef",
    "pollo": "chicken",
    "chicken": "chicken",
    "pescado": "fish",
    "salmón": "fish",
    "salmon": "fish",
    "fish": "fish",
    "cerdo": "pork",
    "tocino": "pork",
    "bacon": "pork",
    "pork": "pork",
    "vegetariano": "vegetables",
    "vegetariana": "vegetables",
    "verduras": "vegetables",
    "vegetables": "vegetables",
    "ensalada": "salad",
    "salad": "salad",
    "vegano": "vegan",
    "vegana": "vegan",
    "vegan": "vegan",
    "leche": "dairy",
    "queso": "dairy",
    "yogur": "dairy",
    "dairy": "dairy",
    "huevo": "eggs",
    "huevos": "eggs",
    "eggs": "eggs",
}

TRANSPORT_KEYWORDS: dict[str, str] = {
    "bus": "bus",
    "autobús": "bus",
    "autobus": "bus",
    "colectivo": "bus",
    "metro": "metro",
    "subte": "metro",
    "subway": "metro",
    "carro": "car",
    "coche": "car",
    "auto": "car",
    "car": "car",
    "taxi": "car",
    "avión": "plane",
    "avion": "plane",
    "vuelo": "plane",
    "plane": "plane",
    "flight": "plane",
    "moto": "motorcycle",
    "motocicleta": "motorcycle",
    "motorcycle": "motorcycle",
    "bici": "bike",
    "bicicleta": "bike",
    "bike": "bike",
    "tren": "train",
    "train": "train",
    "caminé": "walking",
    "caminando": "walking",
    "caminar": "walking",
    "walked": "walking",
    "walking": "walking",
    "anduve": "walking",
}

_DISTANCE_RE = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:km|kilómetros|kilometros|kms|kilómetro|kilometro)",
    re.IGNORECASE,
)

DEFAULT_DISTANCE_KM = 10.0


def _find_distances(text: str) -> list[tuple[int, float]]:
    """Returns list of (char_position, distance_km) for all distances found."""
    results = []
    for match in _DISTANCE_RE.finditer(text):
        value = float(match.group(1).replace(",", "."))
        results.append((match.start(), value))
    return results


def _nearest_distance(pos: int, distances: list[tuple[int, float]]) -> float:
    """Returns the distance value closest (by char position) to pos."""
    return min(distances, key=lambda d: abs(d[0] - pos))[1]


def parse_activities(text: str) -> list[dict]:
    """
    Parse natural language text and return a list of detected activities.

    Each activity is a dict with:
      - category: "food" | "transport"
      - type: canonical type string (e.g. "beef", "bus")
      - keyword: the matched keyword in the original text
      - distance_km: (transport only) distance in km
    """
    text_lower = text.lower()
    distances = _find_distances(text_lower)
    activities: list[dict] = []
    seen_food_types: set[str] = set()
    seen_transport_types: set[str] = set()

    # Food detection — one entry per canonical food type
    for keyword, food_type in FOOD_KEYWORDS.items():
        if food_type in seen_food_types:
            continue
        pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
        if re.search(pattern, text_lower):
            activities.append({"category": "food", "type": food_type, "keyword": keyword})
            seen_food_types.add(food_type)

    # Transport detection — one entry per canonical type per occurrence
    for keyword, transport_type in TRANSPORT_KEYWORDS.items():
        pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
        match = re.search(pattern, text_lower)
        if match:
            if transport_type in seen_transport_types:
                continue
            distance = (
                _nearest_distance(match.start(), distances)
                if distances
                else DEFAULT_DISTANCE_KM
            )
            activities.append(
                {
                    "category": "transport",
                    "type": transport_type,
                    "keyword": keyword,
                    "distance_km": distance,
                }
            )
            seen_transport_types.add(transport_type)

    return activities

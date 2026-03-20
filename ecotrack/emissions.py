"""
emissions.py — CO2 emission factors and estimation logic.

Food factors: kg CO2e per average meal/serving.
Transport factors: kg CO2e per km.

Sources: Our World in Data, IPCC, EEA average values.
"""

# kg CO2e per meal/serving
FOOD_FACTORS: dict[str, float] = {
    "beef": 6.61,
    "pork": 2.15,
    "chicken": 1.72,
    "fish": 1.38,
    "eggs": 0.43,
    "dairy": 0.94,
    "salad": 0.20,
    "vegetables": 0.37,
    "vegan": 0.16,
}

# kg CO2e per km
TRANSPORT_FACTORS: dict[str, float] = {
    "car": 0.210,
    "motorcycle": 0.113,
    "plane": 0.255,
    "bus": 0.089,
    "train": 0.041,
    "metro": 0.028,
    "bike": 0.0,
    "walking": 0.0,
}

# Human-readable labels
FOOD_LABELS: dict[str, str] = {
    "beef": "Carne de res",
    "pork": "Cerdo",
    "chicken": "Pollo",
    "fish": "Pescado",
    "eggs": "Huevos",
    "dairy": "Lácteos",
    "salad": "Ensalada",
    "vegetables": "Verduras",
    "vegan": "Comida vegana",
}

TRANSPORT_LABELS: dict[str, str] = {
    "car": "Auto / Taxi",
    "motorcycle": "Moto",
    "plane": "Avión",
    "bus": "Bus",
    "train": "Tren",
    "metro": "Metro / Subte",
    "bike": "Bicicleta",
    "walking": "A pie",
}


def estimate_emissions(activities: list[dict]) -> list[dict]:
    """
    Compute CO2 estimates for each parsed activity.

    Returns a list of result dicts with:
      - label: display name
      - category: "food" | "transport"
      - detail: human-readable detail string
      - co2_kg: estimated kg CO2e
    """
    results = []

    for act in activities:
        category = act["category"]
        act_type = act["type"]

        if category == "food":
            factor = FOOD_FACTORS.get(act_type, 0.0)
            label = FOOD_LABELS.get(act_type, act_type.capitalize())
            results.append(
                {
                    "label": label,
                    "category": "food",
                    "detail": "1 porción",
                    "co2_kg": round(factor, 3),
                }
            )

        elif category == "transport":
            factor = TRANSPORT_FACTORS.get(act_type, 0.0)
            distance = act.get("distance_km", 10.0)
            label = TRANSPORT_LABELS.get(act_type, act_type.capitalize())
            co2 = round(factor * distance, 3)
            results.append(
                {
                    "label": label,
                    "category": "transport",
                    "detail": f"{distance:.1f} km",
                    "co2_kg": co2,
                }
            )

    return results


def total_co2(results: list[dict]) -> float:
    return round(sum(r["co2_kg"] for r in results), 3)


def co2_context(kg: float) -> str:
    """Return a plain-language comparison for the given CO2 amount."""
    if kg <= 0:
        return "Sin emisiones detectadas."
    km_car = round(kg / TRANSPORT_FACTORS["car"], 1)
    phone_charges = round(kg / 0.008)
    return (
        f"Equivale a conducir ~{km_car} km en auto "
        f"o cargar tu teléfono ~{phone_charges} veces."
    )

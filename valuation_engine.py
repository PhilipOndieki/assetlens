import re

CONDITION_MULTIPLIERS = {
    "Good": 1.00,
    "Fair": 0.70,
    "Poor": 0.40,
    "Condemned": 0.10,
}

FURNITURE_RATES = [
    (["chair", "midback", "leather"], 8500, 5000),
    (["chair", "conference"], 6500, 4000),
    (["chair"], 7000, 4500),
    (["table", "drawer"], 22000, 15000),
    (["table"], 14000, 9000),
    (["sofa", "sofaset"], 35000, 22000),
    (["cabinet"], 18000, 12000),
    (["bookshelf", "shelf"], 9500, 6000),
    (["cupboard"], 16000, 10000),
    (["wardrobe"], 20000, 13000),
    (["filing"], 14000, 9000),
    (["whiteboard", "board"], 12000, 7500),
    (["curtain", "blind"], 5000, 3000),
]

ICT_RATES = [
    (["server"], 180000, 110000),
    (["laptop"], 55000, 35000),
    (["projector"], 45000, 28000),
    (["desktop", "workstation", "computer"], 38000, 22000),
    (["printer", "photocopier", "copier", "scanner"], 25000, 15000),
    (["monitor", "screen", "display"], 12000, 7500),
    (["ups", "uninterruptible"], 18000, 11000),
    (["switch", "router", "hub", "network"], 22000, 14000),
    (["telephone", "handset", "phone"], 3500, 2000),
    (["tablet", "ipad"], 35000, 22000),
    (["camera"], 28000, 18000),
]

LAB_RATES = [
    (["microscope"], 85000, 55000),
    (["centrifuge"], 120000, 75000),
    (["spectrophotometer", "spectrometer"], 250000, 160000),
    (["autoclave"], 180000, 115000),
    (["balance", "scale", "weighing"], 35000, 22000),
    (["incubator"], 95000, 60000),
    (["refrigerator", "fridge", "freezer"], 45000, 28000),
]

VEHICLE_RATES = [
    (["bus", "matatu"], 3500000, 2200000),
    (["pickup", "lorry", "truck"], 2200000, 1400000),
    (["saloon", "vehicle", "car", "van"], 1800000, 1100000),
    (["motorcycle", "motorbike"], 180000, 110000),
]

DEFAULTS = {
    "FURNITURE AND FITTINGS": (10000, 6500),
    "COMPUTER AND ICT EQUIPMENT": (15000, 9000),
    "LAB EQUIPMENT": (30000, 19000),
    "PLANT AND MACHINERY": (50000, 32000),
    "MOTOR VEHICLES": (800000, 500000),
    "OTHER": (8000, 5000),
}


def _match(description: str, keywords: list) -> bool:
    desc = description.lower()
    return all(any(k in word for word in desc.split()) or k in desc for k in keywords)


def estimate_values(description: str, asset_type: str) -> tuple:
    desc = description.upper() if description else ""
    atype = asset_type.upper() if asset_type else "OTHER"

    rate_tables = []
    if "FURNITURE" in atype:
        rate_tables = FURNITURE_RATES
    elif "COMPUTER" in atype or "ICT" in atype:
        rate_tables = ICT_RATES
    elif "LAB" in atype:
        rate_tables = LAB_RATES
    elif "VEHICLE" in atype or "MOTOR" in atype:
        rate_tables = VEHICLE_RATES

    for keywords, fmv, reserve in rate_tables:
        if any(k.upper() in desc for k in keywords):
            return fmv, reserve

    return DEFAULTS.get(atype, (8000, 5000))


def apply_condition_multiplier(fmv: float, reserve: float, condition: str) -> tuple:
    mult = CONDITION_MULTIPLIERS.get(condition, 1.0)
    return round(fmv * mult, 2), round(reserve * mult, 2)

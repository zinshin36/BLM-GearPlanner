from materia_engine import apply_materia
from dps_formula import calculate_dps
from itertools import product

def solve_bis(gear_pool, priority_mode):
    # Organize gear by slot
    slots = {}
    for g in gear_pool:
        slot = g["Slot"]
        slots.setdefault(slot, []).append(g)
    # Generate all combinations
    combinations = product(
        slots.get("Head",[]),
        slots.get("Body",[]),
        slots.get("Hands",[]),
        slots.get("Legs",[]),
        slots.get("Feet",[]),
        slots.get("Main Hand",[]),
        slots.get("Off Hand",[]),
        slots.get("Neck",[]),
        slots.get("Earrings",[]),
        slots.get("Bracelets",[]),
        slots.get("Rings",[])
    )
    best_dps = 0
    best_build = None
    for combo in combinations:
        total_stats = {"Crit":0,"DirectHit":0,"Determination":0,"SpellSpeed":0}
        for piece in combo:
            piece = apply_materia(piece, priority_mode)
            for k,v in piece["Stats"].items():
                total_stats[k] += v
        dps = calculate_dps(total_stats)
        if dps > best_dps:
            best_dps = dps
            best_build = combo
    return best_build, best_dps

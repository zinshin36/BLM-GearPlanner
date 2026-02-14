def calculate_dps(stats, base_int=500):
    crit = stats.get("Crit",0)
    dh = stats.get("DirectHit",0)
    det = stats.get("Determination",0)
    spd = stats.get("SpellSpeed",0)
    # Simplified placeholder FFXIV formula
    return base_int * (1 + crit/100) * (1 + dh/100) * (1 + det/100)

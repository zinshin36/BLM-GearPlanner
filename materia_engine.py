def apply_materia(gear_piece, priority_list):
    slots = gear_piece.get("MateriaSlots",0)
    gear_stats = gear_piece["Stats"]
    # Simplified placeholder logic: evenly distribute by priority
    for stat in priority_list:
        if slots > 0:
            gear_stats[stat] += 10  # Placeholder value per materia
            slots -=1
    return gear_piece

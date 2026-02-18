def separate_by_slot(gear_list):
    """Organize gear by slot."""
    slots = {}
    for item in gear_list:
        slot = item["slot"]
        if slot not in slots:
            slots[slot] = []
        slots[slot].append(item)
    return slots

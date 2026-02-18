from dataclasses import dataclass

@dataclass
class Spell:
    name: str
    potency: int
    mp_cost: int
    cast_time: float

@dataclass
class PlayerState:
    mp: int = 10000
    in_astral_fire: bool = False
    in_umbral_ice: bool = True
    time_elapsed: float = 0.0

from logger import get_logger
logger = get_logger()

class SolverEngine:
    def __init__(self):
        self.best_set = None
        self.best_dps = 0

    def calculate_bis(self, gear_list):
        """
        Placeholder for branch & bound solver.
        Currently logs the received gear.
        """
        logger.info(f"Starting BIS calculation with {len(gear_list)} items")
        # TODO: implement full slot enforcement + unique rules + materia brute-force
        # For Phase 1, we just log and return first gear
        if gear_list:
            self.best_set = gear_list[0]
            self.best_dps = 0
            logger.info(f"Selected first gear as placeholder BIS")

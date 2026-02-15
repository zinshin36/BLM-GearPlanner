import requests
from logger import get_logger

logger = get_logger()
BASE_URL = "https://xivapi.com"

def fetch_gear_by_job(job="BLM", min_ilvl=600, max_ilvl=1600):
    """
    Fetch gear from XIVAPI v2 for the given job and ilvl window.
    Returns a list of gear items.
    """
    logger.info(f"Fetching gear for job={job}, ilvl {min_ilvl}-{max_ilvl}")
    try:
        url = f"{BASE_URL}/search?indexes=Item&filters=JobCategory.{job}&min_ilvl={min_ilvl}&max_ilvl={max_ilvl}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("Results", [])
    except requests.RequestException as e:
        logger.error(f"Failed to fetch gear: {e}")
        return []

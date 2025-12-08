"""Constantes pour l'intégration Hydro-Québec Pointes Hivernales."""

"""Constantes."""
DOMAIN = "hydro_winter_peak"
CONF_API_URL = "api_url"
CONF_NIGHT_START = "night_start"
CONF_NIGHT_END = "night_end"
CONF_OVERHEAT_HOURS = "overheat_hours"

"""Default values."""
DEFAULT_API_URL = "https://donnees.hydroquebec.com/api/explore/v2.1/catalog/datasets/evenements-pointe/records?where=datedebut%3E%3Dnow(hours%3D-2)%20or%20datefin%3E%3Dnow(hours%3D-0.5)&order_by=datedebut&limit=20&refine=offre%3ATPC-DPC&refine=secteurclient%3AResidentiel&timezone=America%2FNew_York"
DEFAULT_NIGHT_START = "23:00"
DEFAULT_NIGHT_END = "06:00"
DEFAULT_OVERHEAT_HOURS = 2
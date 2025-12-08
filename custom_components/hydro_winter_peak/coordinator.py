"""Coordinator V5."""
from __future__ import annotations

from datetime import timedelta
import logging
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_API_URL, CONF_NIGHT_START, CONF_NIGHT_END, CONF_OVERHEAT_HOURS

_LOGGER = logging.getLogger(__name__)

class HydroWinterPeakCoordinator(DataUpdateCoordinator):
    """Gère les données."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )
        self.entry = entry
        # ON INITIALISE POUR ÉVITER LE "NONE"
        self.data = {
            "state": "Confort",
            "raw_results": [],
            "last_check": dt_util.now()
        }

    async def _async_update_data(self):
        """Récupération."""
        config = {**self.entry.data, **self.entry.options}
        url = config.get(CONF_API_URL)
        raw_results = []
        
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(10):
                response = await session.get(url)
                if response.status == 200:
                    json_data = await response.json()
                    # Support multiple JSON shapes returned by different APIs
                    if isinstance(json_data, dict):
                        if "results" in json_data:
                            raw_results = json_data.get("results", [])
                        elif "records" in json_data:
                            records = json_data.get("records", [])
                            norm = []
                            for r in records:
                                if isinstance(r, dict):
                                    # Socrata / explore API often wraps fields
                                    if "fields" in r and isinstance(r["fields"], dict):
                                        norm.append(r["fields"])
                                    elif "record" in r and isinstance(r["record"], dict):
                                        norm.append(r["record"])
                                    else:
                                        norm.append(r)
                                else:
                                    norm.append(r)
                            raw_results = norm
                        else:
                            # Fallback: try common keys or empty
                            raw_results = json_data.get("results") or json_data.get("records") or []
                    elif isinstance(json_data, list):
                        raw_results = json_data
                else:
                    _LOGGER.warning("HTTP %s when fetching %s", response.status, url)
        except Exception:
            _LOGGER.exception("Erreur lors de la récupération des pointes")

        _LOGGER.debug("hydro_winter_peak: fetched %d result(s)", len(raw_results))

        state = self._calculate_logic(raw_results, config)

        return {
            "state": state,
            "raw_results": raw_results,
            "last_check": dt_util.now()
        }

    def _calculate_logic(self, results, config):
        """Logique métier."""
        now = dt_util.now()
        
        # 1. Pointes Hydro
        if results:
            try:
                evt = results[0]
                start = dt_util.parse_datetime(evt["datedebut"])
                end = dt_util.parse_datetime(evt["datefin"])
                overheat = config.get(CONF_OVERHEAT_HOURS, 2)
                
                if (start - timedelta(hours=overheat)) <= now < start:
                    return "OverHeat"
                elif start <= now <= end:
                    return "Low"
            except Exception:
                pass

        # 2. Mode Nuit
        start_s = config.get(CONF_NIGHT_START, "23:00")
        end_s = config.get(CONF_NIGHT_END, "06:00")
        try:
            ns_h, ns_m = map(int, start_s.split(":"))
            ne_h, ne_m = map(int, end_s.split(":"))
            night_start = now.replace(hour=ns_h, minute=ns_m, second=0, microsecond=0)
            night_end = now.replace(hour=ne_h, minute=ne_m, second=0, microsecond=0)
            
            if night_end < night_start:
                if now >= night_start: night_end += timedelta(days=1)
                elif now <= night_end: night_start -= timedelta(days=1)
            
            if night_start <= now <= night_end:
                return "Low"
        except ValueError:
            pass

        return "Confort"
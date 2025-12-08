"""Sensors Production (Final)."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import HydroWinterPeakCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HydroStateSensor(coordinator, entry),
        HydroDateSensor(coordinator, entry, "start", "Début Pointe"),
        HydroDateSensor(coordinator, entry, "end", "Fin Pointe"),
        HydroNextEventSensor(coordinator, entry),
    ])

class HydroSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_has_entity_name = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Hydro-Québec Pointes Hivernales",
            "manufacturer": "Hydro-Québec (Frablaser.com)"
        }
    
    @property
    def available(self) -> bool:
        return True

class HydroStateSensor(HydroSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_state"
        self._attr_name = "État"
        self._attr_icon = "mdi:thermostat"

    @property
    def native_value(self):
        if not self.coordinator.data or not isinstance(self.coordinator.data, dict):
            return "Confort"
        return self.coordinator.data.get("state", "Confort")

class HydroDateSensor(HydroSensor):
    """Affiche les dates."""
    def __init__(self, coordinator, entry, type_date, name):
        super().__init__(coordinator, entry)
        self.type_date = type_date
        self._attr_unique_id = f"{entry.entry_id}_{type_date}"
        self._attr_name = name
        
        # --- MODIFICATION 1 : On retire le DEVICE_CLASS TIMESTAMP ---
        # self._attr_device_class = SensorDeviceClass.TIMESTAMP (On supprime ou commente cette ligne)
        self._attr_icon = "mdi:calendar-clock" # On ajoute une icône sympa

    @property
    def native_value(self):
        if not self.coordinator.data or not isinstance(self.coordinator.data, dict):
            return None
            
        res = self.coordinator.data.get("raw_results", [])
        if not res: return None
        
        val = res[0].get("datedebut" if self.type_date == "start" else "datefin")
        
        # --- MODIFICATION 2 : On formate en texte ---
        if val:
            dt = dt_util.parse_datetime(val)
            # On s'assure d'être en heure locale (Québec)
            local_dt = dt_util.as_local(dt)
            
            # Formatage : Jour Mois Heure:Minute (ex: 08 Dec 06:00)
            # Tu peux changer le format ici : "%Y-%m-%d %H:%M" pour 2025-12-08 06:00
            return local_dt.strftime("%d %b %H:%M") 
            
        return None
class HydroNextEventSensor(HydroSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_next"
        self._attr_name = "Prochaine Pointe"

    @property
    def native_value(self):
        if not self.coordinator.data or not isinstance(self.coordinator.data, dict):
            return "Aucune"
        res = self.coordinator.data.get("raw_results", [])
        if len(res) > 1:
            try:
                s = dt_util.parse_datetime(res[1]['datedebut']).strftime("%d %b %H:%M")
                e = dt_util.parse_datetime(res[1]['datefin']).strftime("%H:%M")
                return f"{s} à {e}"
            except: pass
        return "Aucune"
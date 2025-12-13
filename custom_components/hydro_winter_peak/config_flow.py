"""Config flow pour l'intégration Hydro-Québec Pointes Hivernales."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_NIGHT_START,
    CONF_NIGHT_END,
    CONF_OVERHEAT_HOURS,
    DEFAULT_API_URL,
    DEFAULT_NIGHT_START,
    DEFAULT_NIGHT_END,
    DEFAULT_OVERHEAT_HOURS,
)

_LOGGER = logging.getLogger(__name__)

def get_schema(defaults: dict = None):
    """Génère le schéma du formulaire avec des valeurs par défaut."""
    if defaults is None:
        defaults = {}
    return vol.Schema(
        {
            vol.Required(CONF_API_URL, default=defaults.get(CONF_API_URL, DEFAULT_API_URL)): cv.string,
            vol.Required(CONF_NIGHT_START, default=defaults.get(CONF_NIGHT_START, DEFAULT_NIGHT_START)): cv.string,
            vol.Required(CONF_NIGHT_END, default=defaults.get(CONF_NIGHT_END, DEFAULT_NIGHT_END)): cv.string,
            vol.Required(CONF_OVERHEAT_HOURS, default=defaults.get(CONF_OVERHEAT_HOURS, DEFAULT_OVERHEAT_HOURS)): vol.Coerce(int),
        }
    )

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration initial."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        # On passe l'argument normalement
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Hydro-Québec Hiver", data=user_input)

        return self.async_show_form(step_id="user", data_schema=get_schema())


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Gère la modification des options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialisation."""
        # TRUC: On accepte l'argument 'config_entry' pour ne pas faire planter l'appel,
        # mais on ne tente PAS de le stocker dans self.config_entry car c'est interdit (read-only).
        pass

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Gère l'affichage du formulaire d'options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # ASTUCE DE SIOUX :
        # Au lieu d'utiliser self.config_entry (qui plante), on va le chercher via l'ID
        # self.handler contient l'ID de l'entrée qu'on est en train de modifier.
        entry = self.hass.config_entries.async_get_entry(self.handler)
        
        # Maintenant on peut lire les données en toute sécurité
        data = entry.data or {}
        options = entry.options or {}
        
        current_config = {**data, **options}
        
        return self.async_show_form(
            step_id="init",
            data_schema=get_schema(current_config)
        )
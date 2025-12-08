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
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Hydro-Québec Hiver", data=user_input)
        return self.async_show_form(step_id="user", data_schema=get_schema())


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Gère la modification des options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialisation."""
        # ON REMET CETTE LIGNE (C'est elle qui manquait et causait l'erreur 500)
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Gère l'affichage du formulaire d'options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # On récupère la config actuelle pour pré-remplir
        # C'est ici que ça plantait car self.config_entry n'existait pas
        current_config = {**self.config_entry.data, **self.config_entry.options}
        
        return self.async_show_form(
            step_id="init",
            data_schema=get_schema(current_config)
        )
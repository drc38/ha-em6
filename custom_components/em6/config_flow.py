"""Config flow for the em6 integration."""

from __future__ import annotations

from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LOCATION

from .api import em6Api
from .const import DOMAIN


class em6ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for em6."""

    VERSION = 1

    async def async_step_user(self, user_input: Dict[str, Any] | None = None):  # type: ignore[override]
        errors: Dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_LOCATION], data=user_input)

        api = em6Api()
        locations = await api.async_get_locations()
        if not locations:
            errors["base"] = "cannot_connect"
            locations = []

        data_schema = vol.Schema({vol.Required(CONF_LOCATION): vol.In(locations)})
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)


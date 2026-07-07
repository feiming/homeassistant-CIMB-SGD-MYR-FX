"""Config flow for CIMB SGD to MYR FX Rate."""
import voluptuous as vol
from homeassistant import config_entries
from . import DOMAIN


class CIMBFXConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CIMB SGD-MYR FX."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="CIMB SGD to MYR FX Rate", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

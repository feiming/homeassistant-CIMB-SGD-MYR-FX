"""Config flow for CIMB SGD to MYR FX Rate."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from . import DOMAIN, DEFAULT_SCAN_INTERVAL


class CIMBFXConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CIMB SGD-MYR FX."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="CIMB SGD to MYR FX Rate",
                data={CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL]},
            )

        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL):
                vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

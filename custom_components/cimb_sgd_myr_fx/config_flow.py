"""Config flow for CIMB SGD to MYR FX Rate."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_SCAN_INTERVAL
from . import DOMAIN, DEFAULT_SCAN_INTERVAL


class CIMBFXConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CIMB SGD-MYR FX."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CIMBFXOptionsFlow(config_entry)

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


class CIMBFXOptionsFlow(config_entries.OptionsFlow):
    """Handle reconfiguration of the scan interval after setup."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=current):
                vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
        })
        return self.async_show_form(step_id="init", data_schema=schema)

"""CIMB SGD to MYR FX Rate sensor."""
import re
import logging
from datetime import timedelta

from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)
URL = "https://www.cimbclicks.com.sg/sgd-to-myr"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the CIMB FX sensor platform."""
    session = async_get_clientsession(hass)
    coordinator = CIMBFXCoordinator(hass, session)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([CIMBFXSensor(coordinator)])


class CIMBFXCoordinator(DataUpdateCoordinator):
    """Fetches SGD-MYR rate from CIMB Clicks."""

    def __init__(self, hass, session):
        super().__init__(
            hass,
            _LOGGER,
            name="CIMB SGD-MYR FX",
            update_interval=SCAN_INTERVAL,
        )
        self._session = session

    async def _async_update_data(self):
        try:
            async with self._session.get(URL, headers=HEADERS) as response:
                response.raise_for_status()
                html = await response.text()
        except Exception as err:
            raise UpdateFailed(f"Error fetching CIMB FX page: {err}") from err

        return _parse_rate(html)


def _parse_rate(html: str) -> float:
    """Extract the SGD-MYR rate from the page HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Primary: server-rendered hidden input from IBM WebSphere Portal portlet
    # Name ends with _rateList and value looks like "[3.1565]"
    rate_input = soup.find(
        "input", {"name": lambda n: n and n.endswith("_rateList")}
    )
    if rate_input:
        match = re.search(r"[\d]+\.[\d]+", rate_input.get("value", ""))
        if match:
            return float(match.group())

    # Fallback: label text rendered by JS, e.g. "SGD 1.00 = MYR 3.1565"
    rate_label = soup.find("label", {"id": "rateStr"})
    if rate_label:
        match = re.search(r"MYR\s+([\d]+\.[\d]+)", rate_label.get_text())
        if match:
            return float(match.group(1))

    raise UpdateFailed("Could not parse FX rate from CIMB page")


class CIMBFXSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity for the CIMB SGD-MYR exchange rate."""

    _attr_name = "CIMB SGD to MYR FX Rate"
    _attr_unique_id = "cimb_sgd_myr_fx_rate"
    _attr_icon = "mdi:cash-multiple"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "MYR/SGD"

    def __init__(self, coordinator: CIMBFXCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def native_value(self):
        return self.coordinator.data

    @property
    def extra_state_attributes(self):
        return {
            "source_url": URL,
            "currency_pair": "SGD/MYR",
            "description": "1 SGD = X MYR",
        }

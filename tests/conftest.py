"""Stub out homeassistant modules so tests run without a full HA install."""
import sys
from types import ModuleType
from unittest.mock import MagicMock


class UpdateFailed(Exception):
    """Mirrors homeassistant.helpers.update_coordinator.UpdateFailed."""


class _DataUpdateCoordinator:
    """Minimal stub of DataUpdateCoordinator."""

    def __init__(self, hass, logger, *, name, update_interval):
        self.data = None


class _CoordinatorEntity:
    """Minimal stub of CoordinatorEntity."""

    def __init__(self, coordinator):
        self.coordinator = coordinator


class _SensorStateClass:
    MEASUREMENT = "measurement"


class _ConfigEntry:
    """Minimal stub of ConfigEntry."""


class _ConfigFlow:
    """Minimal stub of ConfigFlow."""

    def __init_subclass__(cls, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)


class _ConfigEntries:
    ConfigFlow = _ConfigFlow


def _build_stubs():
    coordinator_mod = ModuleType("homeassistant.helpers.update_coordinator")
    coordinator_mod.UpdateFailed = UpdateFailed
    coordinator_mod.DataUpdateCoordinator = _DataUpdateCoordinator
    coordinator_mod.CoordinatorEntity = _CoordinatorEntity

    sensor_mod = ModuleType("homeassistant.components.sensor")
    sensor_mod.SensorEntity = object
    sensor_mod.SensorStateClass = _SensorStateClass

    aiohttp_mod = ModuleType("homeassistant.helpers.aiohttp_client")
    aiohttp_mod.async_get_clientsession = MagicMock()

    entity_platform_mod = ModuleType("homeassistant.helpers.entity_platform")
    entity_platform_mod.AddEntitiesCallback = MagicMock()

    config_entries_mod = ModuleType("homeassistant.config_entries")
    config_entries_mod.ConfigEntry = _ConfigEntry
    config_entries_mod.ConfigFlow = _ConfigFlow

    core_mod = ModuleType("homeassistant.core")
    core_mod.HomeAssistant = MagicMock()

    const_mod = ModuleType("homeassistant.const")
    const_mod.CONF_SCAN_INTERVAL = "scan_interval"

    ha_mod = ModuleType("homeassistant")
    components_mod = ModuleType("homeassistant.components")
    helpers_mod = ModuleType("homeassistant.helpers")

    sys.modules.update(
        {
            "homeassistant": ha_mod,
            "homeassistant.components": components_mod,
            "homeassistant.components.sensor": sensor_mod,
            "homeassistant.config_entries": config_entries_mod,
            "homeassistant.const": const_mod,
            "homeassistant.core": core_mod,
            "homeassistant.helpers": helpers_mod,
            "homeassistant.helpers.aiohttp_client": aiohttp_mod,
            "homeassistant.helpers.entity_platform": entity_platform_mod,
            "homeassistant.helpers.update_coordinator": coordinator_mod,
        }
    )


_build_stubs()

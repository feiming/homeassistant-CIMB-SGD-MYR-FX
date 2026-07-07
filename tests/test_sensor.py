"""Unit tests for CIMB SGD-MYR FX sensor."""
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

# conftest.py stubs HA before this import
from tests.conftest import UpdateFailed
from custom_components.cimb_sgd_myr_fx.sensor import (
    _parse_rate,
    CIMBFXCoordinator,
    CIMBFXSensor,
    URL,
)
from custom_components.cimb_sgd_myr_fx import DEFAULT_SCAN_INTERVAL


# ---------------------------------------------------------------------------
# HTML fixtures
# ---------------------------------------------------------------------------

def _html_with_hidden_input(rate="3.1565"):
    return f"""
    <html><body>
      <form>
        <input type="hidden"
               name="ns_Z7_O9A2184149V7306J1RH3VL0SS0_rateList"
               value="[{rate}]">
        <label id="rateStr" class="rateStr">SGD 1.00 = MYR {rate}</label>
      </form>
    </body></html>
    """


def _html_label_only(rate="3.1565"):
    return f"""
    <html><body>
      <form>
        <label id="rateStr" class="rateStr">SGD 1.00 = MYR {rate}</label>
      </form>
    </body></html>
    """


def _html_no_rate():
    return "<html><body><p>No rate here.</p></body></html>"


def _html_hidden_input_bad_value():
    return """
    <html><body>
      <form>
        <input type="hidden"
               name="ns_Z7_abc_rateList"
               value="[N/A]">
      </form>
    </body></html>
    """


# ---------------------------------------------------------------------------
# _parse_rate — pure function tests
# ---------------------------------------------------------------------------

class TestParseRate:
    def test_hidden_input_primary_path(self):
        assert _parse_rate(_html_with_hidden_input("3.1565")) == 3.1565

    def test_hidden_input_different_rate(self):
        assert _parse_rate(_html_with_hidden_input("3.2000")) == 3.2000

    def test_hidden_input_high_precision(self):
        assert _parse_rate(_html_with_hidden_input("3.14159")) == pytest.approx(3.14159)

    def test_label_fallback_when_no_hidden_input(self):
        assert _parse_rate(_html_label_only("3.1565")) == 3.1565

    def test_label_fallback_different_rate(self):
        assert _parse_rate(_html_label_only("3.9999")) == 3.9999

    def test_hidden_input_takes_priority_over_label(self):
        # Hidden input has 3.1000, label has 3.9999 — should return hidden input value
        html = """
        <html><body><form>
          <input type="hidden" name="ns_Z7_abc_rateList" value="[3.1000]">
          <label id="rateStr">SGD 1.00 = MYR 3.9999</label>
        </form></body></html>
        """
        assert _parse_rate(html) == 3.1000

    def test_raises_when_no_rate_found(self):
        with pytest.raises(UpdateFailed, match="Could not parse"):
            _parse_rate(_html_no_rate())

    def test_falls_through_to_label_when_hidden_input_value_is_invalid(self):
        # Hidden input present but value has no number → falls through to label
        html = """
        <html><body><form>
          <input type="hidden" name="ns_Z7_abc_rateList" value="[N/A]">
          <label id="rateStr">SGD 1.00 = MYR 3.1565</label>
        </form></body></html>
        """
        assert _parse_rate(html) == 3.1565

    def test_raises_when_hidden_input_invalid_and_no_label(self):
        with pytest.raises(UpdateFailed):
            _parse_rate(_html_hidden_input_bad_value())

    def test_empty_html(self):
        with pytest.raises(UpdateFailed):
            _parse_rate("")

    def test_returns_float(self):
        result = _parse_rate(_html_with_hidden_input("3.1565"))
        assert isinstance(result, float)

    def test_partial_name_match_for_hidden_input(self):
        # Any input whose name ends with _rateList should match
        html = """
        <html><body><form>
          <input type="hidden" name="portlet_X_rateList" value="[3.5000]">
        </form></body></html>
        """
        assert _parse_rate(html) == 3.5000

    def test_ignores_unrelated_hidden_inputs(self):
        html = """
        <html><body><form>
          <input type="hidden" name="ns_Z7_abc_convertedAmts" value="[1000.00]">
          <input type="hidden" name="ns_Z7_abc_maxTransferAmts" value="[35000.00]">
          <label id="rateStr">SGD 1.00 = MYR 3.2500</label>
        </form></body></html>
        """
        assert _parse_rate(html) == 3.2500


# ---------------------------------------------------------------------------
# CIMBFXCoordinator — async update tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestCIMBFXCoordinator:
    def _make_coordinator(self, html):
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = AsyncMock(return_value=html)

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        coordinator = CIMBFXCoordinator.__new__(CIMBFXCoordinator)
        coordinator._session = mock_session
        return coordinator

    async def test_returns_rate_on_success(self):
        coordinator = self._make_coordinator(_html_with_hidden_input("3.1565"))
        result = await coordinator._async_update_data()
        assert result == 3.1565

    async def test_raises_update_failed_on_http_error(self):
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock(side_effect=Exception("503"))
        mock_response.text = AsyncMock(return_value="")

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_cm)

        coordinator = CIMBFXCoordinator.__new__(CIMBFXCoordinator)
        coordinator._session = mock_session

        with pytest.raises(UpdateFailed, match="Error fetching"):
            await coordinator._async_update_data()

    async def test_raises_update_failed_when_rate_not_found(self):
        coordinator = self._make_coordinator(_html_no_rate())
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    async def test_uses_correct_url(self):
        coordinator = self._make_coordinator(_html_with_hidden_input("3.1565"))
        await coordinator._async_update_data()
        coordinator._session.get.assert_called_once()
        call_args = coordinator._session.get.call_args
        assert call_args[0][0] == URL

    async def test_sends_browser_like_headers(self):
        coordinator = self._make_coordinator(_html_with_hidden_input("3.1565"))
        await coordinator._async_update_data()
        call_kwargs = coordinator._session.get.call_args[1]
        assert "User-Agent" in call_kwargs["headers"]
        assert "Mozilla" in call_kwargs["headers"]["User-Agent"]



class TestCIMBFXCoordinatorInterval:
    def test_coordinator_stores_custom_interval(self):
        coordinator = CIMBFXCoordinator.__new__(CIMBFXCoordinator)
        coordinator._session = MagicMock()
        coordinator.update_interval = timedelta(minutes=15)
        assert coordinator.update_interval == timedelta(minutes=15)

    def test_default_scan_interval_constant(self):
        assert DEFAULT_SCAN_INTERVAL == 30


# ---------------------------------------------------------------------------
# CIMBFXSensor — property tests
# ---------------------------------------------------------------------------

class TestCIMBFXSensor:
    def _make_sensor(self, rate=3.1565):
        coordinator = MagicMock()
        coordinator.data = rate
        sensor = CIMBFXSensor.__new__(CIMBFXSensor)
        sensor.coordinator = coordinator
        return sensor

    def test_native_value_returns_coordinator_data(self):
        sensor = self._make_sensor(3.1565)
        assert sensor.native_value == 3.1565

    def test_native_value_updates_with_coordinator(self):
        sensor = self._make_sensor(3.1565)
        sensor.coordinator.data = 3.2000
        assert sensor.native_value == 3.2000

    def test_native_value_none_when_no_data(self):
        sensor = self._make_sensor(None)
        assert sensor.native_value is None

    def test_extra_state_attributes_contains_source_url(self):
        sensor = self._make_sensor()
        assert sensor.extra_state_attributes["source_url"] == URL

    def test_extra_state_attributes_contains_currency_pair(self):
        sensor = self._make_sensor()
        assert sensor.extra_state_attributes["currency_pair"] == "SGD/MYR"

    def test_unique_id(self):
        assert CIMBFXSensor._attr_unique_id == "cimb_sgd_myr_fx_rate"

    def test_unit_of_measurement(self):
        assert CIMBFXSensor._attr_native_unit_of_measurement == "MYR/SGD"

    def test_name(self):
        assert CIMBFXSensor._attr_name == "CIMB SGD to MYR FX Rate"

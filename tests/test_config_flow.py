"""Unit tests for CIMB FX config flow."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# conftest.py stubs HA before this import
from custom_components.cimb_sgd_myr_fx.config_flow import CIMBFXConfigFlow


class TestCIMBFXConfigFlow:
    def _make_flow(self):
        flow = CIMBFXConfigFlow.__new__(CIMBFXConfigFlow)
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        return flow

    @pytest.mark.asyncio
    async def test_step_user_shows_form_when_no_input(self):
        flow = self._make_flow()
        result = await flow.async_step_user(user_input=None)
        flow.async_show_form.assert_called_once()
        call_kwargs = flow.async_show_form.call_args.kwargs
        assert call_kwargs["step_id"] == "user"
        assert result == {"type": "form"}

    @pytest.mark.asyncio
    async def test_step_user_creates_entry_on_submit(self):
        flow = self._make_flow()
        result = await flow.async_step_user(user_input={})
        flow.async_create_entry.assert_called_once_with(
            title="CIMB SGD to MYR FX Rate", data={}
        )
        assert result == {"type": "create_entry"}

    @pytest.mark.asyncio
    async def test_step_user_sets_unique_id(self):
        flow = self._make_flow()
        await flow.async_step_user(user_input={})
        flow.async_set_unique_id.assert_called_once_with("cimb_sgd_myr_fx")

    @pytest.mark.asyncio
    async def test_step_user_aborts_if_already_configured(self):
        flow = self._make_flow()
        await flow.async_step_user(user_input={})
        flow._abort_if_unique_id_configured.assert_called_once()

    def test_flow_version(self):
        assert CIMBFXConfigFlow.VERSION == 1

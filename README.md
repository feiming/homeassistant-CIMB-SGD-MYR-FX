# CIMB SGD to MYR FX Rate — Home Assistant Integration

A custom Home Assistant integration that polls the live SGD to MYR exchange rate from [CIMB Clicks](https://www.cimbclicks.com.sg/sgd-to-myr) every 30 minutes and exposes it as a sensor.

## Sensor

| Entity ID | Unit | State class |
|---|---|---|
| `sensor.cimb_sgd_to_myr_fx_rate` | MYR/SGD | Measurement |

**Attributes:**

- `source_url` — the scraped page URL
- `currency_pair` — `SGD/MYR`
- `description` — `1 SGD = X MYR`

---

## Installation via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=feiming&repository=homeassistant-CIMB-SGD-MYR-FX&category=integration)

### Prerequisites

- [HACS](https://hacs.xyz/) installed in your Home Assistant instance

### Steps

1. In Home Assistant, go to **HACS → Integrations**
2. Click the three-dot menu (⋮) in the top-right corner and select **Custom repositories**
3. Enter the repository URL:
   ```
   https://github.com/feiming/homeassistant-CIMB-SGD-MYR-FX
   ```
   and set category to **Integration**, then click **Add**
4. Search for **CIMB SGD to MYR FX Rate** in HACS and click **Download**
5. Restart Home Assistant

### Configuration

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: cimb_sgd_myr_fx
```

Restart Home Assistant again. The sensor `sensor.cimb_sgd_to_myr_fx_rate` will appear with the current rate.

### Changing the update interval after setup

If you added the integration through the UI, open **Settings → Devices & Services → CIMB SGD to MYR FX Rate → Configure**, set a new **Update interval (minutes)** (1–1440) and submit. The integration reloads automatically with the new interval — no restart needed.

---

## Manual Installation

1. Copy the `custom_components/cimb_sgd_myr_fx/` folder into your HA config directory:
   ```
   config/custom_components/cimb_sgd_myr_fx/
   ```
2. Add to `configuration.yaml`:
   ```yaml
   sensor:
     - platform: cimb_sgd_myr_fx
   ```
3. Restart Home Assistant

---

## Development & Testing

### Requirements

- Python 3.12+
- Dependencies listed in `requirements-test.txt`

### Install test dependencies

```bash
pip install -r requirements-test.txt
```

### Run tests

```bash
pytest tests/ -v
```

No Home Assistant installation is required — HA modules are stubbed out in `tests/conftest.py`.

### Test coverage

| Area | Tests |
|---|---|
| `_parse_rate` — HTML scraping logic | 13 |
| `CIMBFXCoordinator` — HTTP fetch & error handling | 5 |
| `CIMBFXSensor` — entity properties | 8 |

---

## Data Source

Rate is scraped from [https://www.cimbclicks.com.sg/sgd-to-myr](https://www.cimbclicks.com.sg/sgd-to-myr) and updated every 30 minutes.

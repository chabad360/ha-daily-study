from datetime import timedelta
import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


DOMAIN = "daily_study"
SEFARIA_BASE_URL = "https://www.sefaria.org/api/calendars"


class SefariaDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, data: dict):
        super().__init__(
            hass,
            _LOGGER,
            name="Sefaria Calendar Data",
            update_interval=timedelta(
                hours=1
            ),  # Adjust based on how often you need updates
        )
        self.session = async_get_clientsession(hass)
        self.data = data

    async def _async_update_data(self):
        try:
            async with self.session.get(
                f"{SEFARIA_BASE_URL}?diaspora={'1' if self.data['Diaspora'] is True  else '0'}&timezone={self.hass.config.time_zone}",
            ) as response:
                return await response.json()
        except Exception as e:
            raise UpdateFailed(f"Failed to fetch data: {e}")

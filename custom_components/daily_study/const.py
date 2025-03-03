from datetime import timedelta
import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry


_LOGGER = logging.getLogger(__name__)


DOMAIN = "daily_study"
SEFARIA_BASE_URL = "https://www.sefaria.org/api/calendars"


class SefariaDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            name="Sefaria Calendar",
            update_interval=timedelta(
                hours=1
            ),
            config_entry=config,
            always_update=True
        )
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self):
        _LOGGER.debug(f"Fetching data from Sefaria, config: {self.config_entry.data}")
        try:
            async with self.session.get(
                f"{SEFARIA_BASE_URL}?diaspora={'1' if self.config_entry.data['Diaspora'] is True else '0'}&timezone={self.hass.config.time_zone}",
            ) as response:
                return await response.json()
        except Exception as e:
            raise UpdateFailed(f"Failed to fetch data: {e}")

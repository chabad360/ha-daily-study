from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

ITEM_TYPE = "Daily Study"


class SefariaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        self._state = None
        super().__init__(coordinator)
        self._item_type = ITEM_TYPE
        self._name = f"{self._item_type} {self._detail_type}"
        self._unique_id = f"{self._item_type}_{self._detail_type}"
        self.icon = "mdi:book-open-variant-outline"
        self.attribution = "Data provided by Sefaria"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._item_type)},
            "name": self._item_type,
            "manufacturer": "Sefaria",
            "model": "Daily Study",
        }

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._handle_coordinator_update()

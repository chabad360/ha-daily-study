from typing import Any

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN

ITEM_TYPE = "Daily Study"


class SefariaSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._state = None
        self._item_type = ITEM_TYPE
        self._name = f"{self._item_type} {self._detail_type}"
        self._unique_id = f"{self._item_type}_{self._detail_type}"

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
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
        self.async_update_from_data()

    async def async_update(self):
        self.async_update_from_data()

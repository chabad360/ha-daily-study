from datetime import date
import logging
import re

from .const import DOMAIN
from .util import SefariaSensor

from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            ChumashSensor(coordinator),
            DafYomiSensor(coordinator),
            RambamSensor(coordinator),
            Rambam3Sensor(coordinator),
            TanyaSensor(coordinator),
        ],
        update_before_add=True
    )

def get_index(calendar_items, type):
    for i, item in enumerate(calendar_items):
        if item["title"]["en"] == type:
            return i
    return None



class ChumashSensor(SefariaSensor):
    def __init__(self, coordinator):
        self._detail_type = "Chumash"
        super().__init__(coordinator)

    @property
    def extra_state_attributes(self):
        return self.parse_aliyah(self._state) | {
            "Parshah": self._data["displayValue"]["en"],
            "Parsha (Hebrew)": self._data[
                "displayValue"
            ]["he"],
            "Aliyah": date.today().isoweekday()%7,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        self._index = get_index(self.coordinator.data["calendar_items"], "Parashat Hashavua")
        self._data = self.coordinator.data["calendar_items"][self._index]
        self._state = (
            f"{self._data["displayValue"]["en"]}, {self._data["extraDetails"]["aliyot"][
                date.today().isoweekday()%7
            ]
            or "Not Available"}"
        )
        self.async_write_ha_state()

    def parse_aliyah(self, aliyah: str) -> dict:
        r = re.search(
            r"(?P<Book>\D+)\s(?P<Start>(?P<Start_Chapter>\d{1,3}):(?P<Start_Verse>\d{1,3}))-(?P<End>(?P<End_Chapter>\d{1,3}):(?P<End_Verse>\d{1,3}))",
            aliyah,
        )

        return r.groupdict() if r else {}


class DafYomiSensor(SefariaSensor):
    def __init__(self, coordinator):
        self._detail_type = "Daf Yomi"
        super().__init__(coordinator)

    @property
    def extra_state_attributes(self):
        he = self._data["displayValue"]["he"]
        he_r = self.parse_text(he)
        return self.parse_text(self._state) | {
            "Masechet (Hebrew)": he_r.get("Masechet", "Not Available"),
            "Daf (Hebrew)": he_r.get("Daf", "Not Available"),
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        self._index = get_index(self.coordinator.data["calendar_items"], "Daf Yomi")
        self._data = self.coordinator.data["calendar_items"][self._index]
        self._state = (
            self._data["displayValue"]["en"]
            or "Not Available"
        )

    def parse_text(self, text: str) -> dict:
        r = re.search(
            r"(?P<Masechet>\D+)\s(?P<Daf>(?:\D{1,2}״\D)|\d{1,3})",
            text,
        )

        return r.groupdict() if r else {}


class RambamSensor(SefariaSensor):
    def __init__(self, coordinator):
        self._detail_type = "Rambam"
        super().__init__(coordinator)

    @property
    def extra_state_attributes(self):
        he = self._data["displayValue"]["he"]
        he_r = self.parse_text(he)
        return self.parse_text(self._state) | {
            "Halachah (Hebrew)": he_r.get("Halachah", "Not Available"),
            "Perek (Hebrew)": he_r.get("Perek", "Not Available"),
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        self._index = get_index(self.coordinator.data["calendar_items"], "Daily Rambam")
        self._data = self.coordinator.data["calendar_items"][self._index]
        self._state = (
            self._data["displayValue"]["en"]
            or "Not Available"
        )

    def parse_text(self, text: str) -> dict:
        r = re.search(
            r"(?:הלכות\s)?(?P<Halachah>\D+)\s(?P<Perek>(?:\D{1,2}[״׳]\D)|\d{1,3})",
            text,
        )

        return r.groupdict() if r else {}


class Rambam3Sensor(SefariaSensor):
    def __init__(self, coordinator):
        self._detail_type = "Rambam (3 Chapters)"
        super().__init__(coordinator)

    @property
    def extra_state_attributes(self):
        he = self._data["displayValue"]["he"]
        he_r = self.parse_text(he)
        return self.parse_text(self._state) | {
            "Halachah (Hebrew)": he_r.get("Halachah", "Not Available"),
            "First Perek (Hebrew)": he_r.get("First_Perek", "Not Available"),
            "Last Perek (Hebrew)": he_r.get("Last_Perek", "Not Available"),
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        self._index = get_index(self.coordinator.data["calendar_items"], "Daily Rambam (3 Chapters)")
        self._data = self.coordinator.data["calendar_items"][self._index]
        self._state = (
            self._data["displayValue"]["en"]
            or "Not Available"
        )

    def parse_text(self, text: str) -> dict:
        r = re.search(
            r"(?:הלכות\s)?(?P<Halachah>\D+)\s(?P<First_Perek>(?:\D{1,2}[״׳]\D?)|\d{1,3})-(?P<Last_Perek>(?:\D{1,2}[״׳]\D?)|\d{1,3})",
            text,
        )

        return r.groupdict() if r else {}


class TanyaSensor(SefariaSensor):
    def __init__(self, coordinator):
        self._detail_type = "Tanya"
        super().__init__(coordinator)

    @property
    def extra_state_attributes(self):
        return self.parse_text(self._data["ref"]) | {
            "Day": self._data["displayValue"]["en"],
            "Day (Hebrew)": self._data["displayValue"][
                "he"
            ],
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        self._index = get_index(self.coordinator.data["calendar_items"], "Tanya Yomi")
        self._data = self.coordinator.data["calendar_items"][self._index]
        self._state = (
            self._data["ref"].split(";")[1].strip() or "Not Available"
        )

    def parse_text(self, text: str) -> dict:
        r = re.search(
            r".*Part\s(?P<Part>\D+);\s(?P<Book>\D+)\s(?P<Chapter>\d{1,3})",
            text,
        )

        return r.groupdict() if r else {}

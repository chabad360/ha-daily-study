from datetime import date
import logging
import re

from .const import DOMAIN
from .util import SefariaSensor

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
        ]
    )


class ChumashSensor(SefariaSensor):
    def __init__(self, coordinator):
        self._detail_type = "Chumash"
        super().__init__(coordinator)

    @property
    def extra_state_attributes(self):
        return self.parse_aliyah(self._state) | {
            "Parshah": self.coordinator.data["calendar_items"][0]["displayValue"]["en"],
            "Parsha (Hebrew)": self.coordinator.data["calendar_items"][0][
                "displayValue"
            ]["he"],
            "Aliyah": date.today().weekday(),
        }

    def async_update_from_data(self):
        self._state = (
            self.coordinator.data["calendar_items"][0]["extraDetails"]["aliyot"][
                date.today().weekday()
            ]
            or "Not Available"
        )

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
        he = self.coordinator.data["calendar_items"][2]["displayValue"]["he"]
        he_r = self.parse_text(he)
        return self.parse_text(self._state) | {
            "Masechet (Hebrew)": he_r.get("Masechet", "Not Available"),
            "Daf (Hebrew)": he_r.get("Daf", "Not Available"),
        }

    def async_update_from_data(self):
        self._state = (
            self.coordinator.data["calendar_items"][2]["displayValue"]["en"]
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
        he = self.coordinator.data["calendar_items"][5]["displayValue"]["he"]
        he_r = self.parse_text(he)
        return self.parse_text(self._state) | {
            "Halachah (Hebrew)": he_r.get("Halachah", "Not Available"),
            "Perek (Hebrew)": he_r.get("Perek", "Not Available"),
        }

    def async_update_from_data(self):
        self._state = (
            self.coordinator.data["calendar_items"][5]["displayValue"]["en"]
            or "Not Available"
        )

    def parse_text(self, text: str) -> dict:
        r = re.search(
            r"(?P<Halachah>\D+)\s(?P<Perek>(?:\D{1,2}״\D)|\d{1,3})",
            text,
        )

        return r.groupdict() if r else {}


class Rambam3Sensor(SefariaSensor):
    def __init__(self, coordinator):
        self._detail_type = "Rambam (3 Chapters)"
        super().__init__(coordinator)

    @property
    def extra_state_attributes(self):
        he = self.coordinator.data["calendar_items"][6]["displayValue"]["he"]
        he_r = self.parse_text(he)
        return self.parse_text(self._state) | {
            "Halachah (Hebrew)": he_r.get("Halachah", "Not Available"),
            "First Perek (Hebrew)": he_r.get("First_Perek", "Not Available"),
            "Last Perek (Hebrew)": he_r.get("Last_Perek", "Not Available"),
        }

    def async_update_from_data(self):
        self._state = (
            self.coordinator.data["calendar_items"][6]["displayValue"]["en"]
            or "Not Available"
        )

    def parse_text(self, text: str) -> dict:
        r = re.search(
            r"(?P<Halachah>\D+)\s(?P<First_Perek>(?:\D{1,2}[״׳]\D?)|\d{1,3})-(?P<Last_Perek>(?:\D{1,2}[״׳]\D?)|\d{1,3})",
            text,
        )

        return r.groupdict() if r else {}


class TanyaSensor(SefariaSensor):
    def __init__(self, coordinator):
        self._detail_type = "Tanya"
        super().__init__(coordinator)

    @property
    def extra_state_attributes(self):
        return self.parse_text(self._state) | {
            "Day": self.coordinator.data["calendar_items"][12]["displayValue"]["en"],
            "Day (Hebrew)": self.coordinator.data["calendar_items"][12]["displayValue"][
                "he"
            ],
        }

    def async_update_from_data(self):
        self._state = (
            self.coordinator.data["calendar_items"][12]["ref"] or "Not Available"
        )

    def parse_text(self, text: str) -> dict:
        r = re.search(
            r".*Part\s(?P<Part>\D+);\s(?P<Book>\D+)\s(?P<Chapter>\d{1,3})",
            text,
        )

        return r.groupdict() if r else {}

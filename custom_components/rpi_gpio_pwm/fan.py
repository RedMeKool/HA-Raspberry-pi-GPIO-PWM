"""Support for Fan that can be controlled using PWM."""

from __future__ import annotations

import logging

from gpiozero import PWMOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
import voluptuous as vol

from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
    PLATFORM_SCHEMA,
    FanEntity,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_UNIQUE_ID,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    CONF_FAN,
    CONF_FANS,
    CONF_PIN,
    DEFAULT_FAN_PERCENTAGE,
    DEFAULT_HOST,
    DEFAULT_PORT,
)

_LOGGER = logging.getLogger(__name__)

SUPPORT_SIMPLE_FAN = (
    FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_FANS): vol.All(
            cv.ensure_list,
            [
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_PIN): cv.positive_int,
                    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                    vol.Optional(CONF_UNIQUE_ID): cv.string,
                }
            ],
        )
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the PWM FAN."""
    fans = []
    for fan_conf in config[CONF_FANS]:
        pin = fan_conf[CONF_PIN]
        opt_args = {}
        opt_args["pin_factory"] = PiGPIOFactory(
            host=fan_conf[CONF_HOST], port=fan_conf[CONF_PORT]
        )
        fan = PwmSimpleFan(
            fan=PWMOutputDevice(pin, **opt_args),
            name=fan_conf[CONF_NAME],
            unique_id=fan_conf[CONF_UNIQUE_ID],
            hass=hass,
        )
        fans.append(fan)

    add_entities(fans)


# Transform the configEntry from config_flow into an entity
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up fan from the ConfigEntry configuration created in the integrations UI."""
    pin = config_entry.data.get(CONF_PIN)
    opt_args = {}
    opt_args["pin_factory"] = PiGPIOFactory(
        host=config_entry.data.get(CONF_HOST), port=config_entry.data.get(CONF_PORT)
    )
    entity1 = PwmSimpleFan(
        fan=PWMOutputDevice(pin, **opt_args),
        hass=hass,
        config_entry=config_entry,
    )
    # Do not create entity if is not a fan
    if CONF_FAN not in config_entry.title:
        pass
    else:
        async_add_entities([entity1], update_before_add=True)


class PwmSimpleFan(FanEntity, RestoreEntity):
    """Representation of a simple PWM FAN."""

    def __init__(self, **kwarg):
        """Initialize PWM FAN."""
        self._hass = kwarg["hass"]
        self._attr_has_entity_name = True
        self._fan = kwarg["fan"]
        self._name = (
            kwarg["config_entry"].data.get(CONF_NAME)
            if "config_entry" in kwarg
            else kwarg["name"]
        )
        self._unique_id = (
            kwarg["config_entry"].entry_id
            if "config_entry" in kwarg
            else kwarg["unique_id"]
        )
        self._is_on = False
        self._percentage = DEFAULT_FAN_PERCENTAGE

    async def async_added_to_hass(self):
        """Handle entity about to be added to hass event."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            self._is_on = last_state.state == STATE_ON
            self._percentage = last_state.attributes.get(
                "percentage", DEFAULT_FAN_PERCENTAGE
            )

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the group."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    @property
    def percentage(self):
        """Return the percentage property."""
        return self._percentage

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_SIMPLE_FAN

    def turn_on(
        self,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        if percentage is not None:
            self._percentage = percentage
        elif ATTR_PERCENTAGE in kwargs:
            self._percentage = kwargs[ATTR_PERCENTAGE]
        self._fan.value = self._percentage / 100
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        if self.is_on:
            self._fan.off()
        self._is_on = False
        self.schedule_update_ha_state()

    def set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        self._percentage = percentage
        self._fan.value = self._percentage / 100
        self._is_on = True
        self.schedule_update_ha_state()


"""Support for LED lights that can be controlled using PWM."""

from __future__ import annotations

import logging

from gpiozero import PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
    LightEntityFeature,
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
    CONF_FREQUENCY,
    CONF_LEDS,
    CONF_LIGHT,
    CONF_PIN,
    DEFAULT_BRIGHTNESS,
    DEFAULT_HOST,
    DEFAULT_PORT,
)

_LOGGER = logging.getLogger(__name__)

SUPPORT_SIMPLE_LED = LightEntityFeature.TRANSITION
COLORMODE = ColorMode.BRIGHTNESS

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_LEDS): vol.All(
            cv.ensure_list,
            [
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_PIN): cv.positive_int,
                    vol.Optional(CONF_FREQUENCY): cv.positive_int,
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
    """Set up the PWM LED lights."""
    leds = []
    for led_conf in config[CONF_LEDS]:
        pin = led_conf[CONF_PIN]
        opt_args = {}
        if CONF_FREQUENCY in led_conf:
            opt_args["frequency"] = led_conf[CONF_FREQUENCY]
        opt_args["pin_factory"] = PiGPIOFactory(
            host=led_conf[CONF_HOST], port=led_conf[CONF_PORT]
        )
        led = PwmSimpleLed(
            led=PWMLED(pin, **opt_args),
            name=led_conf[CONF_NAME],
            unique_id=led_conf[CONF_UNIQUE_ID],
            hass=hass,
        )
        leds.append(led)

    add_entities(leds)


# Transform the configEntry from config_flow into an entity
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light from the ConfigEntry configuration created in the integrations UI."""
    pin = config_entry.data.get(CONF_PIN)
    opt_args = {}
    opt_args["frequency"] = config_entry.data.get(CONF_FREQUENCY)
    opt_args["pin_factory"] = PiGPIOFactory(
        host=config_entry.data.get(CONF_HOST), port=config_entry.data.get(CONF_PORT)
    )
    entity1 = PwmSimpleLed(
        led=PWMLED(pin, **opt_args),
        hass=hass,
        config_entry=config_entry,
    )
    # Do not create entity if is not a light
    if CONF_LIGHT not in config_entry.title:
        pass
    else:
        async_add_entities([entity1], update_before_add=True)


class PwmSimpleLed(LightEntity, RestoreEntity):
    """Representation of a simple one-color PWM LED."""

    def __init__(self, **kwarg) -> None:
        """Initialize one-color PWM LED."""
        self._hass = kwarg["hass"]
        self._attr_has_entity_name = True
        self._led = kwarg["led"]
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
        self._brightness = DEFAULT_BRIGHTNESS

    async def async_added_to_hass(self):
        """Handle entity about to be added to hass event."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            self._is_on = last_state.state == STATE_ON
            self._brightness = last_state.attributes.get(
                "brightness", DEFAULT_BRIGHTNESS
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
    def brightness(self):
        """Return the brightness property."""
        return self._brightness

    @property
    def supported_color_modes(self):
        """Return the flag supported_color_modes property."""
        return {COLORMODE}

    @property
    def color_mode(self):
        """Return the color_mode property."""
        return COLORMODE

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_SIMPLE_LED

    def turn_on(self, **kwargs):
        """Turn on a led."""
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
        self._led.value = _from_hass_brightness(self._brightness)
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn off a LED."""
        if self.is_on:
            self._led.off()
        self._is_on = False
        self.schedule_update_ha_state()


def _from_hass_brightness(brightness):
    """Convert Home Assistant brightness units to percentage."""
    return brightness / 255

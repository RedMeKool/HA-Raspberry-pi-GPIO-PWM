"""The rpi_gpio_pwm constants."""

from homeassistant.const import Platform

CONF_FANS = "fans"
CONF_FAN = "fan"
CONF_FREQUENCY = "frequency"
CONF_LEDS = "leds"
CONF_LIGHT = "light"
CONF_PIN = "pin"


DEFAULT_BRIGHTNESS = 255
DEFAULT_FAN_PERCENTAGE = 100
DEFAULT_FREQUENCY = 100
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8888
DOMAIN = "rpi_gpio_pwm"


PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.LIGHT,
]

"""Config flow to configure rpi_gpio_pwm component."""

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PLATFORM,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_FAN,
    CONF_FREQUENCY,
    CONF_LIGHT,
    CONF_PIN,
    DEFAULT_FREQUENCY,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DOMAIN,
)

DATA_SCHEMA_ConfigFlowLight = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_PIN): cv.positive_int,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_FREQUENCY, default=DEFAULT_FREQUENCY): cv.positive_int,
    }
)

DATA_SCHEMA_ConfigFlowFan = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_PIN): cv.positive_int,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)


async def async_check_if_pin_is_used(hass: HomeAssistant, pin: int) -> str | None:
    """Check if pin is free or already use by rpi_gpio_pwm component."""

    # Load all already configured config_entries (in .storage/core.config_entries)
    config_entries_data = await hass.config_entries._store.async_load()

    # Create a list of pins already in use
    pin_list = []
    for i in config_entries_data:
        if i == "entries":
            for j in config_entries_data[i]:
                if j.get("domain") == DOMAIN:
                    for k in j:
                        if k == "data":
                            pin_list.extend([j[k].get(CONF_PIN)])

    # Return True if pin is free, else False
    if pin in pin_list:
        return False
    return True


class GPIOPWMConfigFlow(ConfigFlow, domain=DOMAIN):
    """Rpi_gpio_pwm Custom config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    # Define a dictionary for the information that will be entered
    # data: Optional[dict[str, Any]]

    async def async_step_user(self, user_input=None):
        """Invoke when a user initiates a flow via the user interface."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["light", "fan"],
        )

    async def async_step_light(self, user_input: dict | None = None) -> FlowResult:
        """Invoke when a user initiates a flow via the user interface."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Memorizes the information entered in user_input
            self.data = user_input
            # Stock platform in the user inputs data
            self.data[CONF_PLATFORM] = CONF_LIGHT

            # Check if selected pin is free
            pin_is_free = await async_check_if_pin_is_used(
                hass=self.hass, pin=self.data[CONF_PIN]
            )
            if pin_is_free is False:
                errors[CONF_PIN] = "pin_used"

            if not errors:
                # Create the entity
                return self.async_create_entry(
                    title="GPIO " + str(self.data[CONF_PIN]) + " PWM " + CONF_LIGHT,
                    data=self.data,
                )

        # Menu to display
        return self.async_show_form(
            step_id="light", data_schema=DATA_SCHEMA_ConfigFlowLight, errors=errors
        )

    async def async_step_fan(self, user_input: dict | None = None) -> FlowResult:
        """Invoke when a user initiates a flow via the user interface."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Memorizes the information entered in user_input
            self.data = user_input
            # Stock platform in the user inputs data
            self.data[CONF_PLATFORM] = CONF_FAN

            # Check if selected pin is free
            pin_is_free = await async_check_if_pin_is_used(
                hass=self.hass, pin=self.data[CONF_PIN]
            )
            if pin_is_free is False:
                errors[CONF_PIN] = "pin_used"

            if not errors:
                # Create the entity
                return self.async_create_entry(
                    title="GPIO " + str(self.data[CONF_PIN]) + " PWM " + CONF_FAN,
                    data=self.data,
                )

        # Menu to display
        return self.async_show_form(
            step_id="fan", data_schema=DATA_SCHEMA_ConfigFlowFan, errors=errors
        )

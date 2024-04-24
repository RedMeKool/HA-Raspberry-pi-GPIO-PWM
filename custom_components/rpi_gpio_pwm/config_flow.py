"""Config flow to configure rpi_gpio_pwm component."""

from collections.abc import Mapping
import copy
import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_PLATFORM,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er, selector
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

DATA_SCHEMA_OptionFlowLight = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENTITY_ID): selector.TextSelector(
            selector.TextSelectorConfig(
                prefix="light.", type=selector.TextSelectorType.TEXT
            )
        ),
        vol.Required(CONF_PIN): cv.positive_int,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_FREQUENCY, default=DEFAULT_FREQUENCY): cv.positive_int,
    }
)

DATA_SCHEMA_OptionFlowFan = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENTITY_ID): selector.TextSelector(
            selector.TextSelectorConfig(
                prefix="fan.", type=selector.TextSelectorType.TEXT
            )
        ),
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


async def async_get_entity_id_by_unique_id(
    hass: HomeAssistant, PlatForm: str, Unique_ID: str | None
) -> str | None:
    """Get OLD entity_id in case it need to change."""
    if Unique_ID is None:
        return None
    entity_registry = er.async_get(hass)
    return entity_registry.async_get_entity_id(
        domain=PlatForm, platform=DOMAIN, unique_id=Unique_ID
    )


async def update_entity_ID(
    hass: HomeAssistant, entity_id_OLD: str, entity_id_NEW: str
) -> None:
    """Update entity if change in Config Flow.."""
    entity_registry = er.async_get(hass)
    entity_registry.async_update_entity(
        entity_id=entity_id_OLD,
        new_entity_id=entity_id_NEW,
    )


def add_suggested_values_to_schema(
    data_schema: vol.Schema, suggested_values: Mapping[str, Any]
) -> vol.Schema:
    """Make a copy of the schema, populated with suggested values.

    For each schema marker matching items in `suggested_values`,
    the `suggested_value` will be set. The existing `suggested_value` will
    be left untouched if there is no matching item.
    """
    schema = {}
    for key, val in data_schema.schema.items():
        new_key = key
        if key in suggested_values and isinstance(key, vol.Marker):
            # Copy the marker to not modify the flow schema
            new_key = copy.copy(key)
            new_key.description = {"suggested_value": suggested_values[key]}
            if key == CONF_ENTITY_ID:
                sugg_values = str(suggested_values[key]).replace("light.", "", 1)
                suggested_val = sugg_values.replace("fan.", "", 1)
                new_key.description = {"suggested_value": suggested_val}
        schema[new_key] = val
    return vol.Schema(schema)


class GPIOPWMConfigFlow(ConfigFlow, domain=DOMAIN):
    """Rpi_gpio_pwm Custom config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

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

    # Declare optionFlow
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Get options flow for this handler."""
        return GPIOPWMOptionsFlow(config_entry)


class GPIOPWMOptionsFlow(OptionsFlow):
    """Rpi_gpio_pwm Custom Option flow to modify the configuration."""

    # To memorize the current config
    config_entry: ConfigEntry = None

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initializ the option flow. We have the existing ConfigEntry as input."""
        self.config_entry = config_entry
        # We initialize the data with the data from the configEntry
        self.data = config_entry.data.copy()

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Manage the options. Same option as configflow."""
        errors: dict[str, str] = {}

        # Stock OLD entity_id and add it to data for show it in config suggested_values in case it need to change
        if self.config_entry.data[CONF_PLATFORM] == CONF_LIGHT:
            PLATFORM = CONF_LIGHT
        elif self.config_entry.data[CONF_PLATFORM] == CONF_FAN:
            PLATFORM = CONF_FAN
        entity_id_old = await async_get_entity_id_by_unique_id(
            hass=self.hass,
            PlatForm=PLATFORM,
            Unique_ID=self.config_entry.entry_id,
        )
        self.data.update({CONF_ENTITY_ID: entity_id_old})

        # Stock OLD pin in case it don't change
        pin_old = self.config_entry.data.get(CONF_PIN)

        if user_input is not None:
            # Memorizes the information entered in user_input
            self.data.update(user_input)

            # Check if the pin changes and check if it is free if it is
            if pin_old != self.data[CONF_PIN]:
                pin_is_free = await async_check_if_pin_is_used(
                    hass=self.hass, pin=self.data[CONF_PIN]
                )
                if pin_is_free is False:
                    errors[CONF_PIN] = "pin_used"

            # Check format for Entity_ID
            if self.config_entry.data[CONF_PLATFORM] == CONF_LIGHT:
                if re.match(r"^[_A-Za-z0-9]+$", self.data[CONF_ENTITY_ID]) is None:
                    errors[CONF_ENTITY_ID] = "light_bad_EntityID_format"
                self.data[CONF_ENTITY_ID] = "light." + self.data[CONF_ENTITY_ID]
            elif self.config_entry.data[CONF_PLATFORM] == CONF_FAN:
                if re.match(r"^[_A-Za-z0-9]+$", self.data[CONF_ENTITY_ID]) is None:
                    errors[CONF_ENTITY_ID] = "fan_bad_EntityID_format"
                self.data[CONF_ENTITY_ID] = "fan." + self.data[CONF_ENTITY_ID]

            if not errors:
                # Update the entity
                if self.config_entry.data[CONF_PLATFORM] == CONF_LIGHT:
                    TITLE = "GPIO " + str(self.data[CONF_PIN]) + " PWM " + CONF_LIGHT
                elif self.config_entry.data[CONF_PLATFORM] == CONF_FAN:
                    TITLE = "GPIO " + str(self.data[CONF_PIN]) + " PWM " + CONF_FAN
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    title=TITLE,
                    data=self.data,
                )
                # Reload the entry
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)

                # Updates the entity_id if it changes
                if entity_id_old != self.data[CONF_ENTITY_ID]:
                    await update_entity_ID(
                        hass=self.hass,
                        entity_id_OLD=entity_id_old,
                        entity_id_NEW=self.data[CONF_ENTITY_ID],
                    )
                    await self.notify_update_entity_id(
                        entity_id_OLD=entity_id_old,
                        entity_id_NEW=self.data[CONF_ENTITY_ID],
                    )
                    # We do nothing in the options object in the configEntry
                    return self.async_create_entry(title=None, data=None)

                # We do nothing in the options object in the configEntry
                return self.async_create_entry(title=None, data=None)

        # Menu to display
        if self.data[CONF_PLATFORM] == CONF_LIGHT:
            return self.async_show_form(
                step_id="init",
                data_schema=add_suggested_values_to_schema(
                    data_schema=DATA_SCHEMA_OptionFlowLight,
                    suggested_values=self.data,
                ),
                errors=errors,
            )
        elif self.data[CONF_PLATFORM] == CONF_FAN:
            return self.async_show_form(
                step_id="init",
                data_schema=add_suggested_values_to_schema(
                    data_schema=DATA_SCHEMA_OptionFlowFan,
                    suggested_values=self.data,
                ),
                errors=errors,
            )

    async def notify_update_entity_id(
        self, entity_id_OLD: str, entity_id_NEW: str
    ) -> None:
        """Call a SERVICE for update entity if change in Config Flow."""
        self.config_entry.async_create_task(
            hass=self.hass,
            target=self.hass.services.async_call(
                domain="notify",
                service="persistent_notification",
                service_data={
                    "message": f"The entity_id has been changed {entity_id_OLD} --> {entity_id_NEW}"
                },
                target={},
                blocking=True,
            ),
        )

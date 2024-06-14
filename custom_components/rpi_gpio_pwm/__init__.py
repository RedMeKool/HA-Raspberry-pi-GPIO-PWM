"""The rpi_gpio_pwm component."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, PLATFORMS_FAN, PLATFORMS_LIGHT


# Transform the configEntry from config_flow into an entity
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up entity from a ConfigEntry."""

    # Sets the default domain to be our domain
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)

    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener

    hass.data[DOMAIN][entry.entry_id] = hass_data

    # Propagates the configEntry to all platforms declared in the integration
    # This creates each HA object for each platform your device requires.
    if hass_data["platform"] == "fan":
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_FAN)
    if hass_data["platform"] == "light":
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_LIGHT)

    return True


async def options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Remove config entry from domain.
        entry_data = hass.data[DOMAIN].pop(entry.entry_id)
        # Remove options_update_listener.
        entry_data["unsub_options_update_listener"]()

    return unload_ok

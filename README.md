# Home Assistant Raspberry Pi GPIO PWM custom integration

**This is a spin-off from the original Home Assistant integration which was marked as deprecated and will be removed in Home Assistant Core 2022.4.**

The rpi_gpio_pwm platform allows to control multiple lights using pulse-width modulation, for example LED strips. It supports one-color LEDs driven by GPIOs of a Raspberry Pi (same host or remote)
For controlling the GPIOs, the platform connects to the pigpio-daemon (http://abyz.me.uk/rpi/pigpio/pigpiod.html), which must be running. On Raspbian Jessie 2016-05-10 or newer the pigpio library is already included. On other operating systems it needs to be installed first (see installation instructions: https://github.com/soldag/python-pwmled#installation).

For Home Assistant this daemon can be installed as an add-on (https://github.com/Poeschl/Hassio-Addons/tree/master/pigpio).

# Installation

### HACS

The recommend way to install `ha-rpi_gpio_pwm` is through [HACS](https://hacs.xyz/).

### Manual installation

Copy the `ha-rpi_gpio_pwm` folder and all of its contents into your Home Assistant's `custom_components` folder. This folder is usually inside your `/config` folder. If you are running Hass.io, use SAMBA to copy the folder over. You may need to create the `custom_components` folder and then copy the `ha-rpi_gpio_pwm` folder and all of its contents into it.

# Configuration
To enable this platform, add the following lines to your configuration.yaml:

```yaml
# Example configuration.yaml entry
light:
  - platform: rpi_gpio_pwm
    leds:
      - name: Lightstrip Cupboard
        unique_id: thisismyuniqueid
        pin: 17
```
# CONFIGURATION VARIABLES
- **leds** list *(REQUIRED)*: Can contain multiple LEDs.

- **name** string *(REQUIRED)*: The name of the LED.

- **unique_id** string *(optional)*: An ID that uniquely identifies this LED. Set this to a unique value to allow customization through the UI.

- **pin** integer *(REQUIRED)*: The pin connected to the LED as a list.

- **frequency** integer *(optional, default: 100)*: The PWM frequency.

- **host** string *(optional, default: localhost)*: The remote host address for the GPIO driver.

- **port** integer *(optional, default: 8888)*: The port on which the GPIO driver is listening.


# Home Assistant Raspberry Pi GPIO PWM custom integration

**This is a spin-off from the original Home Assistant integration which was marked as deprecated and will be removed in Home Assistant Core 2022.4.**

The rpi_gpio_pwm platform allows to control multiple lights using pulse-width modulation, for example LED strips. It supports one-color, RGB and RGBW LEDs driven by GPIOs of a Raspberry Pi (same host or remote) or a PCA9685 controller.

For controlling the GPIOs, the platform connects to the pigpio-daemon (http://abyz.me.uk/rpi/pigpio/pigpiod.html), which must be running. On Raspbian Jessie 2016-05-10 or newer the pigpio library is already included. On other operating systems it needs to be installed first (see installation instructions: https://github.com/soldag/python-pwmled#installation).

# Installation

### HACS

The recommend way to install `ha-rpi_gpio_pwm` is through [HACS](https://hacs.xyz/).

### Manual installation

Copy the `ha-rpi_gpio_pwm` folder and all of its contents into your Home Assistant's `custom_components` folder. This folder is usually inside your `/config` folder. If you are running Hass.io, use SAMBA to copy the folder over. You may need to create the `custom_components` folder and then copy the `rpi_gpio` folder and all of its contents into it.

# Configuration
To enable this platform, add the following lines to your configuration.yaml:

```yaml
# Example configuration.yaml entry
light:
  - platform: rpi_gpio_pwm
    leds:
      - name: Lightstrip Cupboard
        driver: gpio
        pins: [17]
        type: simple
```
# CONFIGURATION VARIABLES
leds list REQUIRED
Can contain multiple LEDs.

name string REQUIRED
The name of the LED.

    driver string REQUIRED
    The driver which controls the LED. Choose either gpio or pca9685.

    pins list | integer REQUIRED
    The pins connected to the LED as a list. The order of pins is determined by the specified type.

    type string REQUIRED
    The type of LED. Choose either rgb, rgbw or simple.

    frequency integer (optional, default: 200)
    The PWM frequency.

    address string (optional, default: 64)
    The address of the PCA9685 driver.

    host string (optional)
    The remote host address for the GPIO driver.

# Examples
In this section you find some real-life examples of how to use this sensor.

RGB LED CONNECTED TO PCA9685 CONTROLLER
This example uses a PCA9685 controller (https://www.nxp.com/products/interfaces/ic-bus-portfolio/ic-led-display-control/16-channel-12-bit-pwm-fm-plus-ic-bus-led-controller:PCA9685) to control a RGB LED.

```yaml
# Example configuration.yaml entry
light:
  - platform: rpi_gpio_pwm
    leds:
      - name: TV Backlight
        driver: pca9685
        pins: [0, 1, 2] # [R, G, B]
        type: rgb
```

RGBW LED CONNECTED TO PCA9685 CONTROLLER
This example uses a PCA9685 controller (https://www.nxp.com/products/interfaces/ic-bus-portfolio/ic-led-display-control/16-channel-12-bit-pwm-fm-plus-ic-bus-led-controller:PCA9685) to interact with a RGBW LED.

```yaml
# Example configuration.yaml entry
light:
  - platform: rpi_gpio_pwm
    leds:
      - name: Lightstrip Desk
        driver: pca9685
        pins: [3, 4, 5, 6] # [R, G, B, W]
        type: rgbw
```

RGB LED CONNECTED TO THE GPIO PINS OF A REMOTE RASPBERRY PI.
On the Raspberry Pi the pigpio daemon is running on the default port 6666.

```yaml
# Example configuration.yaml entry
light:
  - platform: rpi_gpio_pwm
    leds:
      - name: Lightstrip Sideboard
        driver: gpio
        host: 192.168.0.66
```

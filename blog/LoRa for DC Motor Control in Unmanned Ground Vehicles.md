
- Brushless DC motor
- ESC and ESP32
- internal LED_PWM
- Traxxas TQ 2.4GHz Radio system
[ESP32 with LoRa using Arduino IDE | Random Nerd Tutorials](https://randomnerdtutorials.com/esp32-lora-rfm95-transceiver-arduino-ide/)

- Technical write up
- Discuss pros and cons of current frequency vs 915 MHz
- Discuss implementation
- Test

## Electronic Speed Controller
The ESC is an electronic circuit that controls the speed of an electric motor by varying the switching rate of a network of field transistors (FETs). Adjusting the switching frequency adjusts the motor speed.![[Pasted image 20260219141608.jpg]]

To control the electronic speed controller, we need to use a PWM. Any GPIO pin will do.

[WiFi LoRa 32(V3), ESP32S3 + SX1262 LoRa Node](https://heltec.org/project/wifi-lora-32-v3/)

## LoRa
- Arduino LoRa library
- SX1262

## Friis Transmission Equation

$$P_r = P_t G_t G_r \left( \frac{c}{4 \pi d f} \right)^2$$

## Free-Space Path Loss
$$FSPL (dB) = 20 \log_{10}(d) + 20 \log_{10}(f) + 20 \log_{10}\left( \frac{4\pi}{c} \right)$$

## Wavelength
$$\lambda = \frac{c}{f}$$

## Knife-Edge Diffraction
$$v = h \sqrt{\frac{2}{\lambda} \left( \frac{1}{d_1} + \frac{1}{d_2} \right)}$$
## Two-Ray Ground Reflection Model
$$P_r = P_t G_t G_r \frac{h_t^2 h_r^2}{d^4}$$

## PWM on ESP32
`analogWrite(int pin, int value)` writes an analog value as a PWM wave to a pin, for LEDs or motors. Continues wave until next action on the pin.

Resolution and frequency of a PWM signal can be set with `analogWriteResolution` and `analogWriteFrequency`. 

However, LEDC allows for higher resolution PWM of up to 16-bit compared to analogWrite's 8-bit.
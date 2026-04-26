
## 9/30/2025 - 10/02/2025: Non-planar slicer setup and bug fixes
- Configure S4_Slicer compatibility for Windows via versioning correction and editing Jupyter pip install process.
- Fixed floating point error for large polygon models with divide by floating point check.
- Automated S4_Slicer configuration and install with Python script.
## 10/06 - 10/9: Firmware installation and configuration
- Established firmware connection via COM serial over USB-C to Duet3D.
- Established server connection and web console through ethernet.
- Configured default `config.g` from Fly E3 to Duet3D by translating pinouts.
- Set up basic calibration and homing for C and X axis. Ran motors through G and M codes.

## 10/21: Firmware Bug Found
- A networking bug is present in the Duet3D Mini 5+:
	```
	M552
		Ethernet is enabled, configured IP address: 192.168.2.1, actual IP address: 0.0.0.0
	```
	The firmware reads IP configurations but does not apply them. Other instances [here](https://forum.duet3d.com/topic/38652/duet-3-mini-5-ethernet-unable-to-get-set-ip-address/17) and [here](https://forum.duet3d.com/topic/24078/cannot-connect-to-duet-3-web-control/69). No solutions are available, besides contacting customer support. 
	One possible fix is to use a Raspberry Pi over GPIO to bypass Duet's default networking. This would also give us access to more peripherals.

## 10/22: Setting up Raspberry Pi
[Single Board Computer (SBC) setup for Duet 3 | Duet3D Documentation](https://docs.duet3d.com/User_manual/Machine_configuration/SBC_setup)

- Set up Pi 4 using documentation. Currently fixed to one hotspot, next step is to set up an additional `wlan1` and create an access point.

## 10/23 First Homing Test
- Configured all axis
- Translated Z pin outs from E3 Fly to Duet3D
- Soldered makeshift Z-probe switch to `io1.in` pin.
- Reversed Z axis stepper motor direction to correct flipped axis. `M569 P4 S1`, per documentation, `Sx` parameter sets direction through current.
- First homing test: [Core Theta: Homing Test 1](https://www.youtube.com/shorts/WjAxdWwizyg)
- Issue: Extruder shifts orientation and misdirects the Z-probe.

## 11/7: Testing motherboard failure
### Voltage Test (Pi disconnected)
#### Expansion Header
- SFI0_SS - 3.3v
- SBC DATA_READY - ~1.6v
- SPI0 MISO - ~1.7v
- All other pins, 0

#### MCU
- all caps, resistors, and even some MCU pins are reading 3.3v

#### Reset Button
- 3.3v on, 0v off, working

### Resistance Test
#### Expansion Header
- DATA_READY -> GND ~3 Mohms
- 3V3 -> GND 0.L Mohms
- SPI0_MISO -> GND alternates between 0.L and some arbitrary Mohms

Duet3D documentation suggests double-clicking reset button to erase firmware. However, this does nothing and no changes are made in the device manager. Possibly a dead MCU. Bootloader never loads and runs STATUS led or GPIO pins

## 11/11: Configuration Updates and Extruder Test

- X calibration disorients B as extruder collides in endstop test. B now homes after X to avoid this.
- Extruding and retracting are functional. Requires inverting extruder motor in the config for some reason. I don't feel like investigating further.

## 11/12: First Print
- Molded CNC'd extruder mount print to bearing with hot glue. Extruder heat doesn't seem to affect it so it's a good temporary solution.
- Nozzle doesn't have enough clearance, need a longer "airbrush" kind of nozzle. Current one collides with print.
- First print test here: https://youtube.com/shorts/j4A8j0xGAxw?feature=share


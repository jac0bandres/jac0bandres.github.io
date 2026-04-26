I'm building my own ESP32-C3 Board.

#### Voltage Regulator: TPS62A01DRLR
DC-DC step-down switching voltage regulator, often called a buck converter. Buck converters convert higher input voltage to lower output voltage for components, with higher efficiency than a simple linear regulator.

This one accepts 2.5 V to 5.5 V and steps it down to a lower, adjustable voltage using external resistors. It can deliver up to 1 A output current. It uses high-frequency switching of around 2.4 MHz to regulate output efficiently. You set the exact output with a resistor divider. Features include overcurrent protection, thermal shutdown, and soft-start.

#### Charger IC: BQ21040
Battery charger that can charge 1 Li-Ion batter to 4.2 V. Programmable charge current using a resistor up to 0.8 A, so we can pick how much current the battery gets. Can handle up to 30 V from the adapter side, with overvoltage protection of 6.6 V. Has internal thermal regulation and shutdown to prevent overheating. 

The charger follows three phase charge profile:
1. Pre-charge/conditioning - low current when batter is low
2. Constant current - speeds up near full
3. Constant voltage - slows down as it nears 100% charge.

It has a CHG pin output to drive an LED or microcontroller input.

#### Power Mux: LM66200
Dual ideal diode controller with automatic switchover, to intelligently connect the highest of two input voltages to a single output using MOSFETs instead of regular diodes. Making it ideal for powerpath management in systems with multiple power sources like SB and battery. Works from typical low-voltage sources like Li-ion batters up to USB voltages. Reverse current boking. Thermal shutdown.

Conventional diodes drop voltage. The LM66200 automatically connects higher voltage input to the output with minimal loss, blocks current from flowing backward, and smooths output voltage rise, reducing strain on capacitors and loads. Ideal for power sharing and switchover in systems powered by USB and batteries. Great for battery powered electronics that also have external power available.

#### ESD Diode
Also called a TVS diode, it protects sensitive electronic circuits from high-voltage electrostatic discharge (ESD) and electrical surges.

#### RC soft-start
The ESP32-C3-Mini-1 has an enable pin. Rather than driving the pin directly from 3.3 V directly through a switch, an RC network can be used to give a controlled start up and reset behavior.

You place a resistor in series between the 3.3V rail the EN pin, then from the EN node to ground, a capacitor and a switch are connected in parallel. This forms the RC delay network.

If the switch is off (open), electricity flows to ground through the resistor and the capacitor. The capacitor's electric field begins to fill, and will block DC once full, and the MCU sits at VCC. This controlled rise prevents unwanted behavior like brown-out oscillations during power-up.

Once the switch is on (closed), electricity immediately flows to ground. The capacitor discharges and the MCU snaps to low.

![[Pasted image 20260208174821.png]]
$τ=R⋅C=10,000⋅1×10−6=0.01 s=10 ms$

## UGV - UNG Spring 2026
### Intro
Spring semester is about to start. My team and I are creating an Unmanned Ground Vehicle system. As the electrical engineer, it's my job to design the PCB for the system.

#### Brainstorm
##### Battery
6s Li-ion, nominal voltage 22.2V, fully charged 25.2. 
##### Motor
For our 1/10 crawler motor, I need a stall current of about **30-60 A** per motor. Battery inputs a have to be rated **=> 120 A** peak. 

##### Motor Controllers
I'm looking at using PWM control. Maybe 3.3V logic.

##### Comms/control
PWM for the motors, UART for telemetry. Simple.

##### Autonomy
The guild president still hasn't given us the objectives. I'm assuming outdoor and teleop like last years UGV project. This introduces EMI from motors and long wires. I'll need a TVS diode on battery input, electrolytic near ESC, and LC filtering on logic rails.
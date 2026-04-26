# Episode 1
## Bandpass Filters, Q, Matching Networks

### How does a radio work?
You start with a high frequency sine wave voltage source. It puts positive charges onto an antenna element on top and negative on the bottom, creating an electric field from top to bottom. Voltage changes and charges move in and out of wires creating currents that create magnetic fields around the wire. The magnetic fields regenerate themselves and propagate away from the source. A receiver receives the magnetic fields and pulls the electron on it's wire causing current to flow through and creating a voltage that needs to be amplified.

Signal, noise, and interferers are received, but bandpass filters are required to isolate the signal. Usually created by inductors and capacitors.

### Impedances, Ohm's Law, and Voltage Dividers
More impedance to the flow of current means less current:
$I=\frac{V}{Z}$

$V=IZ$

$Z$ is impedance. 
A resistor has an impedances constant with frequency. But a real resistor at high frequencies becomes a resistor in series with an inductor.
An inductor has an impedance: $Z=j2\pi fL$. The impedance goes up with frequency.
In a capacitor, the impedance goes down with frequency: $Z=-j\frac{1}{2 \pi fC}$

### Voltage Divider
$$I=\frac{V_s}{Z_1 + Z_2}$$
$$V_0=IZ_2$$
$$V_0=V_s [\frac{Z_2}{Z_1 + Z_2}]$$
Useful for filters. $Z$ can be a set of components. 

### 1-pole Filters (Lowpass and Bandpass)
#### 1-Pole Lowpass
$$V_0=V_s [\frac{Z_R}{Z_1 + Z_C}]$$
![[Pasted image 20260209192133.png]]
![[Pasted image 20260209192108.png]]

#### 1-Pole Bandpass
$$V_0=V_s [\frac{Z_{LC}}{Z_R + Z_{LC}}]$$
![[Pasted image 20260209191645.png]]
![[Pasted image 20260209191716.png]]

### Q
Q is the quality factor, a key RF design parameter of resonant-circuits, filters, matching networks, or underlying reactive components like L and C.

It sets the bandwidth, affects power and insertion loss, and is used in designing filters and matching networks. 

#### Parallel Resonant Circuit Q
How do we pick L and C for the desired centered frequency $f_0$ and Bandwidth B?

$f_0=\frac{1}{2 \pi \sqrt{LC}}$, $X_0=2 \pi F_0 L$, $X=\frac{1}{2 \pi f_0 C}$
$Q = \frac{R_p}{X_0}$, $B=\frac{f_0}{Q}$

If you have three things in parallel, the smallest impedance wins, except in RLC the L and C have a feature when reactance are equal, the reactance of the L and C in parallel goes to infinity, and we are just left with R. Quality is given by resistance divided by reactance of a circuit. Bandwidth is center frequency divided by Q.

#### Parallel vs Series Resonators
In a parallel LC circuit, impedance of at low frequency drops to zero because L impedance goes towards 0 and shorts at L. At high frequency, C shorts out and the impedance goes to zero as frequency goes to infinity. Q is then: $Q = \frac{R_0}{X_0}$

In a series LC circuit, impedance goes towards the resistor at the center frequency as L and C impedance cancels. Q is then: $Q=\frac{X_0}{R_s}$.

In bandpass filter design we want a high Q for a narrow bandwidth. In parallel LC, it requires a high resistor, in series it requires a smaller resistor, due to the equations.

#### Some observations
Here is a resonant LC series circuit.
![[Pasted image 20260210093454.png]]
![[Pasted image 20260210093539.png]]
Center resonant frequency is $$F_0=\frac{1}{2 \pi \sqrt{LC}}$$ $$\frac{1}{2 \pi sqrt{(10*10^{-6}F)(100*10^{-3}H)}} = 159.15 Hz$$
This can be confirmed with the graph. The resonance is at 159.15 Hz, very cool. Now we remember that we want a large Q, so $Q=\frac{X}{R}$, we will need a smaller R. This should give us a narrower filter. Lowering R to 100 $\Omega$ fives us exactly that.

![[Pasted image 20260210094541.png]]
### Filter Design
#### Preselector
A preselector is a bandpass filter that sits between the antenna and receiver an "preselects"  frequencies as to let only desired ones through.

Start with a desired center frequency and bandwidth. Let's say my radio should only receive frequencies at around 100 Mhz and a bandwidth of 17 Mhz. By $Q=\frac{f_0}{B} \rightarrow \frac{100}{17} = 6$.
We need a quality factor of 6. Using $Q=\frac{R}{X}$ we solve for X by selecting a resistor of 25 $\Omega$. Our impedance should be 4.2. Using inductor and capacitor impedance equations: $X_0=2 \pi F_0 L$, $X_0=\frac{1}{2 \pi f_0 C}$, We find we need 6.7 nH and 380 pF.  
I'm going to use two resistors in parallel, and by parallel resistor equation $$\frac{1}{R_{\text{total}} = \frac{1}{R_1} + \frac{1}{R_2}...}$$
I'll just get back 25 $\Omega$.

![[Pasted image 20260210100618.png]]
![[Pasted image 20260210100923.png]]

### Parasitics
However, on a NanoVNA with a real board instead of Spice, we have a different result:
![[Pasted image 20260210101016.png]]
We have an in-band insertion loss of almost 4 dB and our bandwidth is wider than 17 Mhz (almost 22). This has to do with component parasitics. Ideal components have no parasitics and behave perfectly with the equation. However, the inductor and capacitor have some resistance, and the inductor has some capacitance, which throw things off.

If we can calculate the individual Q of the inductor after measuring it's impedance with a NanoVNA and get 41 $\Omega$ for the inductor. Now we have a parallel resistance to our already existing resistors. The solution is to use an inductor with much higher parallel resistance, meaning a lower series resistance.

![[Pasted image 20260210103304.png]]
The capacitor also has some parasitic properties. Looking at a higher frequency range of 50kHz to 500 MHz, we see the response increase. The capacitor also has resistance, but especially has a certain length to it that also creates inductance. A solution is to use smaller components.

### Transmission Lines
A perfect wire would carry signal throughout itself without any voltage drop and impedance. However, this is not the case. In reality, there is a voltage drop from one end to the other caused by the impedance and delay in sending the signal. The amount of time it takes for the signal to travel is called transit time. Transit time results in the difference between two points on a line. We can minimize the voltage drop by decreasing the wave frequency. Essentially, the length of wire between two points must be small compared to the wavelength. If we divide the wire into smaller segments, we can analyze it using lower frequency rules like Kirchoff's Laws and the transit time effect would be negligible over each section. A transmission line is path carrying electrical energy from source to load. 

A transmission line has the characteristics of inductors in series, as well as capacitors in parallel. We can model this behavior using a circuit.
### Impedance Matching
A receiver is receiving multiple thing: signals, interferers, and noise ($P_r, P_i, P_n$). We need to receive power $P_r$ greater than noise poewr $P_n$.
$$P_r=[\frac{Pt}{4 \pi R^2}Gt]Ae$$
$$P_n=kTB$$

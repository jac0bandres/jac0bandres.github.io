### 01/27
Because of the snow in, I decided to write a simulation plotting Core Theta space vector to 3D space vector, essentially reversing the process of the S4_Slicer.

#### Solution 1: Vector arithmetic
Even though C rotates relative to the printer, rotating the printer relative to C also holds true. Otherwise, I'd have to replot all points in matplotlib to a C rotation which is too expensive.

Given Core R theta vector $\begin{pmatrix} x \\ z \\ c \\ b \end{pmatrix}$

$\theta=c\frac{180}{\pi}$, $\phi = b\frac{180}{\pi}$
$C = <cos(\theta),sin(\theta),0>$

$Z=<0,0,z>$
$$\overrightarrow{OX}=50\overrightarrow{OC} + \overrightarrow{CZ} - (50-x)\overrightarrow{C}$$
This only brought me up to the X and B joint, and at this point the computation was too expensive. Mapping the $\overrightarrow{XB}$ vector was even more difficult. All attempts just gave a buggy simulation and some asymptotic behavior from some bad trig.
![C:\Users\jacob\OneDrive\Documents\Research\Core-R-Theta\thetasim\test.gif](file:///c%3A/Users/jacob/OneDrive/Documents/Research/Core-R-Theta/thetasim/test.gif)

#### Solution 2: Cylindrical Coordinates
Another approach would be to define cylindrical coordinates instead. The machine kinematics properly translates $x$ from the origin without the need for an offset. I was applying an offset to $x$ by $c$'s domain, which was unnecessary if $x$ has already been defined. All axis respect the absolute position defined by `G90`. $x,c,z$ are literally just cylindrical coordinates, and the $\overrightarrow{XB}$ would be defined as a scalar on $x$ and $z$ subtracted by $b$. This gives a concise vector.
$\begin{pmatrix} x & z & c & b \end{pmatrix},$ $\lVert b \rVert = 5$
$\theta=c\frac{180}{\pi}$, $\phi = b\frac{180}{\pi}$
$X = (x-\lVert b \rVert cos(\phi))cos(\theta))$
$Y = (x-\lVert b \rVert cos(\phi))sin(\theta))$
$Z = z + \lVert b \rVert sin(\phi)$

This gave a a proper plot of all points for the `bridge.gcode` test file. Ignoring additional points from movement operations, you can see the tool paths in the most condensed points.

![[Figure_1.png]]

### True Non-Planar Slicing
Trying to replot $x,y,z$ from Core Theta space highlighted an interesting issue. The S4_Slicer is not true non-planar slicing. It's really just a mesh deformation/reformation process that uses a planar slicer in between. This means it won't properly map toolpaths for uniform meshes or meshes with no overhangs.
![C:\Users\jacob\OneDrive\Documents\Research\Core-R-Theta\S4_Slicer\gifs\Quarter Circle V2_optimize_rotations.gif](file:///c%3A/Users/jacob/OneDrive/Documents/Research/Core-R-Theta/S4_Slicer/gifs/Quarter%20Circle%20V2_optimize_rotations.gif)
![C:\Users\jacob\OneDrive\Documents\Research\Core-R-Theta\S4_Slicer\gifs\test_cube_optimize_rotations.gif](file:///c%3A/Users/jacob/OneDrive/Documents/Research/Core-R-Theta/S4_Slicer/gifs/test_cube_optimize_rotations.gif)

Here are two optimization visuals for a flat quarter circle piece with no overhangs, and a uniform cube shape. The quarter circle compiles into a planar slice, and the cube never compiles. The S4_Slicer is really only built for overhangs.

What if we could define non-planar slices regardless of the models geometry?

### 02/01
### True Non-Planar Slicing

![[Figure_1 1.png]]![[Figure_1 2.png]]
These slice inclines are too steep to print realistically.

### 02/12/26 Correcting Extrusion
The slicer tends to over-extrude at small movements. This causes plastic to accumulate in certain areas disproportionally. It could have something to do with the "z-squishing" feature of the slicer.

```
G01 C1180.93516 X10.06149 Z-0.31787 B-8.92487 E3.1824 F6421.1136
G01 C1174.17974 X9.88053 Z-0.32129 B-8.93028 E0.3979 F4664.6652
```

Changing scaling extrusions don't provide much of a solution since extrusions are still disproportional to each other.

We found the ideal extrusion would be 0.33 mm of material per 1 mm of travel. The distances can be used from a Cartesian transformation of the polar coordinates like earlier.
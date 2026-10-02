"""Matplotlib-generated grid for a continuous Möbius inversion family.

The mapping is

    f_theta(z) = (cos(theta) z + i sin(theta)) /
                 (i sin(theta) z + cos(theta))

with theta = inversion * pi/2. At inversion=0 it is the identity and at
inversion=1 it is 1/z. The card uses the same 10% maximum state as the website.
"""

from pathlib import Path
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-card-cache")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _rdp(points, epsilon):
    """Ramer-Douglas-Peucker simplification in millimetres."""
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    chord = end - start
    length = np.linalg.norm(chord)
    if length == 0:
        distances = np.linalg.norm(points - start, axis=1)
    else:
        distances = np.abs(np.cross(chord, points - start) / length)
    index = int(np.argmax(distances))
    if distances[index] <= epsilon:
        return np.array([start, end])
    left = _rdp(points[: index + 1], epsilon)
    right = _rdp(points[index:], epsilon)
    return np.vstack((left[:-1], right))


def _length(points):
    return float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum())


def mobius_pole_paths(width=85.6, height=54.0, inversion=.10,
                      overscan_ratio=.36):
    """Return the transformed Cartesian grid at a fixed inversion amount."""
    xs = np.linspace(-width / 2 - 0.8, width / 2 + 0.8, 720)
    ys = np.linspace(-height / 2 - 0.8, height / 2 + 0.8, 480)
    x, y = np.meshgrid(xs, ys)
    theta = inversion * np.pi / 2
    cosine, sine = np.cos(theta), np.sin(theta)
    base_scale = min(width, height)
    scale = base_scale * (.075 * (1 - inversion) + .82 * inversion)
    # Rotate the output plane 90° and translate it so f_theta(∞), together with
    # the empty lobe around it, sits beyond the right edge. The curved approach
    # remains visible without exposing the singularity gap on the printed face.
    convergence_overscan = height * overscan_ratio
    origin_x = width / 2 + convergence_overscan - scale / np.tan(theta)
    mapped_real = y / scale
    mapped_imaginary = -(x - origin_x) / scale

    # Invert f_theta so contours of the recovered source coordinates are the
    # forward image of a regular Cartesian grid under the Möbius map.
    numerator_real = cosine * mapped_real
    numerator_imaginary = cosine * mapped_imaginary - sine
    denominator_real = cosine + sine * mapped_imaginary
    denominator_imaginary = -sine * mapped_real
    denominator = denominator_real ** 2 + denominator_imaginary ** 2
    source_real = (
        numerator_real * denominator_real
        + numerator_imaginary * denominator_imaginary
    ) / denominator
    source_imaginary = (
        numerator_imaginary * denominator_real
        - numerator_real * denominator_imaginary
    ) / denominator
    # Keep a uniform Cartesian source grid, but use a printable pitch: near the
    # right-edge convergence point, denser contours would merge into a solid
    # cut even though the underlying map is perfectly continuous.
    levels = np.arange(-18.0, 18.001, 1.24)

    figure, axis = plt.subplots()
    real_contours = axis.contour(x, y, source_real, levels=levels)
    imag_contours = axis.contour(x, y, source_imaginary, levels=levels)
    paths = []
    for family, contour_set in (("real", real_contours), ("imag", imag_contours)):
        for level, segments in zip(contour_set.levels, contour_set.allsegs):
            for segment in segments:
                if len(segment) >= 2 and _length(segment) >= 2.0:
                    simplified = _rdp(np.asarray(segment), .055)
                    paths.append({"family": family, "level": float(level), "points": simplified})
    plt.close(figure)
    return paths


def save_diagnostic(filename, paths, width=85.6, height=54.0,
                    inversion=.10):
    """Save the exact contour paths used by the 3D generator."""
    figure, axis = plt.subplots(figsize=(12, 7.6), dpi=150)
    figure.patch.set_facecolor("#090b0b")
    axis.set_facecolor("#090b0b")
    for path in paths:
        points = path["points"]
        color = "#d9dcd4" if path["family"] == "real" else "#9eb788"
        axis.plot(points[:, 0], points[:, 1], color=color, linewidth=.75, alpha=.88)
    axis.set_xlim(-width / 2, width / 2)
    axis.set_ylim(-height / 2, height / 2)
    axis.set_aspect("equal")
    axis.set_xlabel("Re(z) / mm", color="#929a95")
    axis.set_ylabel("Im(z) / mm", color="#929a95")
    axis.set_title(
        rf"Möbius grid: $f_\theta(z)=(\cos\theta\,z+i\sin\theta)/(i\sin\theta\,z+\cos\theta)$, inversion={inversion:.0%}",
        color="#d9dcd4",
    )
    axis.tick_params(colors="#929a95")
    for spine in axis.spines.values():
        spine.set_color("#38413f")
    figure.tight_layout()
    figure.savefig(Path(filename), facecolor=figure.get_facecolor())
    plt.close(figure)

from __future__ import annotations

import io
from typing import List, Sequence, Tuple

import numpy as np
from PIL import Image
import matplotlib
import matplotlib.cm as cm


def rgba_png_from_grid(values: np.ndarray, vmin: float | None = None, vmax: float | None = None, colormap: str = "viridis", alpha: float = 0.7) -> bytes:
	matplotlib.use("Agg")
	arr = values.copy()
	mask = np.isnan(arr)
	if vmin is None:
		vmin = np.nanpercentile(arr, 5) if np.isfinite(arr).any() else 0.0
	if vmax is None:
		vmax = np.nanpercentile(arr, 95) if np.isfinite(arr).any() else 1.0
	if vmin == vmax:
		vmax = vmin + 1e-6

	norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
	cmap = cm.get_cmap(colormap)
	rgba = cmap(norm(arr))  # (H,W,4)
	rgba[..., 3] = alpha
	rgba[mask, 3] = 0.0
	img = (rgba * 255).astype(np.uint8)
	im = Image.fromarray(img, mode="RGBA")
	buf = io.BytesIO()
	im.save(buf, format="PNG", optimize=True)
	return buf.getvalue()


def legend_breakpoints(values: np.ndarray) -> List[Tuple[str, float]]:
	finite = values[np.isfinite(values)]
	if finite.size == 0:
		return [("min", 0.0), ("p5", 0.0), ("p95", 0.0), ("max", 0.0)]
	return [
		("min", float(np.min(finite))),
		("p5", float(np.percentile(finite, 5))),
		("p95", float(np.percentile(finite, 95))),
		("max", float(np.max(finite))),
	]


__all__ = ["rgba_png_from_grid", "legend_breakpoints"]

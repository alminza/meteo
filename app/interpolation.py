from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

from .geo import haversine_km, mask_outside_circle
from .models import InterpolationSpec
from . import get_logger


logger = get_logger(__name__)


def _select_neighbors(
		points: np.ndarray,
		query_lat: np.ndarray,
		query_lon: np.ndarray,
		radius_km: Optional[float],
		k_neighbors: Optional[int],
) -> Tuple[np.ndarray, np.ndarray]:
	# points: (P,3) lat,lon,val
	lat_p = points[:, 0]
	lon_p = points[:, 1]
	val_p = points[:, 2]

	# Flatten query grid for vectorized computation
	qlat_flat = query_lat.ravel()
	qlon_flat = query_lon.ravel()
	Q = qlat_flat.shape[0]
	P = lat_p.shape[0]

	# Compute distances (Q,P) in blocks to limit memory
	block = max(1, 20000 // max(1, P))
	dist_list = []
	for i in range(0, Q, block):
		end = min(Q, i + block)
		qlat_b = qlat_flat[i:end]
		qlon_b = qlon_flat[i:end]
		d_b = np.array([
			[ haversine_km(qlat_b[j], qlon_b[j], lat_p[k], lon_p[k]) for k in range(P) ]
			for j in range(end - i)
		], dtype=float)
		dist_list.append(d_b)
	dists = np.vstack(dist_list)

	# neighbor selection mask
	if radius_km is not None:
		mask = dists <= radius_km
	else:
		mask = np.ones_like(dists, dtype=bool)

	if k_neighbors is not None and k_neighbors < P:
		# keep top-k smallest distances per row
		order = np.argsort(dists, axis=1)
		k_idx = order[:, :k_neighbors]
		row_idx = np.arange(Q)[:, None]
		k_mask = np.zeros_like(mask)
		k_mask[row_idx, k_idx] = True
		mask = mask & k_mask

	return dists, mask


def idw_interpolate(
		points: Sequence[Tuple[float, float, float]],
		lat_grid: np.ndarray,
		lon_grid: np.ndarray,
		spec: InterpolationSpec,
		center_lat: Optional[float] = None,
		center_lon: Optional[float] = None,
		radius_km: Optional[float] = None,
) -> np.ndarray:
	if len(points) == 0:
		raise ValueError("No points provided for interpolation")
	pts = np.asarray(points, dtype=float)
	if pts.shape[1] != 3:
		raise ValueError("points must be (lat, lon, value)")

	if len(points) == 1:
		return np.full_like(lat_grid, fill_value=pts[0, 2], dtype=float)

	dists, mask = _select_neighbors(
		pts, lat_grid, lon_grid, spec.radius_km, spec.k_neighbors
	)

	Q, P = dists.shape
	values = pts[:, 2][None, :].repeat(Q, axis=0)

	# IDW weights
	with np.errstate(divide='ignore'):
		weights = 1.0 / np.power(dists, spec.idw_power)
	weights[~mask] = 0.0

	# handle exact matches (distance = 0)
	z_exact = (dists == 0)
	result = np.zeros(Q, dtype=float)
	result[z_exact.any(axis=1)] = values[z_exact.any(axis=1)][z_exact[z_exact.any(axis=1)]].mean(axis=1)

	row_sum = weights.sum(axis=1)
	valid = row_sum > 0
	result[valid] = (weights[valid] * values[valid]).sum(axis=1) / row_sum[valid]

	res_grid = result.reshape(lat_grid.shape)

	# mask outside AOI circle if provided
	if center_lat is not None and center_lon is not None and radius_km is not None:
		inside = mask_outside_circle(lat_grid, lon_grid, center_lat, center_lon, radius_km)
		res_grid = np.where(inside, res_grid, np.nan)

	return res_grid


def rbf_interpolate(
		points: Sequence[Tuple[float, float, float]],
		lat_grid: np.ndarray,
		lon_grid: np.ndarray,
		function: str = "linear",
		epsilon: Optional[float] = None,
		center_lat: Optional[float] = None,
		center_lon: Optional[float] = None,
		radius_km: Optional[float] = None,
) -> np.ndarray:
	try:
		from scipy.interpolate import Rbf
	except Exception as exc:  # noqa: BLE001
		logger.warning("SciPy not available or failed (%s). Falling back to IDW.", exc)
		# Fallback to IDW (power=2 as common default)
		default_spec = InterpolationSpec(method="idw", idw_power=2.0, resolution_km=5.0, k_neighbors=8)
		return idw_interpolate(points, lat_grid, lon_grid, default_spec, center_lat, center_lon, radius_km)

	pts = np.asarray(points, dtype=float)
	if pts.shape[1] != 3:
		raise ValueError("points must be (lat, lon, value)")

	rbf = Rbf(pts[:, 0], pts[:, 1], pts[:, 2], function=function, epsilon=epsilon)
	res = rbf(lat_grid, lon_grid)
	res = res.astype(float)

	if center_lat is not None and center_lon is not None and radius_km is not None:
		inside = mask_outside_circle(lat_grid, lon_grid, center_lat, center_lon, radius_km)
		res = np.where(inside, res, np.nan)

	return res


def interpolate_surface(
		points: Sequence[Tuple[float, float, float]],
		lat_grid: np.ndarray,
		lon_grid: np.ndarray,
		spec: InterpolationSpec,
		center_lat: Optional[float] = None,
		center_lon: Optional[float] = None,
		radius_km: Optional[float] = None,
) -> np.ndarray:
	if spec.method == "idw":
		return idw_interpolate(points, lat_grid, lon_grid, spec, center_lat, center_lon, radius_km)
	elif spec.method == "rbf":
		return rbf_interpolate(points, lat_grid, lon_grid, center_lat=center_lat, center_lon=center_lon, radius_km=radius_km)
	else:
		raise ValueError("Unsupported interpolation method")


__all__ = ["interpolate_surface", "idw_interpolate", "rbf_interpolate"]

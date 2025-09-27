from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np

from . import get_logger


logger = get_logger(__name__)


EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	dphi = math.radians(lat2 - lat1)
	dlambda = math.radians(lon2 - lon1)
	a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	return EARTH_RADIUS_KM * c


def is_within_circle(lat: float, lon: float, center_lat: float, center_lon: float, radius_km: float) -> bool:
	return haversine_km(lat, lon, center_lat, center_lon) <= radius_km


def circle_bbox(center_lat: float, center_lon: float, radius_km: float) -> Tuple[float, float, float, float]:
	lat_delta = math.degrees(radius_km / EARTH_RADIUS_KM)
	lon_delta = math.degrees(radius_km / (EARTH_RADIUS_KM * math.cos(math.radians(center_lat)) or 1e-9))
	min_lat = max(-90.0, center_lat - lat_delta)
	max_lat = min(90.0, center_lat + lat_delta)
	min_lon = max(-180.0, center_lon - lon_delta)
	max_lon = min(180.0, center_lon + lon_delta)
	return (min_lat, min_lon, max_lat, max_lon)


@dataclass
class GridDefinition:
	lat_grid: np.ndarray  # shape (H, W)
	lon_grid: np.ndarray  # shape (H, W)
	bounds: Tuple[float, float, float, float]  # (min_lat, min_lon, max_lat, max_lon)
	resolution_km: float


def estimate_grid_shape(bounds: Tuple[float, float, float, float], resolution_km: float) -> Tuple[int, int]:
	min_lat, min_lon, max_lat, max_lon = bounds
	lat_km = haversine_km(min_lat, min_lon, max_lat, min_lon)
	lon_km = haversine_km(min_lat, min_lon, min_lat, max_lon)
	height = max(1, int(round(lat_km / resolution_km)))
	width = max(1, int(round(lon_km / resolution_km)))
	return height, width


def generate_circle_grid(center_lat: float, center_lon: float, radius_km: float, resolution_km: float) -> GridDefinition:
	bounds = circle_bbox(center_lat, center_lon, radius_km)
	height, width = estimate_grid_shape(bounds, resolution_km)
	min_lat, min_lon, max_lat, max_lon = bounds
	lat_lin = np.linspace(min_lat, max_lat, height)
	lon_lin = np.linspace(min_lon, max_lon, width)
	lon_grid, lat_grid = np.meshgrid(lon_lin, lat_lin)
	return GridDefinition(lat_grid=lat_grid, lon_grid=lon_grid, bounds=bounds, resolution_km=resolution_km)


def mask_outside_circle(lat_grid: np.ndarray, lon_grid: np.ndarray, center_lat: float, center_lon: float, radius_km: float) -> np.ndarray:
	# Vectorized haversine approximation by converting to radians and using broadcasting
	lat1 = np.radians(lat_grid)
	lon1 = np.radians(lon_grid)
	lat2 = math.radians(center_lat)
	lon2 = math.radians(center_lon)
	dlat = lat1 - lat2
	dlon = lon1 - lon2
	a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
	c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
	dist = EARTH_RADIUS_KM * c
	return dist <= radius_km


def filter_points_within_circle(points: Sequence[Tuple[float, float, float]], center_lat: float, center_lon: float, radius_km: float) -> List[Tuple[float, float, float]]:
	# points: list of (lat, lon, value)
	return [p for p in points if is_within_circle(p[0], p[1], center_lat, center_lon, radius_km)]


__all__ = [
	"haversine_km",
	"is_within_circle",
	"circle_bbox",
	"GridDefinition",
	"estimate_grid_shape",
	"generate_circle_grid",
	"mask_outside_circle",
	"filter_points_within_circle",
]

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Literal, Optional, Tuple


AOIType = Literal["circle", "bbox"]
InterpolationMethod = Literal["idw", "rbf"]
TimeAggMode = Literal["auto", "hourly", "daily"]
SoilProvider = Literal["soilgrids", "esdac", "brgm", "custom"]
SoilStyle = Literal["raster", "tiles"]


@dataclass
class AOI:
	type: AOIType
	center_lat: Optional[float] = None
	center_lon: Optional[float] = None
	radius_km: Optional[float] = None
	bbox: Optional[Tuple[float, float, float, float]] = None

	def validate(self) -> None:
		if self.type == "circle":
			if self.center_lat is None or self.center_lon is None or self.radius_km is None:
				raise ValueError("AOI circle requires center_lat, center_lon, radius_km")
			if not (-90.0 <= self.center_lat <= 90.0 and -180.0 <= self.center_lon <= 180.0):
				raise ValueError("AOI center coordinates out of range")
			if self.radius_km <= 0:
				raise ValueError("AOI radius_km must be > 0")
		elif self.type == "bbox":
			if self.bbox is None:
				raise ValueError("AOI bbox requires bbox=(min_lat, min_lon, max_lat, max_lon)")
			min_lat, min_lon, max_lat, max_lon = self.bbox
			if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90 and -180 <= min_lon <= 180 and -180 <= max_lon <= 180):
				raise ValueError("AOI bbox coordinates out of range")
			if min_lat >= max_lat or min_lon >= max_lon:
				raise ValueError("AOI bbox must have min < max for both lat and lon")
		else:
			raise ValueError("Unsupported AOI type")


@dataclass
class InterpolationSpec:
	enabled_weather: bool = True
	enabled_pollution: bool = True
	method: InterpolationMethod = "idw"
	resolution_km: float = 5.0
	idw_power: float = 2.0
	radius_km: Optional[float] = None
	k_neighbors: Optional[int] = 8

	def validate(self) -> None:
		if self.method not in ("idw", "rbf"):
			raise ValueError("Interpolation method must be 'idw' or 'rbf'")
		if self.resolution_km <= 0:
			raise ValueError("resolution_km must be > 0")
		if self.idw_power <= 0:
			raise ValueError("idw_power must be > 0")
		if self.radius_km is None and self.k_neighbors is None:
			raise ValueError("Provide either radius_km or k_neighbors for neighborhood selection")
		if self.k_neighbors is not None and self.k_neighbors <= 0:
			raise ValueError("k_neighbors must be > 0")
		if self.radius_km is not None and self.radius_km <= 0:
			raise ValueError("radius_km must be > 0")


@dataclass
class TimeAggSpec:
	mode: TimeAggMode = "auto"

	def validate(self) -> None:
		if self.mode not in ("auto", "hourly", "daily"):
			raise ValueError("TimeAggSpec.mode must be one of: auto, hourly, daily")


@dataclass
class SoilLayerSpec:
	enabled: bool = False
	provider: SoilProvider = "soilgrids"
	style: SoilStyle = "tiles"
	opacity: float = 0.6
	cache_policy: str = "persistent"
	extra: Dict[str, str] = field(default_factory=dict)

	def validate(self) -> None:
		if self.provider not in ("soilgrids", "esdac", "brgm", "custom"):
			raise ValueError("Unsupported soil provider")
		if self.style not in ("raster", "tiles"):
			raise ValueError("Soil style must be 'raster' or 'tiles'")
		if not (0.0 <= self.opacity <= 1.0):
			raise ValueError("opacity must be between 0 and 1")


__all__ = [
	"AOI",
	"InterpolationSpec",
	"TimeAggSpec",
	"SoilLayerSpec",
]

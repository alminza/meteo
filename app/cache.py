from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

from .models import AOI, InterpolationSpec, TimeAggSpec, SoilLayerSpec
from . import get_logger


logger = get_logger(__name__)


def _stable_json(data: Dict[str, Any]) -> str:
	return json.dumps(data, sort_keys=True, separators=(",", ":"))


def compute_manifest_hash(
		aoi: AOI,
		interp: InterpolationSpec,
		time_agg: TimeAggSpec,
		soil: SoilLayerSpec,
		soil_provider_meta: Optional[Dict[str, Any]] = None,
)	-> str:
	payload = {
		"aoi": asdict(aoi),
		"interpolation": {
			"method": interp.method,
			"resolution_km": interp.resolution_km,
			"idw_power": interp.idw_power,
			"radius_km": interp.radius_km,
			"k_neighbors": interp.k_neighbors,
			"enabled_weather": interp.enabled_weather,
			"enabled_pollution": interp.enabled_pollution,
		},
		"time_agg": {"mode": time_agg.mode},
		"soil": {
			"provider": soil.provider,
			"style": soil.style,
			"opacity": soil.opacity,
			"cache_policy": soil.cache_policy,
		},
		"soil_meta": soil_provider_meta or {},
	}
	data = _stable_json(payload).encode("utf-8")
	return hashlib.sha256(data).hexdigest()


def ensure_dir(path: str | os.PathLike) -> Path:
	p = Path(path)
	p.mkdir(parents=True, exist_ok=True)
	return p


def tile_cache_path(base_dir: str | os.PathLike, provider: str, z: int, x: int, y: int, ext: str = "png") -> Path:
	root = ensure_dir(Path(base_dir) / provider / str(z) / str(x))
	return root / f"{y}.{ext}"


__all__ = ["compute_manifest_hash", "ensure_dir", "tile_cache_path"]

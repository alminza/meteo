from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

from .models import InterpolationSpec, SoilLayerSpec
from . import get_logger


logger = get_logger()


DEFAULT_CONFIG: Dict[str, Any] = {
	"soil": {
		"providers": {
			"soilgrids": {
				"tiles_url": "https://maps.isric.org/mapserv?map=/map/soilgrids.map&LAYERS=bdod_mean&FORMAT=image/png&TRANSPARENT=true&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG:3857&BBOX={bbox}&WIDTH=256&HEIGHT=256",
			},
			"esdac": {
				"wms_url": "https://esdac.jrc.ec.europa.eu/arcgis/services/global/soil/MapServer/WMSServer",
			},
			"brgm": {
				"wms_url": "https://geoservices.brgm.fr/geologie",
			},
			"custom": {
				"tiles_url": "",
				"wms_url": "",
			},
		}
	},
	"cache": {
		"tiles_dir": ".tiles/soil",
		"ttl_days": 45,
	},
	"interpolation": {
		"defaults": {
			"method": "idw",
			"power": 2.0,
			"k": 8,
			"resolution_km": 5.0,
		}
	},
}


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
	result = dict(base)
	for key, value in override.items():
		if isinstance(value, dict) and isinstance(result.get(key), dict):
			result[key] = deep_merge(result[key], value)
		else:
			result[key] = value
	return result


def load_config(config_path: str | os.PathLike = "config.yaml") -> Dict[str, Any]:
	path = Path(config_path)
	user_cfg: Dict[str, Any] = {}
	if path.exists():
		with path.open("r", encoding="utf-8") as f:
			user_cfg = yaml.safe_load(f) or {}
	else:
		logger.info("No config.yaml found, using defaults")
	config = deep_merge(DEFAULT_CONFIG, user_cfg)
	return config


def interpolation_spec_from_config(config: Dict[str, Any]) -> InterpolationSpec:
	defaults = config.get("interpolation", {}).get("defaults", {})
	spec = InterpolationSpec(
		method=str(defaults.get("method", "idw")),
		resolution_km=float(defaults.get("resolution_km", 5.0)),
		idw_power=float(defaults.get("power", 2.0)),
		k_neighbors=int(defaults.get("k", 8)) if defaults.get("k") is not None else None,
	)
	spec.validate()
	return spec


def default_soil_spec(config: Dict[str, Any]) -> SoilLayerSpec:
	spec = SoilLayerSpec(enabled=False, provider="soilgrids", style="tiles", opacity=0.6)
	spec.validate()
	return spec


__all__ = ["load_config", "interpolation_spec_from_config", "default_soil_spec"]

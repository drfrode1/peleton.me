from pathlib import Path
from typing import Any

import yaml


def load_locations_config() -> dict[str, Any]:
    """Locates and loads the locations.yaml configuration file."""
    candidates = [
        Path(__file__).parent.parent / "config" / "locations.yaml",
        Path(__file__).parent.parent.parent / "config" / "locations.yaml",
        Path("data_pipeline/config/locations.yaml"),
        Path("config/locations.yaml"),
        Path("locations.yaml"),
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                return content if isinstance(content, dict) else {}

    raise FileNotFoundError("Could not find locations.yaml configuration file in candidate paths.")

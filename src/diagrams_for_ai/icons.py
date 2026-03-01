import base64
import os
from functools import lru_cache
from pathlib import Path

from PIL import Image

import diagrams


def _resources_dir() -> Path:
    diagrams_dir = Path(os.path.dirname(diagrams.__file__))
    return diagrams_dir.parent / "resources"


def _find_icon_file(icon_key: str) -> Path:
    """Resolve an icon key to a file path.

    Supports two formats:
      - Full path:  "aws/compute/ec2"  -> resources/aws/compute/ec2.png
      - Custom path: "/absolute/path/to/icon.png" or "relative/icon.png"
    """
    if os.path.isfile(icon_key):
        return Path(icon_key)

    resources = _resources_dir()
    candidate = resources / f"{icon_key}.png"
    if candidate.is_file():
        return candidate

    parts = icon_key.split("/")
    if len(parts) >= 2:
        provider = parts[0]
        name = parts[-1]
        category_parts = parts[1:-1]

        if category_parts:
            category_path = "/".join(category_parts)
            candidate = resources / provider / category_path / f"{name}.png"
            if candidate.is_file():
                return candidate

        provider_dir = resources / provider
        if provider_dir.is_dir():
            for category_dir in provider_dir.iterdir():
                if category_dir.is_dir():
                    candidate = category_dir / f"{name}.png"
                    if candidate.is_file():
                        return candidate

    raise FileNotFoundError(
        f"Icon not found: '{icon_key}'. "
        f"Use format 'provider/category/name' (e.g. 'aws/compute/ec2') "
        f"or an absolute file path."
    )


@lru_cache(maxsize=256)
def load_icon_base64(icon_key: str) -> str:
    """Load an icon and return it as a base64-encoded data URI string."""
    path = _find_icon_file(icon_key)
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    suffix = path.suffix.lstrip(".").lower()
    mime = {"png": "image/png", "svg": "image/svg+xml", "jpg": "image/jpeg"}.get(
        suffix, "image/png"
    )
    return f"data:{mime};base64,{data}"


@lru_cache(maxsize=256)
def load_icon_image(icon_key: str, size: int = 64) -> Image.Image:
    """Load an icon as a Pillow Image, resized to the given square size."""
    path = _find_icon_file(icon_key)
    img = Image.open(path).convert("RGBA")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img


def list_providers() -> list[str]:
    """List all available icon providers (aws, gcp, azure, etc.)."""
    resources = _resources_dir()
    return sorted(
        d.name for d in resources.iterdir() if d.is_dir()
    )


def list_icons(provider: str) -> list[str]:
    """List all icon keys for a provider, e.g. list_icons('aws')."""
    resources = _resources_dir()
    provider_dir = resources / provider
    if not provider_dir.is_dir():
        raise ValueError(f"Unknown provider: '{provider}'")

    icons = []
    for category_dir in sorted(provider_dir.iterdir()):
        if category_dir.is_dir():
            for icon_file in sorted(category_dir.iterdir()):
                if icon_file.suffix == ".png":
                    key = f"{provider}/{category_dir.name}/{icon_file.stem}"
                    icons.append(key)
    return icons

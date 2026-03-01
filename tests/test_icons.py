import pytest
from PIL import Image

from diagrams_for_ai.icons import (
    _find_icon_file,
    list_icons,
    list_providers,
    load_icon_base64,
    load_icon_image,
)


def test_list_providers_returns_known_providers():
    providers = list_providers()
    assert "aws" in providers
    assert "gcp" in providers
    assert "azure" in providers
    assert "k8s" in providers


def test_list_providers_returns_sorted():
    providers = list_providers()
    assert providers == sorted(providers)


def test_list_icons_aws_has_ec2():
    icons = list_icons("aws")
    assert "aws/compute/ec2" in icons


def test_list_icons_unknown_provider_raises():
    with pytest.raises(ValueError):
        list_icons("nonexistent_provider")


def test_find_icon_file_full_path():
    path = _find_icon_file("aws/compute/ec2")
    assert path.exists()
    assert path.suffix == ".png"


def test_find_icon_file_search():
    path = _find_icon_file("aws/ec2")
    assert path.exists()


def test_find_icon_file_missing_raises():
    with pytest.raises(FileNotFoundError):
        _find_icon_file("nonexistent/missing/icon")


def test_load_icon_base64_returns_data_uri():
    uri = load_icon_base64("aws/compute/ec2")
    assert uri.startswith("data:image/png;base64,")
    assert len(uri) > 100


def test_load_icon_image_returns_pillow_image():
    img = load_icon_image("aws/compute/ec2", size=64)
    assert isinstance(img, Image.Image)
    assert img.size == (64, 64)
    assert img.mode == "RGBA"


def test_load_icon_image_custom_size():
    img = load_icon_image("aws/compute/ec2", size=128)
    assert img.size == (128, 128)

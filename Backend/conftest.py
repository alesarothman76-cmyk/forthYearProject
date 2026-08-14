"""Root-level shared fixtures."""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


def pytest_collection_modifyitems(config, items):
    """Auto-skip tests marked requires_backbone if the real .pth file isn't
    present - matches Section 8.5's documented current real-world state
    (only the backbone MAY or may not be deployed in a given environment)."""
    from django.conf import settings

    backbone_present = settings.RESNET_BACKBONE_PATH.exists()
    if backbone_present:
        return

    skip_marker = pytest.mark.skip(reason="ResNet50 backbone weights not present at RESNET_BACKBONE_PATH")
    for item in items:
        if "requires_backbone" in item.keywords:
            item.add_marker(skip_marker)

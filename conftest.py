import os

import pytest


@pytest.fixture(autouse=True)
def _isolate_media_root(settings, tmp_path):
    media_root = tmp_path / "test-media"
    os.makedirs(media_root, exist_ok=True)
    settings.MEDIA_ROOT = str(media_root)


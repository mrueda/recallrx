from pathlib import Path

from openrecall.validate import validate_dataset


def test_seed_dataset_validates():
    assert validate_dataset(Path("data")) == []

from pathlib import Path

from openrecall_es.validate import validate_dataset


def test_seed_dataset_validates():
    assert validate_dataset(Path("data")) == []

from pathlib import Path

from openrecall_es.cli import build_dist


def test_dist_copies_site_and_data(tmp_path):
    output = tmp_path / "dist"

    build_dist(Path("site"), Path("data"), output)

    assert (output / "index.html").exists()
    assert (output / "data" / "metadata.json").exists()

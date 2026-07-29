from pathlib import Path

from recallrx.cli import build_dist


def test_dist_copies_site_and_data(tmp_path):
    output = tmp_path / "dist"

    build_dist(Path("site"), Path("data"), output)

    assert (output / "index.html").exists()
    assert (output / "freshness.js").exists()
    assert (output / "recallrx-logo.svg").exists()
    assert (output / "data" / "metadata.json").exists()


def test_logo_assets_stay_in_sync():
    assert Path("site/recallrx-logo.svg").read_bytes() == Path(
        "docs-site/static/img/recallrx-logo.svg"
    ).read_bytes()

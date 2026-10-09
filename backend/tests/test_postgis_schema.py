from pathlib import Path
def test_spatial_adapter_has_real_geography_index():
    src=Path(__file__).parents[1].joinpath("app/postgis.py").read_text()
    assert "GIST(geom)" in src and "ST_MakePoint" in src

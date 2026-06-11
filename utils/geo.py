"""Geographic helpers for the branch map.

The survey data has no branch coordinates, so we place each branch at the
centroid of its city/regency (KABKOTA) using a curated lookup, with a small
deterministic jitter so multiple branches in the same city don't overlap.
"""

import hashlib
import json
from pathlib import Path

import pandas as pd

# Bundled kabupaten/kota (ADM2) boundaries for the 55 cities present in the data,
# derived from geoBoundaries IDN ADM2 and tagged with our KABKOTA / PROV names.
KABKOTA_GEOJSON_PATH = Path(__file__).resolve().parent.parent / "assets" / "indonesia-kabkota.geojson"


def load_kabkota_geojson():
    with open(KABKOTA_GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Approximate (lat, lon) for every city/regency present in the data.
CITY_COORDS = {
    # DKI Jakarta
    "Jakarta Barat": (-6.1684, 106.7588),
    "Jakarta Pusat": (-6.1865, 106.8343),
    "Jakarta Selatan": (-6.2615, 106.8106),
    "Jakarta Timur": (-6.2250, 106.9004),
    "Jakarta Utara": (-6.1214, 106.8744),
    # Banten
    "Cilegon": (-6.0025, 106.0540),
    "Lebak": (-6.5644, 106.2510),
    "Pandeglang": (-6.3090, 106.1060),
    "Serang": (-6.1200, 106.1503),
    "Tangerang": (-6.1783, 106.6319),
    "Tangerang Selatan": (-6.2889, 106.7180),
    # Jawa Barat
    "Bandung": (-6.9175, 107.6191),
    "Bandung Barat": (-6.8650, 107.4760),
    "Banjar": (-7.3700, 108.5340),
    "Bekasi": (-6.2383, 106.9756),
    "Bogor": (-6.5950, 106.8166),
    "Ciamis": (-7.3260, 108.3530),
    "Cianjur": (-6.8170, 107.1425),
    "Cimahi": (-6.8721, 107.5420),
    "Cirebon": (-6.7320, 108.5523),
    "Depok": (-6.4025, 106.7942),
    "Garut": (-7.2140, 107.9080),
    "Indramayu": (-6.3360, 108.3240),
    "Karawang": (-6.3227, 107.3376),
    "Kuningan": (-6.9760, 108.4830),
    "Majalengka": (-6.8360, 108.2280),
    "Pangandaran": (-7.6960, 108.6500),
    "Purwakarta": (-6.5560, 107.4430),
    "Subang": (-6.5710, 107.7600),
    "Sukabumi": (-6.9277, 106.9300),
    "Sumedang": (-6.8590, 107.9180),
    "Tasikmalaya": (-7.3270, 108.2200),
    # Jawa Tengah
    "Banyumas": (-7.4250, 109.2390),
    "Boyolali": (-7.5320, 110.5960),
    "Pekalongan": (-6.8886, 109.6753),
    "Semarang": (-6.9667, 110.4167),
    "Sragen": (-7.4270, 111.0200),
    "Surakarta": (-7.5755, 110.8243),
    "Tegal": (-6.8694, 109.1402),
    # Jawa Timur
    "Surabaya": (-7.2575, 112.7521),
    # Bali
    "Denpasar": (-8.6705, 115.2126),
    # Kalimantan Selatan
    "Banjarbaru": (-3.4420, 114.8410),
    "Banjarmasin": (-3.3194, 114.5908),
    # Kalimantan Timur
    "Balikpapan": (-1.2675, 116.8289),
    "Samarinda": (-0.5022, 117.1536),
    # Kepulauan Riau
    "Batam": (1.0456, 104.0305),
    "Tanjung Pinang": (0.9186, 104.4665),
    # Lampung
    "Bandar Lampung": (-5.3971, 105.2668),
    "Lampung Tengah": (-4.8830, 105.2200),
    # Riau
    "Pekanbaru": (0.5071, 101.4478),
    # Sulawesi Selatan
    "Gowa": (-5.2060, 119.4490),
    "Makassar": (-5.1477, 119.4327),
    # Sumatera Selatan
    "Ogan Ilir": (-3.2200, 104.6400),
    "Palembang": (-2.9761, 104.7754),
    # Sumatera Utara
    "Medan": (3.5952, 98.6722),
}

# Map centre (roughly Java) and default zoom.
MAP_CENTER = (-4.0, 113.0)
MAP_ZOOM = 5


def _jitter(name, scale=0.045):
    """Deterministic small offset (lat, lon) derived from the branch name."""
    h = hashlib.md5(str(name).encode()).hexdigest()
    dx = (int(h[:4], 16) / 0xFFFF - 0.5) * 2 * scale
    dy = (int(h[4:8], 16) / 0xFFFF - 0.5) * 2 * scale
    return dx, dy


def branch_coord(branch, city):
    """Return (lat, lon) for a branch, jittered around its city centroid."""
    base = CITY_COORDS.get(str(city))
    if base is None:
        return None
    dx, dy = _jitter(branch)
    return (base[0] + dx, base[1] + dy)


def missing_cities(df, city_col="KABKOTA"):
    """Cities present in the data but absent from the coordinate lookup."""
    if city_col not in df.columns:
        return []
    cities = df[city_col].dropna().astype(str).unique()
    return [c for c in cities if c not in CITY_COORDS]

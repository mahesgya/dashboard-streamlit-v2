"""Data layer: load the codebook + responses, attach labels, parse the 1–6 scales.

Per the PRD (section 5.1):
  1. Read codebook.csv to get the ordered list of variable codes and their labels.
  2. Read responses with dtype=str (ratings are stored as mixed strings).
  3. Parse every T_* rating column to a numeric 1–6 scale (999 / '' -> NaN).
  4. Parse the free-numeric columns (age, waiting times) to float.
  5. Cache the result so the heavy CSV read happens only once.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CODEBOOK_PATH = DATA_DIR / "codebook.csv"
RESPONSE_PATH = DATA_DIR / "response.csv"

# Outcome columns measured on a rating scale that we want a numeric copy of.
# E1A/E1B = CSAT (1–6); G1A/G1C = NPS (0–10); F1A/F1B = retention (1–6).
OUTCOME_COLS = ["E1A", "E1B", "G1A", "G1C", "F1A", "F1B"]

# Free-text numeric columns (minutes / years).
NUMERIC_COLS = ["S2_1", "TL5", "TL6", "CS5", "CS6"]

_LEADING_INT = re.compile(r"^\s*(\d+)")


def to_scale(value):
    """Extract the leading integer of a rating cell.

    '5' -> 5, '6 SANGAT PUAS' -> 6, '999' -> NaN, '' / NaN -> NaN.
    """
    if value is None:
        return np.nan
    s = str(value).strip()
    if s == "" or s.lower() in ("nan", "none"):
        return np.nan
    m = _LEADING_INT.match(s)
    if not m:
        return np.nan
    n = int(m.group(1))
    if n == 999:
        return np.nan
    return float(n)


@st.cache_data(show_spinner="Loading survey data…")
def load_data():
    if not RESPONSE_PATH.exists() or not CODEBOOK_PATH.exists():
        st.error(
            "Data files not found. Expected `data/codebook.csv` and `data/response.csv` "
            "next to the app."
        )
        st.stop()

    codebook = pd.read_csv(CODEBOOK_PATH, dtype=str).fillna("")
    # code -> label map; later codes override earlier duplicates harmlessly.
    labels = dict(zip(codebook["code"], codebook["label"]))

    df = pd.read_csv(RESPONSE_PATH, dtype=str, keep_default_na=False)

    # SERIAL arrives as scientific notation — treat it as an opaque string ID.
    if "SERIAL" in df.columns:
        df["SERIAL"] = df["SERIAL"].astype(str)

    # Parse every touchpoint rating column in place to a numeric 1–6 scale.
    scale_cols = [c for c in df.columns if c.startswith("T_")]
    for c in scale_cols:
        df[c] = df[c].map(to_scale)

    # Numeric copies of the outcome metrics (keep the raw label column too).
    for c in OUTCOME_COLS:
        if c in df.columns:
            df[c + "_num"] = df[c].map(to_scale)

    # Free-numeric columns -> float.
    for c in NUMERIC_COLS:
        if c in df.columns:
            df[c + "_num"] = pd.to_numeric(
                df[c].str.extract(r"(\d+[.,]?\d*)", expand=False).str.replace(",", ".", regex=False),
                errors="coerce",
            )

    # De-fragment after the many column insertions above.
    df = df.copy()

    return df, labels


def clean_label(label):
    """Strip the '- XYZ' / '- kompetitor' benchmark suffix from a codebook label."""
    if label is None:
        return ""
    s = str(label)
    s = re.sub(r"\s*-\s*(XYZ|kompetitor)\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\.\d+$", "", s)  # drop the pandas '.1' duplicate suffix
    return s.strip()

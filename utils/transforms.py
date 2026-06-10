"""Reusable analytics helpers (PRD section 5.2 / 5.3).

Everything keys off the codebook labels: paired benchmark columns end with
'- XYZ' or '- kompetitor', so we classify Bank XYZ vs Competitor from the label
rather than relying purely on the 3n-1 / 3n suffix arithmetic. This also handles
the groups the PRD flagged as uncertain (T_CA1/CA2, T_SL1/SL2) — they simply have
no competitor counterpart and fall through to the single-series helper.
"""

import re

import numpy as np
import pandas as pd

from utils.data_loader import clean_label

# Top-2-Box on a 1–6 scale = scores 5 and 6.
TOP_BOX_SCORES = {5, 6}


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------
def aggregate_series(series, mode="Mean"):
    """Aggregate a parsed 1–6 rating column.

    Mean       -> arithmetic mean ignoring NaN.
    Top-2-Box  -> % of valid responses scoring 5 or 6.
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) == 0:
        return np.nan
    if mode == "Top-2-Box":
        return round(s.isin(TOP_BOX_SCORES).mean() * 100, 1)
    return round(s.mean(), 2)


def metric_suffix(mode="Mean"):
    return "%" if mode == "Top-2-Box" else " / 6"


def metric_axis_title(mode="Mean"):
    return "Top-2-Box (%)" if mode == "Top-2-Box" else "Mean score (1–6)"


# ---------------------------------------------------------------------------
# Column discovery
# ---------------------------------------------------------------------------
def group_columns(df, prefix):
    """Return the columns matching `prefix` followed by `_<number>`, in order."""
    pat = re.compile(rf"^{re.escape(prefix)}_\d+$")
    cols = [c for c in df.columns if pat.match(c)]
    cols.sort(key=lambda c: int(c.rsplit("_", 1)[1]))
    return cols


def _benchmark_side(label):
    """'XYZ', 'Competitor' or None, read from the label suffix."""
    if re.search(r"-\s*XYZ\s*$", str(label), flags=re.IGNORECASE):
        return "XYZ"
    if re.search(r"-\s*kompetitor\s*$", str(label), flags=re.IGNORECASE):
        return "Competitor"
    return None


# ---------------------------------------------------------------------------
# Paired (XYZ vs Competitor) scores — PRD 5.2
# ---------------------------------------------------------------------------
OVERALL_PATTERN = r"keseluruhan|overall|secara umum"


def _is_overall(attr):
    return bool(re.search(OVERALL_PATTERN, str(attr), flags=re.IGNORECASE))


def get_paired_scores(df, prefix, labels, mode="Mean", drop_overall=True):
    """Return DataFrame[attribute, xyz, competitor, gap] for a paired group.

    Only attributes that have BOTH an XYZ and a competitor column are returned.
    `gap` = xyz - competitor (positive => Bank XYZ ahead). When `drop_overall`
    is set, the per-touchpoint 'overall / keseluruhan' summary rows are excluded
    so charts show granular attributes only.
    """
    rows = {}
    for col in group_columns(df, prefix):
        side = _benchmark_side(labels.get(col, ""))
        if side is None:
            continue
        attr = clean_label(labels.get(col, col))
        if drop_overall and _is_overall(attr):
            continue
        rows.setdefault(attr, {})[side] = aggregate_series(df[col], mode)

    records = []
    for attr, sides in rows.items():
        if "XYZ" in sides and "Competitor" in sides:
            xyz = sides["XYZ"]
            comp = sides["Competitor"]
            gap = (xyz - comp) if (pd.notna(xyz) and pd.notna(comp)) else np.nan
            records.append(
                {"attribute": attr, "xyz": xyz, "competitor": comp, "gap": gap}
            )

    out = pd.DataFrame(records)
    if not out.empty:
        out = out.dropna(subset=["xyz", "competitor"]).reset_index(drop=True)
    return out


def has_competitor(df, prefix, labels):
    """True if the group contains any '- kompetitor' column."""
    return any(
        _benchmark_side(labels.get(c, "")) == "Competitor"
        for c in group_columns(df, prefix)
    )


def likert_composition(df, cols, labels):
    """Top-2 / Middle / Bottom-2 box composition (%) for the given 1–6 columns.

    Returns DataFrame[attribute, top, mid, bottom] where the three sum to ~100.
    """
    records = []
    for col in cols:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(s) == 0:
            continue
        top = round(s.isin([5, 6]).mean() * 100, 1)
        mid = round(s.isin([3, 4]).mean() * 100, 1)
        bottom = round(s.isin([1, 2]).mean() * 100, 1)
        records.append({
            "attribute": clean_label(labels.get(col, col)),
            "top": top, "mid": mid, "bottom": bottom,
        })
    return pd.DataFrame(records)


def branch_attribute_matrix(df, cols, labels, branch_col="CABANG", min_n=5, top_branches=15, mode="Mean"):
    """Branch × attribute score matrix for a heatmap.

    Rows = attributes (cleaned labels), columns = branches with >= `min_n` rows,
    capped at the `top_branches` largest branches by sample size.
    """
    if branch_col not in df.columns or not cols:
        return pd.DataFrame()

    sizes = df[branch_col].dropna().astype(str).value_counts()
    branches = [b for b, n in sizes.items() if n >= min_n][:top_branches]
    if not branches:
        return pd.DataFrame()

    data = {}
    for b in branches:
        sub = df[df[branch_col].astype(str) == b]
        data[b] = {clean_label(labels.get(c, c)): aggregate_series(sub[c], mode) for c in cols}
    matrix = pd.DataFrame(data)
    return matrix.dropna(how="all")


def get_single_scores(df, prefix, labels, mode="Mean", drop_overall=False):
    """Return DataFrame[attribute, score] for a single-series group (no competitor)."""
    records = []
    cols = group_columns(df, prefix)
    for col in cols:
        attr = clean_label(labels.get(col, col))
        records.append({"attribute": attr, "score": aggregate_series(df[col], mode), "code": col})
    out = pd.DataFrame(records).dropna(subset=["score"]).reset_index(drop=True)
    if drop_overall and not out.empty:
        mask = out["attribute"].str.contains(
            r"keseluruhan|overall|secara umum", case=False, na=False
        )
        out = out[~mask].reset_index(drop=True)
    return out


# ---------------------------------------------------------------------------
# Outcome metrics — PRD 3.3
# ---------------------------------------------------------------------------
def nps(series):
    """Net Promoter Score from a 0–10 column (promoters 9–10, detractors 0–6)."""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) == 0:
        return None
    promoters = (s >= 9).mean()
    detractors = (s <= 6).mean()
    return round((promoters - detractors) * 100, 1)


def nps_breakdown(series):
    """Return (%promoters, %passives, %detractors) for a 0–10 column."""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) == 0:
        return (0.0, 0.0, 0.0)
    promoters = round((s >= 9).mean() * 100, 1)
    passives = round(((s >= 7) & (s <= 8)).mean() * 100, 1)
    detractors = round((s <= 6).mean() * 100, 1)
    return (promoters, passives, detractors)


def csat(df, col="E1A_num", mode="Mean"):
    """CSAT: mean of E1A (1–6) or its Top-2-Box."""
    if col not in df.columns:
        return None
    return aggregate_series(df[col], mode)


# ---------------------------------------------------------------------------
# Importance–Performance Analysis — PRD 5.3
# ---------------------------------------------------------------------------
def ipa(df, labels, imp_prefix="T_C1A", perf_prefix="T_C1B", mode="Mean"):
    """Return DataFrame[attribute, importance, performance] matched by attribute.

    Importance comes from the sequential T_C1A group; performance from the Bank
    XYZ side of the paired T_C1B group. They share the same attribute wording, so
    we match on the cleaned label.
    """
    importance = {}
    for col in group_columns(df, imp_prefix):
        attr = clean_label(labels.get(col, col))
        importance[attr] = aggregate_series(df[col], "Mean")

    performance = {}
    for col in group_columns(df, perf_prefix):
        if _benchmark_side(labels.get(col, "")) != "XYZ":
            continue
        attr = clean_label(labels.get(col, col))
        performance[attr] = aggregate_series(df[col], "Mean")

    records = []
    for attr, imp in importance.items():
        if attr in performance and pd.notna(imp) and pd.notna(performance[attr]):
            records.append(
                {"attribute": attr, "importance": imp, "performance": performance[attr]}
            )
    return pd.DataFrame(records)

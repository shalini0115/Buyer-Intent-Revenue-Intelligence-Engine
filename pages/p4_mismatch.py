"""pages/p4_mismatch.py - Mismatch Intelligence: SHAP diagnosed products with a fix for each."""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.style import SEG_COLORS, fmt_inr
from utils.theme import esc, kpi_html, md_html

# If a column in your data has a different name, add it to the matching list below.
CANDIDATES = {
    "title": ["title", "product_name", "name", "product_title"],
    "segment": ["segment", "pred_segment", "segment_pred", "placed_segment"],
    "target": ["target_segment", "ideal_segment", "intent_segment", "true_segment", "recommended_segment"],
    "discount": ["discount_pct", "discount_percentage", "discount", "discount_percent"],
    "savings": ["savings_ratio"],
    "trust": ["trust_score", "trust"],
    "rating": ["rating", "avg_rating", "rating_value"],
    "reviews": ["review_count", "reviews", "rating_count", "num_reviews"],
    "id": ["asin", "product_id", "id", "sku"],
    "cat": ["top_cat"],
}
LOSS = "mismatch_revenue_loss"
ID_LIKE = {"asin", "product_id", "id", "sku", "index", "idx"}


def pick(df, key):
    return next((c for c in CANDIDATES[key] if c in df.columns), None)


def pct(s):
    s = pd.to_numeric(s, errors="coerce")
    return s * 100 if s.max() <= 1 else s


def ok(v):
    return isinstance(v, (int, float, np.number)) and not pd.isna(v)


def num(v, f):
    return format(v, f) if ok(v) else "n/a"


def plot(fig, h=320):
    fig.update_layout(height=h, legend_title_text="")
    try:
        st.plotly_chart(fig, width="stretch")
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


# SHAP alignment
def shap_for(feat_all, shap_df, labels, id_col):
    """Return a SHAP frame aligned row for row with the selected products, or None."""
    try:
        if shap_df is None or len(shap_df) == 0:
            return None
        if id_col and id_col in shap_df.columns and id_col in feat_all.columns:
            sd = shap_df.drop_duplicates(id_col).set_index(id_col).select_dtypes("number")
            out = sd.reindex(feat_all.loc[labels, id_col].values)
        elif len(shap_df) == len(feat_all):
            sd = shap_df.select_dtypes("number")
            sd = sd.drop(columns=[c for c in sd.columns
                                  if c.lower() in ID_LIKE or c.lower().startswith("unnamed")])
            out = sd.iloc[feat_all.index.get_indexer(labels)]
        else:
            return None
        out = out.reset_index(drop=True)
        return out if out.shape[1] else None
    except Exception:
        return None


# Fix engine
def fix_text(kind, r):
    t = r.get("_target", "")
    texts = {
        "discount": ("Cut headline discounting",
                     f"Savings ratio is {num(r.get('_sav'), '.2f')} and the discount is {num(r.get('_disc'), '.0f')}%. "
                     "Deep discounts signal low quality to quality-led buyers. Move to a cleaner price point "
                     "and cap the discount near 20%."),
        "trust": ("Rebuild trust signals",
                  f"Trust score is {num(r.get('_trust'), '.2f')}. Use verified purchase review prompts, "
                  "brand store content and a fast answer time on buyer questions. Target 3.8 or higher."),
        "rating": ("Recover the rating",
                   f"Rating is {num(r.get('_rating'), '.1f')}. Audit the 1 and 2 star themes, correct listing "
                   "claims that drive returns, and target 4.2 or higher."),
        "reviews": ("Build review volume",
                    f"Review count is {num(r.get('_rev'), ',.0f')}. Add post purchase review requests and "
                    "bundle inserts to reach a credible volume for social proof buyers."),
        "deal": ("Make the deal visible",
                 f"Discount is {num(r.get('_disc'), '.0f')}%, too low for deal driven buyers. Add a coupon "
                 "badge or timed deal and aim for a 20 to 30% visible saving."),
        "quality": ("Lead with quality, not price",
                    "Rewrite the title and image stack around materials, warranty and certifications "
                    "instead of price claims."),
        "proof": ("Lead with social proof",
                  "Surface review count, star rating and photo reviews in the first image and bullet points."),
        "niche": ("Sharpen listing specifics",
                  "Use a specification rich title, comparison charts and A+ content so niche buyers "
                  "confirm fit quickly."),
    }
    return texts[kind], t


def build_fixes(r, barrier):
    plan = {}

    def add(prio, kind):
        if kind not in plan or prio < plan[kind]:
            plan[kind] = prio

    disc, sav, trust, rate, rev = (r.get(k) for k in ("_disc", "_sav", "_trust", "_rating", "_rev"))
    target = r.get("_target", "")
    if ok(sav) and sav > 0.35:
        add(1, "discount")
    if ok(trust) and trust < 3.5:
        add(1, "trust")
    if ok(rate) and rate < 4.0:
        add(2, "rating")
    if ok(rev) and rev < 100:
        add(2, "reviews")
    if target == "DEAL_SEEKER" and ok(disc) and disc < 15:
        add(2, "deal")
    if target == "QUALITY_FIRST" and ok(disc) and disc > 25:
        add(2, "quality")
    if target == "SOCIAL_PROOF":
        add(3, "proof")
    if target == "NICHE_EXPLORER":
        add(3, "niche")
    b = (barrier or "").lower()
    for key, kind in (("trust", "trust"), ("rating", "rating"), ("saving", "discount"),
                      ("discount", "discount"), ("review", "reviews")):
        if key in b:
            add(2, kind)
    ordered = sorted(plan.items(), key=lambda kv: kv[1])[:3]
    fixes = []
    for kind, prio in ordered:
        (title, detail), _ = fix_text(kind, r)
        fixes.append((prio, title, detail))
    if not fixes:
        fixes.append((3, "Monitor placement",
                      "No rule was triggered. Re-score this product after the next catalogue refresh."))
    return fixes


def card(r, rec, sev, cols):
    title = str(r.get(cols["title"], "Untitled product")) if cols["title"] else "Product"
    title = title if len(title) <= 120 else title[:117] + "..."
    chips = []
    seg = str(r.get(cols["segment"], "")) if cols["segment"] else ""
    if seg:
        col = SEG_COLORS.get(seg, "#7A6E65")
        chips.append(f'<span class="bi-chip" style="background:{col}1A;color:{col};border-color:{col}55;'
                     f'font-weight:600">Placed: {esc(seg)}</span>')
    tgt = r.get("_target", "")
    if tgt:
        chips.append(f'<span class="bi-chip">Target: {esc(tgt)}</span>')
    for lab, key, f, suf in (("Discount", "_disc", ".0f", "%"), ("Savings ratio", "_sav", ".3f", ""),
                             ("Trust", "_trust", ".2f", ""), ("Rating", "_rating", ".1f", "")):
        if ok(r.get(key)):
            chips.append(f'<span class="bi-chip">{lab} {format(r[key], f)}{suf}</span>')
    chips.append(f'<span class="bi-chip">{sev} priority</span>')

    shap_html = ""
    if rec["push"]:
        shap_html = (
            '<div class="bi-split">'
            f'<div class="bi-box push"><div class="bi-box-l">Classification driver</div>'
            f'<div class="bi-box-f">{esc(rec["push"].replace("_", " "))}</div>'
            f'<div class="bi-box-v">SHAP {rec["pv"]:+.3f}</div></div>'
            f'<div class="bi-box barrier"><div class="bi-box-l">Upgrade blocker</div>'
            f'<div class="bi-box-f">{esc(rec["bar"].replace("_", " "))}</div>'
            f'<div class="bi-box-v">SHAP {rec["bv"]:+.3f}</div></div></div>'
        )
    fixes = "".join(f"<li><b>{esc(t)}.</b> {esc(d)}</li>" for _, t, d in rec["fixes"])
    md_html(
        f'<div class="bi-card sev-{sev.lower()}">'
        f'<div class="bi-head"><div class="bi-title">{esc(title)}</div>'
        f'<div class="bi-loss">{esc(fmt_inr(r["_loss"]))}<small>revenue leakage per month</small></div></div>'
        f'<div class="bi-chips">{"".join(chips)}</div>{shap_html}'
        f'<div class="bi-fixes-l">Recommended fixes</div><ol class="bi-fixes">{fixes}</ol></div>'
    )


def render(feat, imp, filtered_feat, filtered_imp, shap_df):
    md_html('<div class="bi-sec">04 / Mismatch Intelligence</div>'
            '<div class="bi-h">Mismatch Alerts</div>'
            '<div class="bi-sub">SHAP diagnosed products where buyer intent misaligns with placement tier, '
            'each with a prioritised fix.</div>')

    df = filtered_feat
    if len(df) == 0:
        st.info("No products match the current filters.")
        return
    cols = {k: pick(df, k) for k in CANDIDATES}
    flag = df["mismatch_flag"].astype(bool)
    mism = df[flag]
    if mism.empty:
        st.success("No mismatched products in the current selection.")
        return

    sh = shap_for(feat, shap_df, mism.index, cols["id"])
    d = mism.reset_index(drop=True)
    d["_loss"] = pd.to_numeric(d[LOSS], errors="coerce").fillna(0)
    nan = pd.Series(np.nan, index=d.index)
    d["_disc"] = pct(d[cols["discount"]]) if cols["discount"] else nan
    d["_sav"] = pd.to_numeric(d[cols["savings"]], errors="coerce") if cols["savings"] else nan
    d["_trust"] = pd.to_numeric(d[cols["trust"]], errors="coerce") if cols["trust"] else nan
    d["_rating"] = pd.to_numeric(d[cols["rating"]], errors="coerce") if cols["rating"] else nan
    d["_rev"] = pd.to_numeric(d[cols["reviews"]], errors="coerce") if cols["reviews"] else nan
    d["_target"] = d[cols["target"]].astype(str).str.upper() if cols["target"] else ""

    q75, q50 = d["_loss"].quantile(0.75), d["_loss"].quantile(0.50)
    d["_sev"] = np.where(d["_loss"] >= q75, "Critical", np.where(d["_loss"] >= q50, "High", "Moderate"))

    recs = []
    for i, r in enumerate(d.to_dict("records")):
        push = bar = pv = bv = None
        if sh is not None:
            row = sh.iloc[i].dropna()
            if len(row):
                push, bar = row.idxmax(), row.idxmin()
                pv, bv = float(row[push]), float(row[bar])
        recs.append({"push": push, "bar": bar, "pv": pv, "bv": bv, "fixes": build_fixes(r, bar)})
    d["_primary"] = [x["fixes"][0][1] for x in recs]

    # KPI rows
    n, m, loss = len(df), len(d), d["_loss"].sum()
    top10 = d["_loss"].nlargest(10).sum() / loss * 100 if loss else 0
    top_cat = d.groupby(cols["cat"])["_loss"].sum().idxmax() if cols["cat"] else "n/a"
    row1 = [
        kpi_html("Misaligned products", f"{m:,}", f"of {n:,} in view", "bad"),
        kpi_html("Mismatch rate", f"{m / n * 100:.1f}%", "share of filtered catalogue", "warn"),
        kpi_html("Monthly leakage", fmt_inr(loss), "revenue lost to misplacement", "bad"),
        kpi_html("Avg leakage per product", fmt_inr(loss / m), "across misaligned set", "brand"),
        kpi_html("Critical products", f"{int((d['_sev'] == 'Critical').sum()):,}", "top quartile by leakage", "bad"),
    ]
    row2 = [
        kpi_html("Top 10 concentration", f"{top10:.1f}%", "of leakage sits in ten products", "warn"),
        kpi_html("Largest leaking category", str(top_cat), "by monthly leakage", "brand"),
    ]
    others = df[~flag]
    for lab, key, f in (("Trust gap", "trust", ".2f"), ("Rating gap", "rating", ".2f"),
                        ("Discount gap", "discount", ".1f")):
        c = cols[key]
        if c and not others.empty:
            a = pct(mism[c]).mean() if key == "discount" else pd.to_numeric(mism[c], errors="coerce").mean()
            b = pct(others[c]).mean() if key == "discount" else pd.to_numeric(others[c], errors="coerce").mean()
            if pd.notna(a) and pd.notna(b):
                unit = " pts" if key == "discount" else ""
                row2.append(kpi_html(lab, f"{a - b:+{f}}{unit}", "mismatched vs well placed",
                                     "bad" if (a - b) * (1 if key == "discount" else -1) > 0 else "good"))
    for row in (row1, row2):
        for col, html in zip(st.columns(len(row)), row):
            md_html(html, col)

    # Charts
    md_html('<div class="bi-group">Where the leakage sits</div>')
    c1, c2, c3 = st.columns(3)
    if cols["cat"]:
        g = d.groupby(cols["cat"])["_loss"].sum().nlargest(8).sort_values().reset_index()
        fig = px.bar(g, x="_loss", y=cols["cat"], orientation="h", title="Leakage by category",
                     color_discrete_sequence=["#8F1D2C"])
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        with c1:
            plot(fig)
    if cols["segment"]:
        g = d.groupby(cols["segment"])["_loss"].sum().reset_index()
        fig = px.bar(g, x=cols["segment"], y="_loss", color=cols["segment"],
                     color_discrete_map=SEG_COLORS, title="Leakage by placed segment")
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
        with c2:
            plot(fig)
    g = d.groupby("_primary")["_loss"].sum().sort_values().reset_index()
    fig = px.bar(g, x="_loss", y="_primary", orientation="h", title="Leakage by primary fix",
                 color_discrete_sequence=["#E07B1F"])
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    with c3:
        plot(fig)

    # Product level view
    md_html('<div class="bi-group">Product level diagnosis</div>')
    sorts = {"Revenue leakage (highest)": ("_loss", False)}
    for lab, key, asc in (("Trust score (lowest)", "_trust", True), ("Rating (lowest)", "_rating", True),
                          ("Discount (highest)", "_disc", False)):
        if d[key].notna().any():
            sorts[lab] = (key, asc)
    f1, f2, f3, f4, f5 = st.columns([1.2, 1.4, 1.4, 1.6, 1])
    sev_f = f1.selectbox("Severity", ["All", "Critical", "High", "Moderate"])
    cat_opts = ["All"] + (sorted(d[cols["cat"]].dropna().unique().tolist()) if cols["cat"] else [])
    cat_f = f2.selectbox("Category", cat_opts)
    sort_f = f3.selectbox("Sort by", list(sorts.keys()))
    q = f4.text_input("Search title")
    top_n = f5.number_input("Show", 5, 100, 10, step=5)

    view = d
    if sev_f != "All":
        view = view[view["_sev"] == sev_f]
    if cat_f != "All" and cols["cat"]:
        view = view[view[cols["cat"]] == cat_f]
    if q and cols["title"]:
        view = view[view[cols["title"]].astype(str).str.contains(q, case=False, na=False, regex=False)]
    key, asc = sorts[sort_f]
    view = view.sort_values(key, ascending=asc, na_position="last")

    st.caption(f"Showing {min(int(top_n), len(view))} of {len(view):,} matching products.")
    if view.empty:
        st.info("No products match these filters.")
    for i in view.index[: int(top_n)]:
        card(d.loc[i], recs[i], d.at[i, "_sev"], cols)

    with st.expander("Data mapping used by this page"):
        rows = [(k, v if v else "not found") for k, v in cols.items()]
        rows.append(("SHAP detail", "aligned" if sh is not None else "not available"))
        st.dataframe(pd.DataFrame(rows, columns=["field", "column"]), hide_index=True)
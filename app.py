"""
app.py - Buyer Intent Intelligence Platform
Entry point: page config, theme, sidebar navigation, filters, KPI strip, routing.
"""

import streamlit as st

st.set_page_config(
    page_title="Buyer Intent Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.style import CSS, SEG_COLORS, SEG_ICONS, fmt_inr
from utils.data_loader import load_all, load_shap, apply_filters
from utils.theme import THEME_CSS, apply_palette, md_html, kpi_html

apply_palette(SEG_COLORS, SEG_ICONS)
st.markdown(CSS, unsafe_allow_html=True)
md_html(THEME_CSS)

feat, imp = load_all("data")
shap_df = load_shap("data")

total_products = len(feat)
total_uplift = feat["revenue_uplift"].sum()
total_leakage = feat["mismatch_revenue_loss"].sum()
n_mismatched = int(feat["mismatch_flag"].sum())

PAGES = {
    "Home": "Executive overview of the catalogue and the key findings.",
    "Market Intelligence": "Segment distribution, revenue landscape and placement quality.",
    "ML Engine Room": "Model performance, validation and training diagnostics.",
    "Explainability Studio": "SHAP drivers behind every classification.",
    "Mismatch Alerts": "Products whose placement does not match buyer intent, with a fix for each.",
    "Buyer DNA": "Buyer archetypes, fingerprints and top products.",
    "Product Intelligence": "Search any product, decode its classification and simulate upgrades.",
}

with st.sidebar:
    md_html(
        """
        <div class="brand-mark">
          <div class="brand-icon">BI</div>
          <div>
            <div class="brand-text-main">Buyer Intent</div>
            <div class="brand-text-sub">Intelligence Platform</div>
          </div>
        </div>
        """
    )

    md_html('<span class="nav-label">Navigation</span>')
    page = st.radio("Page", list(PAGES.keys()), label_visibility="collapsed")

    st.markdown("---")
    md_html('<span class="nav-label">Filter: Category</span>')
    all_cats = sorted(feat["top_cat"].dropna().unique().tolist())
    sel_cats = st.multiselect("Category", all_cats, default=all_cats, label_visibility="collapsed")

    md_html('<span class="nav-label">Filter: Segment</span>')
    all_segs = list(SEG_COLORS.keys())
    default_segs = [s for s in all_segs if s != "UNMATCHED"]
    sel_segs = st.multiselect("Segment", all_segs, default=default_segs, label_visibility="collapsed")

    st.markdown("---")
    md_html('<span class="nav-label">Dataset Stats</span>')
    stats = [
        (f"{total_products:,}", "Total products"),
        (f"{len(SEG_COLORS)}", "Buyer segments"),
        (f"{n_mismatched:,}", "Mismatched products"),
        (fmt_inr(total_uplift), "Revenue opportunity"),
        (fmt_inr(total_leakage), "Mismatch leakage"),
    ]
    md_html(
        "".join(
            f'<div class="sidebar-stat"><div class="sidebar-stat-val">{v}</div>'
            f'<div class="sidebar-stat-label">{l}</div></div>'
            for v, l in stats
        )
    )

filtered_feat = apply_filters(feat, sel_cats, sel_segs)
filtered_imp = apply_filters(imp, sel_cats, sel_segs, cat_col="top_cat", seg_col="segment")

md_html(
    f'<div class="bi-hero"><div class="bi-hero-t">{page}</div>'
    f'<div class="bi-hero-s">{PAGES[page]}</div></div>'
)


def render_kpis(df):
    n = len(df)
    if n == 0:
        st.info("No products match the current filters.")
        return
    mism = int(df["mismatch_flag"].sum())
    rate = mism / n * 100
    uplift = df["revenue_uplift"].sum()
    leak = df["mismatch_revenue_loss"].sum()
    leak_share = (leak / uplift * 100) if uplift else 0
    top_cat = (
        df.groupby("top_cat")["revenue_uplift"].sum().idxmax()
        if df["top_cat"].notna().any()
        else "n/a"
    )
    cards = [
        kpi_html("Products in view", f"{n:,}", f"of {total_products:,} total"),
        kpi_html("Mismatch rate", f"{rate:.1f}%", f"{mism:,} products flagged",
                 "bad" if rate > 30 else "warn"),
        kpi_html("Revenue opportunity", fmt_inr(uplift), "projected uplift", "good"),
        kpi_html("Mismatch leakage", fmt_inr(leak), f"{leak_share:.1f}% of opportunity", "bad"),
        kpi_html("Avg uplift per product", fmt_inr(uplift / n), "across filtered set", "brand"),
        kpi_html("Top category", str(top_cat), "by revenue uplift"),
    ]
    for col, card in zip(st.columns(len(cards)), cards):
        md_html(card, col)


if page != "Mismatch Alerts":
    render_kpis(filtered_feat)

if page == "Home":
    from pages.p0_home import render
elif page == "Market Intelligence":
    from pages.p1_market import render
elif page == "ML Engine Room":
    from pages.p2_model import render
elif page == "Explainability Studio":
    from pages.p3_shap import render
elif page == "Mismatch Alerts":
    from pages.p4_mismatch import render
elif page == "Buyer DNA":
    from pages.p5_dna import render
else:
    from pages.p6_product import render

try:
    render(feat, imp, filtered_feat, filtered_imp, shap_df)
except Exception as exc:
    st.error(f"This page could not be rendered: {exc}")
    with st.expander("Technical details"):
        st.exception(exc)
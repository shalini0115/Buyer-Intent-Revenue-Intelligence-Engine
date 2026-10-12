"""utils/theme.py - shared design system: palette, CSS, Plotly template, HTML helpers."""

import html as _html
import re

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

SEG_PALETTE = {
    "DEAL_SEEKER": "#E07B1F",
    "QUALITY_FIRST": "#8F1D2C",
    "SOCIAL_PROOF": "#2F5D7C",
    "NICHE_EXPLORER": "#6B8F5E",
    "UNMATCHED": "#B9B0A6",
}
COLORWAY = ["#8F1D2C", "#E07B1F", "#2F5D7C", "#6B8F5E", "#B9B0A6", "#C8502A", "#7A6E65"]


def apply_palette(seg_colors, seg_icons):
    """Recolor shared segment dictionaries in place so every page picks them up."""
    if isinstance(seg_colors, dict):
        for k, v in SEG_PALETTE.items():
            if k in seg_colors:
                seg_colors[k] = v
    if isinstance(seg_icons, dict):
        for k in list(seg_icons.keys()):
            seg_icons[k] = ""

    axis = dict(gridcolor="#EFE8E0", linecolor="#E0D6CB", zerolinecolor="#E0D6CB")
    tpl = go.layout.Template()
    tpl.layout = go.Layout(
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#3B3029"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=COLORWAY,
        title=dict(font=dict(size=14, color="#241C17"), x=0.0),
        xaxis=axis,
        yaxis=axis,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    pio.templates["bi"] = tpl
    pio.templates.default = "bi"


def flat(s):
    """Collapse HTML to one line. Single-line HTML can never render as a markdown code block."""
    return re.sub(r">\s+<", "><", " ".join(s.split()))


def md_html(s, target=None):
    (target or st).markdown(flat(s), unsafe_allow_html=True)


def esc(x):
    return _html.escape(str(x))


def kpi_html(label, value, sub="", tone=""):
    return flat(
        f'<div class="bi-kpi {tone}"><div class="bi-kpi-l">{esc(label)}</div>'
        f'<div class="bi-kpi-v">{esc(value)}</div><div class="bi-kpi-s">{esc(sub)}</div></div>'
    )


THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@500;600;700&display=swap');
:root{--bg:#FBF8F4;--card:#FFFFFF;--cream:#FFF6EE;--line:#E8DFD5;--ink:#241C17;--muted:#7A6E65;
--maroon:#8F1D2C;--orange:#E07B1F;--good:#3F7D4E;--warn:#D98A1C;--bad:#B3261E;--slate:#3D4A5C;}

html, body, .stApp, [data-testid="stAppViewContainer"]{background:var(--bg) !important;color:var(--ink) !important;}
.stApp, .stMarkdown, p, label, li, input, button, textarea, [data-baseweb]{font-family:'Inter',Arial,sans-serif;}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, label{color:var(--ink);}
h1,h2,h3{font-family:'Source Serif 4',Georgia,serif !important;color:var(--ink) !important;letter-spacing:-0.01em;}
[data-testid="stHeader"]{background:transparent !important;}
[data-testid="stSidebarNav"]{display:none !important;}
.block-container{padding-top:1.4rem !important;max-width:1400px;}
hr{border:none !important;border-top:1px solid var(--line) !important;margin:1rem 0 !important;}

[data-testid="stSidebar"]{background:var(--card) !important;border-right:1px solid var(--line);}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p{color:var(--ink);}
.brand-mark{display:flex;align-items:center;gap:12px;padding:4px 0 14px 0;}
.brand-icon{width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#8F1D2C,#E07B1F);
color:#fff !important;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;}
.brand-text-main{font-weight:700;font-size:15px;color:var(--ink) !important;}
.brand-text-sub{font-size:12px;color:var(--muted) !important;}
.nav-label{display:block;font-size:11px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;
color:var(--muted) !important;margin:8px 0 6px 0;}
.sidebar-stat{background:var(--cream);border:1px solid var(--line);border-left:3px solid var(--maroon);
border-radius:8px;padding:9px 12px;margin-bottom:8px;}
.sidebar-stat-val{font-size:17px;font-weight:700;color:var(--maroon) !important;}
.sidebar-stat-label{font-size:11px;color:var(--muted) !important;text-transform:uppercase;letter-spacing:.05em;}

[data-testid="stSidebar"] [role="radiogroup"]{gap:2px;}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:8px 12px;border-radius:8px;width:100%;cursor:pointer;}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child{display:none;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:var(--cream);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:var(--cream);box-shadow:inset 3px 0 0 var(--maroon);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p{color:var(--maroon);font-weight:600;}

[data-baseweb="select"] > div, [data-baseweb="input"] > div, .stTextInput input{
background:#FFFFFF !important;border:1px solid var(--line) !important;border-radius:8px !important;color:var(--ink) !important;}
[data-baseweb="select"] *{color:var(--ink) !important;}
[data-baseweb="tag"]{background:#F6E3D3 !important;border-radius:6px !important;}
[data-baseweb="tag"] span, [data-baseweb="tag"] svg{color:#8F1D2C !important;fill:#8F1D2C !important;}
[data-baseweb="popover"] ul, [data-baseweb="menu"]{background:#FFFFFF !important;}
[data-baseweb="popover"] li{color:var(--ink) !important;}
[data-baseweb="popover"] li:hover{background:var(--cream) !important;}

pre, code{background:#F4EEE8 !important;color:#3B2A22 !important;border-radius:6px;}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;}
[data-testid="stMetricLabel"] *{color:var(--muted) !important;}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;overflow:hidden;}
.stTabs [data-baseweb="tab-list"]{gap:6px;border-bottom:1px solid var(--line);}
.stTabs [aria-selected="true"]{color:var(--maroon) !important;}
.stButton > button{background:var(--maroon);color:#fff !important;border:none;border-radius:8px;font-weight:600;}
.stButton > button:hover{background:#731724;}

.bi-hero{background:linear-gradient(90deg,#8F1D2C,#E07B1F);padding:22px 28px;border-radius:14px;margin-bottom:18px;}
.bi-hero-t{font-family:'Source Serif 4',Georgia,serif;color:#fff !important;font-size:1.9rem;font-weight:600;}
.bi-hero-s{color:#FFE9D6 !important;margin-top:4px;font-size:.95rem;}

.bi-kpi{background:var(--cream);border:1px solid var(--line);border-left:5px solid var(--slate);
border-radius:10px;padding:12px 14px;margin-bottom:12px;height:100%;}
.bi-kpi.good{border-left-color:var(--good);} .bi-kpi.warn{border-left-color:var(--warn);}
.bi-kpi.bad{border-left-color:var(--bad);} .bi-kpi.brand{border-left-color:var(--maroon);}
.bi-kpi-l{font-size:.72rem;color:var(--muted) !important;text-transform:uppercase;letter-spacing:.05em;font-weight:600;}
.bi-kpi-v{font-size:1.45rem;font-weight:700;color:var(--ink) !important;line-height:1.3;font-variant-numeric:tabular-nums;}
.bi-kpi-s{font-size:.75rem;color:var(--muted) !important;}

.bi-sec{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted) !important;font-weight:600;margin:4px 0 2px 0;}
.bi-h{font-family:'Source Serif 4',Georgia,serif;font-size:1.7rem;font-weight:600;color:var(--ink) !important;margin:0;}
.bi-sub{color:var(--muted) !important;font-size:.95rem;margin:2px 0 16px 0;}
.bi-group{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--maroon) !important;font-weight:700;margin:18px 0 10px 0;}

.bi-card{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--slate);border-radius:12px;
padding:18px 20px;margin:0 0 14px 0;box-shadow:0 1px 2px rgba(36,28,23,.04);}
.bi-card.sev-critical{border-left-color:var(--bad);} .bi-card.sev-high{border-left-color:var(--warn);}
.bi-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;}
.bi-title{font-weight:600;font-size:15px;line-height:1.45;color:var(--ink) !important;}
.bi-loss{white-space:nowrap;font-weight:700;color:var(--bad) !important;font-size:16px;text-align:right;}
.bi-loss small{display:block;font-weight:500;color:var(--muted) !important;font-size:11px;}
.bi-chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 14px 0;}
.bi-chip{font-size:12px;padding:3px 10px;border-radius:999px;background:#F4EEE8;color:#4A3F37 !important;border:1px solid var(--line);}
.bi-split{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;}
.bi-box{border-radius:10px;padding:10px 12px;border:1px solid var(--line);background:var(--bg);}
.bi-box.push{border-left:3px solid var(--good);} .bi-box.barrier{border-left:3px solid var(--bad);}
.bi-box-l{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted) !important;font-weight:600;}
.bi-box-f{font-size:14px;font-weight:600;margin-top:3px;color:var(--ink) !important;}
.bi-box-v{font-size:12px;color:var(--muted) !important;font-variant-numeric:tabular-nums;}
.bi-fixes-l{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--maroon) !important;font-weight:700;}
.bi-fixes{margin:6px 0 0 18px;padding:0;}
.bi-fixes li{margin-bottom:7px;font-size:13.5px;line-height:1.55;color:#3B3029 !important;}
.bi-fixes li b{color:var(--ink);}
@media (max-width: 800px){.bi-split{grid-template-columns:1fr;}}
</style>
"""
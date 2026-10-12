"""
animations.py — Animation utilities for dashboard cards and charts
"""

from html import escape


def kpi_card_animated(
    label: str,
    value: str,
    subtitle: str,
    color: str = "orange",
    card_index: int = 0,
) -> str:
    """Build a KPI card without embedding executable JavaScript in the markup."""
    stagger_delay = max(0, card_index) * 100
    return f"""
    <div class="kpi-card c-{escape(color)} kpi-enhanced"
         style="--stagger-delay: {stagger_delay}ms;">
      <div class="kpi-glow-effect"></div>
      <div class="kc-label">{escape(str(label))}</div>
      <div class="kc-val">{escape(str(value))}</div>
      <div class="kc-sub">{escape(str(subtitle))}</div>
    </div>
    """


def animated_plotly_config():
    """Return responsive Plotly config without the mode bar logo."""
    return {
        "responsive": True,
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {
            "format": "png",
            "filename": "chart",
            "height": 600,
            "width": 1200,
            "scale": 2,
        },
    }

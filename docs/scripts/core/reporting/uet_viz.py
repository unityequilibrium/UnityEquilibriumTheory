import os
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path


# Ensure Result directory exists relative to caller or specified path
def save_plot(fig, filename, result_dir):
    Path(result_dir).mkdir(parents=True, exist_ok=True)

    # Force extension to .png
    if filename.endswith(".html"):
        filename = filename.replace(".html", ".png")
    elif not filename.endswith(".png"):
        filename += ".png"

    path = Path(result_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Use Kaleido for static image
        fig.write_image(str(path), scale=2)  # scale=2 for higher res
        print(f"  [Plot Saved]: {path}")
        return path
    except Exception as e:
        print(f"  [Plot Error]: Could not save {filename}. Error: {e}")
        return None


def plot_galaxy_curve(r_kpc, v_obs, v_bar, v_uet, title, output_dir):
    """Plots Galaxy Rotation Curve: Obs vs Newton vs UET."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=r_kpc, y=v_obs, mode="markers", name="Observed (SPARC)", marker=dict(color="black")
        )
    )
    fig.add_trace(
        go.Scatter(
            x=r_kpc,
            y=v_bar,
            mode="lines",
            name="Newtonian (Baryonic)",
            line=dict(color="blue", dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=r_kpc, y=v_uet, mode="lines", name="UET Prediction", line=dict(color="red", width=3)
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Radius (kpc)",
        yaxis_title="Velocity (km/s)",
        template="plotly_white",
        width=1000,
        height=600,
    )
    save_plot(fig, "rotation_curve.html", output_dir)


def plot_universal_trend(x_data, y_data, x_label, y_label, title, filename, output_dir):
    """Generic Scatter Plot."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_data, y=y_data, mode="markers+lines", name="Data"))
    fig.update_layout(
        title=title, xaxis_title=x_label, yaxis_title=y_label, template="plotly_white"
    )
    save_plot(fig, filename, output_dir)


def plot_comparison(categories, values_legacy, values_uet, values_obs, title, output_dir):
    """Bar Chart Comparison."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=categories, y=values_legacy, name="Legacy Theory", marker_color="gray"))
    fig.add_trace(go.Bar(x=categories, y=values_uet, name="UET Theory", marker_color="blue"))
    fig.add_trace(go.Bar(x=categories, y=values_obs, name="Observation", marker_color="green"))

    fig.update_layout(title=title, barmode="group", template="plotly_white")
    save_plot(fig, "comparison_chart.html", output_dir)

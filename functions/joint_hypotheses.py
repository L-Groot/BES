import itertools
from typing import Dict, List, Sequence
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from functions.color_palette import hypothesis_palette as palette

def plotly_color(color: str) -> str:
    """Convert #RRGGBBAA to #RRGGBB for Plotly compatibility."""
    if isinstance(color, str) and color.startswith("#") and len(color) == 9:
        return color[:7]
    return color


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert #RRGGBB or #RRGGBBAA to an rgba(...) string with custom alpha."""
    hex_clean = plotly_color(hex_color).lstrip("#")
    if len(hex_clean) < 6:
        raise ValueError(f"Invalid color: {hex_color}")
    r = int(hex_clean[0:2], 16)
    g = int(hex_clean[2:4], 16)
    b = int(hex_clean[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def create_cube(xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float) -> pd.DataFrame:
    """Create cube vertices in R expand.grid order (x fastest, then y, then z)."""
    rows = []
    for z in (zmin, zmax):
        for y in (ymin, ymax):
            for x in (xmin, xmax):
                rows.append((x, y, z))
    return pd.DataFrame(rows, columns=["x", "y", "z"])


def add_cube_edges(
    fig: go.Figure,
    cube: pd.DataFrame,
    color: str,
    width: int = 4,
    opacity: float = 0.5,
    dash: str = "solid",
) -> go.Figure:
    color = plotly_color(color)
    edges = [
        (1, 2), (1, 3), (1, 5),
        (2, 4), (2, 6),
        (3, 4), (3, 7),
        (4, 8),
        (5, 6), (5, 7),
        (6, 8),
        (7, 8),
    ]

    for a, b in edges:
        idx = [a - 1, b - 1]
        fig.add_trace(
            go.Scatter3d(
                x=cube.loc[idx, "x"],
                y=cube.loc[idx, "y"],
                z=cube.loc[idx, "z"],
                mode="lines",
                line={"color": color, "width": width, "dash": dash},
                opacity=opacity,
                showlegend=False,
            )
        )

    return fig


def add_h0_marker(fig: go.Figure, h0: Sequence[float], xmin: float, color: str) -> go.Figure:
    color = plotly_color(color)
    x0, y0, z0 = h0

    n = 15
    seg1 = pd.DataFrame({
        "x": [x0] * n,
        "y": [xmin + i * (y0 - xmin) / (n - 1) for i in range(n)],
        "z": [xmin] * n,
    })
    seg2 = pd.DataFrame({
        "x": [x0] * n,
        "y": [y0] * n,
        "z": [xmin + i * (z0 - xmin) / (n - 1) for i in range(n)],
    })
    guide_dots = pd.concat([seg1, seg2], ignore_index=True)

    fig.add_trace(
        go.Scatter3d(
            x=guide_dots["x"],
            y=guide_dots["y"],
            z=guide_dots["z"],
            mode="markers",
            marker={"size": 3, "color": color, "opacity": 0.9},
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[x0],
            y=[y0],
            z=[z0],
            mode="markers",
            marker={"size": 8, "color": color, "opacity": 0.9},
            name="H0",
            showlegend=False,
        )
    )

    return fig


def add_cube_mesh(fig: go.Figure, cube: pd.DataFrame, color: str, opacity: float = 0.4, alpha_min: float = 0.2, alpha_max: float = 0.5) -> go.Figure:
    color = plotly_color(color)
    #face_alphas = [0.35 + i * (0.8 - 0.35) / 11 for i in range(12)]
    #face_alphas = [alpha_min + i * (alpha_max - alpha_min) / 11 for i in range(12)]
    face_alphas = [alpha_max] * 12  # All faces use max alpha
    face_colors = [hex_to_rgba(color, a) for a in face_alphas]

    fig.add_trace(
        go.Mesh3d(
            x=cube["x"],
            y=cube["y"],
            z=cube["z"],
            i=[0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6],
            j=[1, 2, 3, 2, 5, 3, 6, 7, 5, 6, 6, 7],
            k=[2, 3, 1, 5, 6, 6, 7, 4, 6, 7, 7, 4],
            facecolor=face_colors,
            opacity=opacity,
            flatshading=False,
            showscale=False,
            #alphahull=5,
        )
    )

    return fig


def build_segments_single_study(xlo: float, xhi: float, h1_xmin: float, h1_xmax: float) -> pd.DataFrame:
    if xhi > h1_xmax and xlo < h1_xmin:
        return pd.DataFrame(
            {
                "xmin": [xlo, xlo, h1_xmax, h1_xmin],
                "xmax": [xhi, h1_xmin, xhi, h1_xmax],
                "y": [1.5, 1, 1, 0.5],
                "hypothesis": ["Hu", "Hc", "Hc", "H1"],
            }
        )

    if xlo == h1_xmin and xhi != h1_xmax:
        hc_xmin, hc_xmax = h1_xmax, xhi
    elif xhi == h1_xmax and xlo != h1_xmin:
        hc_xmin, hc_xmax = xlo, h1_xmin
    else:
        raise ValueError("invalid configuration")

    return pd.DataFrame(
        {
            "xmin": [xlo, hc_xmin, h1_xmin],
            "xmax": [xhi, hc_xmax, h1_xmax],
            "y": [1.5, 1, 0.5],
            "hypothesis": ["Hu", "Hc", "H1"],
        }
    )


def create_hc_h1_cubes_list(
    xmin: float = 0,
    xmax: float = 1,
    h1_min: Sequence[float] = (0.5, 0.5, 0.5),
    h1_max: Sequence[float] = (1, 1, 1),
) -> List[List[Dict[str, float]]]:
    """Per-study list of components: hc_1/hc_2/hc and h1 as final component."""
    out = []
    for i in range(len(h1_min)):
        h1 = {"LB": h1_min[i], "UB": h1_max[i]}

        if xmax > h1_max[i] and xmin < h1_min[i]:
            comp1 = {"LB": xmin, "UB": h1_min[i]}
            comp2 = {"LB": h1_max[i], "UB": xmax}
            out.append([comp1, comp2, h1])
        else:
            if xmin < h1_min[i]:
                hc = {"LB": xmin, "UB": h1_min[i]}
            elif xmax > h1_max[i]:
                hc = {"LB": h1_max[i], "UB": xmax}
            else:
                raise ValueError("faulty logic, this should not happen")
            out.append([hc, h1])

    return out


def _cubes_from_component_combos(
    hc_h1_list: List[List[Dict[str, float]]],
    combos: List[Sequence[int]],
) -> List[pd.DataFrame]:
    cubes = []
    for combo in combos:
        bounds = []
        for study_idx, comp_idx in enumerate(combo):
            comp = hc_h1_list[study_idx][comp_idx]
            bounds.append((comp["LB"], comp["UB"]))

        cubes.append(
            create_cube(
                bounds[0][0], bounds[0][1],
                bounds[1][0], bounds[1][1],
                bounds[2][0], bounds[2][1],
            )
        )
    return cubes


def create_hc_cubes_incomplete(xmin: float, xmax: float, h1_min: Sequence[float], h1_max: Sequence[float]) -> List[pd.DataFrame]:
    hc_h1_list = create_hc_h1_cubes_list(xmin, xmax, h1_min, h1_max)
    comp_counts = [len(study) for study in hc_h1_list]

    all_combos = list(itertools.product(*[range(n) for n in comp_counts]))
    combos = [
        c
        for c in all_combos
        if not any(c[i] == comp_counts[i] - 1 for i in range(len(c)))
    ]

    return _cubes_from_component_combos(hc_h1_list, combos)

def create_hc_cubes_complete(xmin: float, xmax: float, h1_min: Sequence[float], h1_max: Sequence[float]) -> List[pd.DataFrame]:
    hc_h1_list = create_hc_h1_cubes_list(xmin, xmax, h1_min, h1_max)
    comp_counts = [len(study) for study in hc_h1_list]

    all_combos = list(itertools.product(*[range(n) for n in comp_counts]))
    combos = [
        c
        for c in all_combos
        if not all(c[i] == comp_counts[i] - 1 for i in range(len(c)))
    ]

    return _cubes_from_component_combos(hc_h1_list, combos)


def add_axis_segments(
    fig: go.Figure,
    seg_df: pd.DataFrame,
    xmin: float,
    offset: float,
    colors_map: Dict[str, str],
    xmax: float,
) -> go.Figure:
    for _, seg in seg_df.iterrows():
        col = plotly_color(colors_map[seg["hypothesis"]])
        axis = int(seg["axis"])

        if axis == 1:
            x = [seg["xmin"], seg["xmax"]]
            y = [xmin - offset, xmin - offset]
            z = [xmin, xmin]
        elif axis == 2:
            x = [xmin - offset, xmin - offset]
            y = [seg["xmin"], seg["xmax"]]
            z = [xmin, xmin]
        elif axis == 3:
            x = [xmin - offset, xmin - offset]
            y = [xmax + offset, xmax + offset]
            z = [seg["xmin"], seg["xmax"]]
        else:
            continue

        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                line={"color": col, "width": 8},
                showlegend=False,
            )
        )

    return fig


def plot_hypothesis_cube(
    xmin: float = 0,
    xmax: float = 1,
    h1_min: Sequence[float] = (0.5, 0.5, 0.5),
    h1_max: Sequence[float] = (1, 1, 1),
    h0: Sequence[float] = (0.5, 0.5, 0.5),
    title: str = "",
    tickvals_x: Sequence[float] = (0, 0.5, 1),
    tickvals_y: Sequence[float] = (0, 0.5, 1),
    tickvals_z: Sequence[float] = (0, 0.5, 1),
    plot_h1: bool = True,
    plot_hc_incomplete: bool = True,
    plot_hc_complete: bool = False,
    plot_h0: bool = True,
    plot_hu: bool = False,
) -> go.Figure:
    if plot_hc_incomplete and plot_hc_complete:
        raise ValueError("Can't plot both incomplete AND complete Hc in one plot")

    if (plot_hc_incomplete or plot_hc_complete) and plot_hu:
        raise ValueError("Can't plot Hc and Hu together")

    segments_list = []
    for i in range(3):
        seg = build_segments_single_study(xlo=xmin, xhi=xmax, h1_xmin=h1_min[i], h1_xmax=h1_max[i]).copy()
        seg["axis"] = i + 1
        segments_list.append(seg)

    segments_all = pd.concat(segments_list, ignore_index=True)
    seg_filtered = segments_all[segments_all["hypothesis"].isin(["Hu", "H1", "Hc"])]

    by_hyp = {k: v.copy() for k, v in seg_filtered.groupby("hypothesis")}
    segments_hu = by_hyp.get("Hu", pd.DataFrame(columns=seg_filtered.columns))
    segments_h1 = by_hyp.get("H1", pd.DataFrame(columns=seg_filtered.columns))
    segments_hc = by_hyp.get("Hc", pd.DataFrame(columns=seg_filtered.columns))

    cube_full = create_cube(xmin, xmax, xmin, xmax, xmin, xmax)
    cube_h1 = create_cube(h1_min[0], h1_max[0], h1_min[1], h1_max[1], h1_min[2], h1_max[2])

    cubes_hc = []
    if plot_hc_complete and not plot_hc_incomplete:
        cubes_hc = create_hc_cubes_complete(xmin, xmax, h1_min, h1_max)
    elif (not plot_hc_complete) and plot_hc_incomplete:
        cubes_hc = create_hc_cubes_incomplete(xmin, xmax, h1_min, h1_max)

    fig = go.Figure()
    # Add dashed outline for full cube
    fig = add_cube_edges(fig, cube_full, "black", width=5, dash="dash")

    # Add Hu
    if plot_hu:
        fig = add_cube_mesh(fig, cube_full, palette["Hu"], opacity=0.4, alpha_min=0.5, alpha_max=0.8)

    # Add Hc
    if plot_hc_incomplete or plot_hc_complete:
        for cube in cubes_hc:
            #fig = add_cube_mesh(fig, cube, palette["Hc"], opacity=0.2)
            #fig = add_cube_edges(fig, cube, palette["Hc"], width=4, opacity=0.3)
            fig = add_cube_mesh(fig, cube, palette["Hc"], opacity=0.3, alpha_min=0.3, alpha_max=0.4)
            fig = add_cube_edges(fig, cube, palette["Hc"], width=4, opacity=0.3)

    # Add H1
    if plot_h1:
        fig = add_cube_mesh(fig, cube_h1, palette["H1"], opacity=0.8, alpha_min=0.8, alpha_max=0.9)
        fig = add_cube_edges(fig, cube_h1, palette["H1"], width=4, opacity=0.9)

    axis_offset_h1_hc = (xmax - xmin) * 0.05
    axis_offset_hu = (xmax - xmin) * 0.10

    # H1 is always drawn on axis-side guides.
    fig = add_axis_segments(fig, segments_h1, xmin, axis_offset_h1_hc, palette, xmax)

    # Draw Hu side guides only when Hu is plotted; otherwise draw Hc on same guide as H1.
    if plot_hu:
        fig = add_axis_segments(fig, segments_hu, xmin, axis_offset_hu, palette, xmax)
    elif plot_hc_incomplete or plot_hc_complete:
        fig = add_axis_segments(fig, segments_hc, xmin, axis_offset_h1_hc, palette, xmax)

    # Always use the Hu offset for the axis range so all cube plots have the same dimensions.
    buffer = axis_offset_hu * 1.05

    # Add H0 marker
    if plot_h0:
        fig = add_h0_marker(fig, h0, xmin, palette["H0"])

    axis_title_font = {
        "size": 18,
        "family": "Arial",
        "color": "black",
    }

    fig.update_layout(
        title=title,
        scene={
            "aspectmode": "cube",
            "xaxis": {
                "title": {"text": "θ₁", "font": axis_title_font},
                "range": [xmin - buffer, xmax + buffer],
                "tickvals": list(tickvals_x),
                "tickmode": "array",
                "gridcolor": "lightgray",
                "showbackground": False,
                "zeroline": False,
            },
            "yaxis": {
                "title": {"text": "θ₂", "font": axis_title_font},
                "range": [xmin - buffer, xmax + buffer],
                "tickvals": list(tickvals_y),
                "tickmode": "array",
                "gridcolor": "lightgray",
                "showbackground": False,
                "zeroline": False,
            },
            "zaxis": {
                "title": {"text": "θ₃", "font": axis_title_font},
                "range": [xmin, xmax],
                "tickvals": list(tickvals_z),
                "tickmode": "array",
                "gridcolor": "lightgray",
                "showbackground": False,
                "zeroline": False,
            },
        },
    )

    return fig


if __name__ == "__main__":
    # --- Example A: Choice probabilities ---

    # A1: H1 + "incomplete" Hc
    fig = plot_hypothesis_cube()
    fig.update_layout(title="A1: Choice probabilities – H1 + incomplete Hc")
    fig.show()

    # A2: H1 + "complete" Hc
    fig = plot_hypothesis_cube(plot_hc_incomplete=False, plot_hc_complete=True)
    fig.update_layout(title="A2: Choice probabilities – H1 + complete Hc")
    fig.show()

    # A3: H1 + Hu
    fig = plot_hypothesis_cube(plot_hc_incomplete=False, plot_hu=True)
    fig.update_layout(title="A3: Choice probabilities – H1 + Hu")
    fig.show()

    # --- Example B: Equivalence Testing ---

    # B1: H1 + "incomplete" Hc
    fig = plot_hypothesis_cube(
        xmin=-1,
        xmax=1,
        h1_min=(-0.0625, -0.1, -0.2),
        h1_max=(0.0625, 0.1, 0.2),
        h0=(0, 0, 0),
        tickvals_x=(-1, -0.0625, 0, 0.0625, 1),
        tickvals_y=(-1, -0.1, 0, 0.1, 1),
        tickvals_z=(-1, -0.2, 0, 0.2, 1),
        plot_h1=True,
        plot_hc_incomplete=True,
        plot_hc_complete=False,
        plot_h0=True,
        plot_hu=False,
    )
    fig.update_layout(title="B1: Equivalence testing – H1 + incomplete Hc")
    fig.show()

    # B2: H1 + "complete" Hc
    fig = plot_hypothesis_cube(
        xmin=-1,
        xmax=1,
        h1_min=(-0.0625, -0.1, -0.2),
        h1_max=(0.0625, 0.1, 0.2),
        h0=(0, 0, 0),
        tickvals_x=(-1, -0.0625, 0, 0.0625, 1),
        tickvals_y=(-1, -0.1, 0, 0.1, 1),
        tickvals_z=(-1, -0.2, 0, 0.2, 1),
        plot_h1=True,
        plot_hc_incomplete=False,
        plot_hc_complete=True,
        plot_h0=True,
        plot_hu=False,
    )
    fig.update_layout(title="B2: Equivalence testing – H1 + complete Hc")
    fig.show()

    # B3: H1 + Hu
    fig = plot_hypothesis_cube(
        xmin=-1,
        xmax=1,
        h1_min=(-0.0625, -0.1, -0.2),
        h1_max=(0.0625, 0.1, 0.2),
        h0=(0, 0, 0),
        tickvals_x=(-1, -0.0625, 0, 0.0625, 1),
        tickvals_y=(-1, -0.1, 0, 0.1, 1),
        tickvals_z=(-1, -0.2, 0, 0.2, 1),
        plot_h1=True,
        plot_hc_incomplete=False,
        plot_hc_complete=False,
        plot_h0=True,
        plot_hu=True,
    )
    fig.update_layout(title="B3: Equivalence testing – H1 + Hu")
    fig.show()

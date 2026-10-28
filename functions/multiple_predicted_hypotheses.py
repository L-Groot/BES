import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from pathlib import Path
import matplotlib as mpl
import matplotlib.colors as mcolors
from functions.color_palette import hypothesis_palette


# Plot window: keep 0 centered on both axes.
X_MIN, X_MAX = -1.0, 1.0
Y_MIN, Y_MAX = -1.0, 1.0

# Match palette style used in figure1/figure2 scripts (Classic_20 approximation).
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Arial"]
mpl.rcParams["font.size"] = 16

def _lighten_hex(color: str, amount: float) -> str:
    """Return a lighter shade of the given color while preserving hue."""
    r, g, b = mcolors.to_rgb(color)
    r = r + (1.0 - r) * amount
    g = g + (1.0 - g) * amount
    b = b + (1.0 - b) * amount
    return mcolors.to_hex((r, g, b))


DEFAULT_COLOR_LIGHTNESS = 0.0


def _get_region_colors(lightness: float = DEFAULT_COLOR_LIGHTNESS) -> tuple[str, str, str]:
    """Return (H2, Hc, H1) colors with configurable lightness."""
    amount = min(1.0, max(0.0, lightness))
    # color_h2 = _lighten_hex(hypothesis_palette["H2"], amount=amount)
    # color_hc = _lighten_hex(hypothesis_palette["Hc"], amount=amount)
    # color_h1 = _lighten_hex(hypothesis_palette["H1"], amount=amount)
    color_h2 = hypothesis_palette["H2"]
    color_hc = hypothesis_palette["Hc"]
    color_h1 = hypothesis_palette["H1"]
    return color_h2, color_hc, color_h1


BOUNDARY_COLOR = "#222222"
LABEL_COLOR = "#111111"

# Default output should match the main project figure layout, not a nested
# functions/figures directory created during module import.
OUT_DIR = Path(__file__).resolve().parent.parent / "plots" / "figure3"

BASE_FIG_WIDTH = 12.0
BASE_FIG_HEIGHT = 5.0
BASE_TICK_LABEL_SIZE = 15
BASE_AXIS_LABEL_SIZE = 19
BASE_TITLE_SIZE = 18
BASE_REGION_LABEL_SIZE = 18
BASE_NESTED_LABEL_SIZE = 17


def _add_diagonal_stripes(
    ax: plt.Axes,
    clip_rect: Rectangle,
    color_a: str,
    color_b: str,
    stripe_width: float = 0.16,
) -> None:
    """Draw alternating filled diagonal stripes clipped to a rectangle."""
    x0, y0 = clip_rect.get_xy()
    w = clip_rect.get_width()
    h = clip_rect.get_height()
    xmin = x0
    xmax = x0 + w
    ymin = y0
    ymax = y0 + h

    xs = [xmin, xmax]
    k = ymin - xmax
    i = 0
    while k <= ymax - xmin:
        color = color_a if i % 2 == 0 else color_b
        collection = ax.fill_between(
            xs,
            [x + k for x in xs],
            [x + k + stripe_width for x in xs],
            color=color,
            alpha=0.56,
            linewidth=0,
            zorder=2,
        )
        collection.set_clip_path(clip_rect)
        i += 1
        k += stripe_width


def _style_axes(ax: plt.Axes, title: str, axis_label_scale: float = 1.0, dash_coarseness: float = 1.0) -> None:
    """Apply a consistent style and axis annotations."""
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_aspect("equal", adjustable="box")

    # Remove default spines and draw custom axes.
    for spine in ax.spines.values():
        spine.set_visible(False)

    dash_len = max(0.4, 3.0 * dash_coarseness)
    dash_pattern = (0, (dash_len, dash_len))

    # beta axis: fixed endpoints (no arrowheads).
    ax.plot([X_MIN, X_MAX], [0, 0], color=BOUNDARY_COLOR, linewidth=1.5, linestyle=dash_pattern, zorder=5)

    # Hypothesis boundaries (vertical center line only).
    ax.plot([0, 0], [Y_MIN, Y_MAX], color=BOUNDARY_COLOR, linestyle=dash_pattern, linewidth=1.5, zorder=4)

    # sigma axis direction: separate arrowheads at both ends.
    head_span = 0.0
    tip_eps = 0.004 * (Y_MAX - Y_MIN)
    ax.annotate(
        "",
        xy=(0, Y_MAX + tip_eps),
        xytext=(0, Y_MAX - head_span),
        arrowprops=dict(arrowstyle="->", color=BOUNDARY_COLOR, lw=1.5, shrinkA=0, shrinkB=0),
        annotation_clip=False,
        zorder=7,
    )
    ax.annotate(
        "",
        xy=(0, Y_MIN - tip_eps),
        xytext=(0, Y_MIN + head_span),
        arrowprops=dict(arrowstyle="->", color=BOUNDARY_COLOR, lw=1.5, shrinkA=0, shrinkB=0),
        annotation_clip=False,
        zorder=7,
    )

    # Ticks with 0 centered.
    ax.set_xticks([X_MIN, 0, X_MAX])
    ax.set_yticks([0])
    ax.tick_params(axis="both", labelsize=BASE_TICK_LABEL_SIZE * axis_label_scale)
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", length=0)

    ax.set_xlabel(r"$\beta$", fontsize=BASE_AXIS_LABEL_SIZE * axis_label_scale, labelpad=14)
    ax.set_ylabel(r"$\sigma_{\alpha,\beta}$", fontsize=BASE_AXIS_LABEL_SIZE * axis_label_scale, labelpad=16)
    ax.set_title(title, fontsize=BASE_TITLE_SIZE * axis_label_scale, pad=26)


def plot_set_1(
    ax: plt.Axes,
    axis_label_scale: float = 1.0,
    hypothesis_label_scale: float = 1.0,
    dash_coarseness: float = 1.0,
    color_h2: str = hypothesis_palette["H2"],
    color_hc: str = hypothesis_palette["Hc"],
    color_h1: str = hypothesis_palette["H1"],
) -> None:
    """Set 1: H1 (beta>0, sigma>0), H2 (beta>0, sigma<0), Hc elsewhere."""
    # Hc region (left half-plane).
    ax.add_patch(
        Rectangle((X_MIN, Y_MIN), 0 - X_MIN, Y_MAX - Y_MIN, facecolor=color_hc, alpha=0.56, edgecolor="none")
    )

    # H1 region (top-right quadrant).
    ax.add_patch(
        Rectangle((0, 0), X_MAX - 0, Y_MAX - 0, facecolor=color_h1, alpha=0.56, edgecolor="none")
    )

    # H2 region (bottom-right quadrant).
    ax.add_patch(
        Rectangle((0, Y_MIN), X_MAX - 0, 0 - Y_MIN, facecolor=color_h2, alpha=0.56, edgecolor="none")
    )

    _style_axes(ax, "", axis_label_scale=axis_label_scale, dash_coarseness=dash_coarseness)

    ax.text(0.5, 0.5, r"$H_1$", ha="center", va="center", fontsize=BASE_REGION_LABEL_SIZE * hypothesis_label_scale, color=LABEL_COLOR, weight="bold")
    ax.text(0.5, -0.5, r"$H_2$", ha="center", va="center", fontsize=BASE_REGION_LABEL_SIZE * hypothesis_label_scale, color=LABEL_COLOR, weight="bold")
    ax.text(-0.5, 0.16, r"$H_c$", ha="center", va="center", fontsize=BASE_REGION_LABEL_SIZE * hypothesis_label_scale, color=LABEL_COLOR, weight="bold")



def plot_set_2(
    ax: plt.Axes,
    axis_label_scale: float = 1.0,
    hypothesis_label_scale: float = 1.0,
    dash_coarseness: float = 1.0,
    color_h2: str = hypothesis_palette["H2"],
    color_hc: str = hypothesis_palette["Hc"],
    color_h1: str = hypothesis_palette["H1"],
) -> None:
    """Set 2: H2 nested in H1 (H1: beta>0, H2: beta>0 and sigma<0)."""
    # Hc region (same area as set 1, visually: left half-plane).
    ax.add_patch(
        Rectangle((X_MIN, Y_MIN), 0 - X_MIN, Y_MAX - Y_MIN, facecolor=color_hc, alpha=0.56, edgecolor="none")
    )

    # H1 region outside the overlap with H2 (top-right quadrant only).
    ax.add_patch(
        Rectangle((0, 0), X_MAX - 0, Y_MAX - 0, facecolor=color_h1, alpha=0.56, edgecolor="none")
    )

    # H2 region (subset of H1, bottom-right): alternating filled stripes, no white gaps.
    nested_rect = Rectangle(
        (0, Y_MIN),
        X_MAX - 0,
        0 - Y_MIN,
        edgecolor="none",
        facecolor="none",
        linewidth=0,
    )
    ax.add_patch(nested_rect)
    _add_diagonal_stripes(ax, nested_rect, color_h1, color_h2, stripe_width=0.14)

    _style_axes(ax, "", axis_label_scale=axis_label_scale, dash_coarseness=dash_coarseness)

    ax.text(0.5, 0.5, r"$H_1$", ha="center", va="center", fontsize=BASE_REGION_LABEL_SIZE * hypothesis_label_scale, color=LABEL_COLOR, weight="bold")
    ax.text(0.5, -0.5, r"$H_2 \subset H_1$", ha="center", va="center", fontsize=BASE_NESTED_LABEL_SIZE * hypothesis_label_scale, color=LABEL_COLOR, weight="bold")
    ax.text(-0.5, 0.16, r"$H_c$", ha="center", va="center", fontsize=BASE_REGION_LABEL_SIZE * hypothesis_label_scale, color=LABEL_COLOR, weight="bold")



def create_figure3(
    fig_width: float = BASE_FIG_WIDTH,
    axis_label_scale: float = 1.0,
    hypothesis_label_scale: float = 1.0,
    dash_coarseness: float = 1.0,
    lightness: float = DEFAULT_COLOR_LIGHTNESS,
) -> plt.Figure:
    """Build and return the Figure 3 canvas.

    Args:
        fig_width: Figure width in inches.
        axis_label_scale: Multiplier for axis/tick label font sizes.
        hypothesis_label_scale: Multiplier for hypothesis region label font sizes (H1, H2, Hc).
        dash_coarseness: Multiplier for axis dash/gap length (higher means coarser dashes).
        lightness: Color lightness blend amount toward white (0 = base color, 1 = white).
    """
    fig_height = BASE_FIG_HEIGHT * (fig_width / BASE_FIG_WIDTH)
    width_scale = fig_width / BASE_FIG_WIDTH
    color_h2, color_hc, color_h1 = _get_region_colors(lightness=lightness)

    fig, axes = plt.subplots(1, 2, figsize=(fig_width, fig_height), constrained_layout=True)
    fig.set_constrained_layout_pads(h_pad=0.08, w_pad=0.04, hspace=0.08, wspace=0.08)

    plot_set_1(
        axes[0],
        axis_label_scale=width_scale * axis_label_scale,
        hypothesis_label_scale=width_scale * hypothesis_label_scale,
        dash_coarseness=dash_coarseness,
        color_h2=color_h2,
        color_hc=color_hc,
        color_h1=color_h1,
    )
    plot_set_2(
        axes[1],
        axis_label_scale=width_scale * axis_label_scale,
        hypothesis_label_scale=width_scale * hypothesis_label_scale,
        dash_coarseness=dash_coarseness,
        color_h2=color_h2,
        color_hc=color_hc,
        color_h1=color_h1,
    )

    return fig


def save_figure3(
    out_dir: Path | None = None,
    show: bool = False,
    fig_width: float = BASE_FIG_WIDTH,
    axis_label_scale: float = 1.0,
    hypothesis_label_scale: float = 1.0,
    dash_coarseness: float = 1.0,
    lightness: float = DEFAULT_COLOR_LIGHTNESS,
) -> Path:
    """Create Figure 3 and save it as PDF and SVG; return the output path."""
    out = OUT_DIR if out_dir is None else out_dir
    out.mkdir(parents=True, exist_ok=True)

    fig = create_figure3(
        fig_width=fig_width,
        axis_label_scale=axis_label_scale,
        hypothesis_label_scale=hypothesis_label_scale,
        dash_coarseness=dash_coarseness,
        lightness=lightness,
    )
    pdf_path = out / "fig3_multiple_predicted_hypotheses.pdf"

    fig.savefig(pdf_path, bbox_inches="tight")
    print(f"Saved: {pdf_path}")
    
    svg_path = out / "fig3_multiple_predicted_hypotheses.svg"
    fig.savefig(svg_path, bbox_inches="tight", format="svg")
    print(f"Saved: {svg_path}")
    
    if show:
        plt.show()
    plt.close(fig)
    return pdf_path


def main() -> None:
    save_figure3(show=False)


if __name__ == "__main__":
    main()


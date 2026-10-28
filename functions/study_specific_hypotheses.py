# %%
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from functions.color_palette import hypothesis_palette as palette

# set font for figures
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Arial"]

# %%
# -------------------------------------------------------
# Build segments (same logic as R)
# -------------------------------------------------------
def build_segments_single_study(xlo, xhi, h1_xmin, h1_xmax):
    if xhi > h1_xmax and xlo < h1_xmin:
        return pd.DataFrame({
            "xmin": [xlo, xlo, h1_xmax, h1_xmin],
            "xmax": [xhi, h1_xmin, xhi, h1_xmax],
            "y": [1, 0.5, 0.5, 1.5],
            "hypothesis": ["Hu", "Hc", "Hc", "H1"]
        })
    else:
        if xlo == h1_xmin and xhi != h1_xmax:
            hc_xmin, hc_xmax = h1_xmax, xhi
        elif xhi == h1_xmax and xlo != h1_xmin:
            hc_xmin, hc_xmax = xlo, h1_xmin
        else:
            raise ValueError("invalid configuration")

        return pd.DataFrame({
            "xmin": [xlo, hc_xmin, h1_xmin],
            "xmax": [xhi, hc_xmax, h1_xmax],
            "y": [1, 0.5, 1.5],
            "hypothesis": ["Hu", "Hc", "H1"]
        })

# %%
# -------------------------------------------------------
# Draw single study
# -------------------------------------------------------
def draw_single_study(
    ax, title, xlo, xhi, h1_xmin, h1_xmax, h0_x,
    xendsopen=False, arrow_height=0.4, extra_ticks=None, infinitexaxis=False
):
    # Construct segments for Hu, Hc, and H1 based on input parameters
    segments = build_segments_single_study(xlo, xhi, h1_xmin, h1_xmax)

    # Draw H0 line
    ax.plot([h0_x, h0_x], [0, 1.95], linestyle="dotted", color=palette["H0"], linewidth=2)

    # Draw other hypotheses lines
    for _, row in segments.iterrows():
        ax.plot([row["xmin"], row["xmax"]], [row["y"], row["y"]],
                color=palette[row["hypothesis"]], linewidth=2.5)

    # Define height of arrow caps at segment ends
    cap_half = 0.08

    # Function to draw caps at segment ends
    def draw_cap(x, y, color):
        ax.plot([x, x], [y - cap_half, y + cap_half], color=color, linewidth=2.5)

    # Put arrows at ends of segments if xendsopen is True
    if xendsopen:
        seg_ends = segments[(segments["xmin"] == xlo) & (segments["xmax"] == xhi)]
        seg_left = segments[(segments["xmin"] == xlo) & (segments["xmax"] != xhi)]
        seg_right = segments[(segments["xmax"] == xhi) & (segments["xmin"] != xlo)]
        seg_middle = segments[~((segments["xmin"] == xlo) | (segments["xmax"] == xhi))]

        # Draw caps on middle segments
        for _, row in seg_middle.iterrows():
            c = palette[row["hypothesis"]]
            draw_cap(row["xmin"], row["y"], c)
            draw_cap(row["xmax"], row["y"], c)

        # Draw caps on left segments
        for _, row in seg_left.iterrows():
            draw_cap(row["xmax"], row["y"], palette[row["hypothesis"]])

        # Draw caps on right segments
        for _, row in seg_right.iterrows():
            draw_cap(row["xmin"], row["y"], palette[row["hypothesis"]])

        # Open arrows at ends
        eps = 0.01 * (xhi - xlo)  # larger offset so arrow extends well beyond the line
        #eps = 0
        fig_h_pts = ax.figure.get_size_inches()[1] * 72  # figure height in points
        n_axes = len(ax.figure.axes)
        ax_h_pts = fig_h_pts / n_axes  # approximate height of one panel in points
        ms = ax_h_pts * arrow_height * 0.2  # arrow scales as proportion of panel height

        left_arrows = pd.concat([seg_left, seg_ends], ignore_index=True)
        for _, row in left_arrows.iterrows():
            c = palette[row["hypothesis"]]
            ax.annotate(
                "",
                xy=(row["xmin"] - eps, row["y"]),
                xytext=(row["xmin"] + 0.2*eps, row["y"]),
                arrowprops=dict(
                    arrowstyle="wedge,tail_width=1.5",
                    color=c,
                    mutation_scale=ms,
                    shrinkA=0,
                    shrinkB=0,
                )
            )

        right_arrows = pd.concat([seg_right, seg_ends], ignore_index=True)
        for _, row in right_arrows.iterrows():
            c = palette[row["hypothesis"]]
            ax.annotate(
                "",
                xy=(row["xmax"] + eps, row["y"]),
                xytext=(row["xmax"] - 0.2*eps, row["y"]),
                arrowprops=dict(
                    arrowstyle="wedge,tail_width=1.5",
                    color=c,
                    mutation_scale=ms,
                    shrinkA=0,
                    shrinkB=0,
                )
            )
    else:
        for _, row in segments.iterrows():
            c = palette[row["hypothesis"]]
            draw_cap(row["xmin"], row["y"], c)
            draw_cap(row["xmax"], row["y"], c)

    # Draw x axis
    axis_lw = 1
    ax.annotate(
        "",
        xy=(xhi, 0),
        xytext=(xlo, 0),
        arrowprops=dict(
            arrowstyle="-",
            color="black",
            shrinkA=0,
            shrinkB=0,
            lw=axis_lw,
        ),
    )
    
    # Add x-axis ticks and labels
    ticks = [h0_x] if infinitexaxis else [xlo, h0_x, xhi]
    if extra_ticks:
        ticks.extend(extra_ticks)
    ticks = sorted(set(ticks))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:g}" for t in ticks])

    # Add arrows at x axis ends if infinitexaxis is True
    if infinitexaxis:
        # Axis-end arrows to indicate continuation beyond [xlo, xhi].
        eps = 0.01 * (xhi - xlo)
        
        # Left arrow
        ax.annotate(
            "",
            xy=(xlo - eps, 0),
            xytext=(xlo + 0.2 * eps, 0),
            arrowprops=dict(
                arrowstyle="->",
                color="black",
                shrinkA=0,
                shrinkB=0,
                lw=axis_lw,
            ),
        )
        
        # Right arrow
        ax.annotate(
            "",
            xy=(xhi + eps, 0),
            xytext=(xhi - eps, 0),
            arrowprops=dict(
                arrowstyle="->",
                color="black",
                shrinkA=0,
                shrinkB=0,
                lw=axis_lw,
            ),
        )
    
    # Label each hypothesis line
    ax.text(xlo - 0.10 * (xhi - xlo), 1.45, r"$H_1$", color=palette["H1"], fontsize=12)
    ax.text(xlo - 0.10 * (xhi - xlo), 0.95, r"$H_u$", color=palette["Hu"], fontsize=12)
    ax.text(xlo - 0.10 * (xhi - xlo), 0.45, r"$H_c$", color=palette["Hc"], fontsize=12)
    ax.text(h0_x, 2.05, r"$H_0$", color=palette["H0"], fontsize=12, ha="center", va="bottom")

    # Add one x axis label below third plot
    ax.text(xlo - 0.1 * (xhi - xlo), 2.2, title, fontsize=13, fontweight="bold")

    # Set x and y limits for entire figure
    ax.set_xlim(xlo - 0.1 * (xhi - xlo), xhi + 0.05 * (xhi - xlo))
    ax.set_ylim(0, 2.2)
    # remove y ticks
    ax.set_yticks([])
    # remove all default spines (we draw the x axis manually)
    ax.spines[["left", "right", "top", "bottom"]].set_visible(False)

# %%
# -------------------------------------------------------
# Combine 3 studies
# -------------------------------------------------------
def draw_study_specific_hypotheses(
    xlo=0, xhi=1,
    h1_study1=(0.5, 1), h0_study1=0.5,
    h1_study2=(0.5, 1), h0_study2=0.5,
    h1_study3=(0.5, 1), h0_study3=0.5,
    xlab="",
    xendsopen=False,
    arrow_height=0.2,
    h_pad=3.5,
    bottom_margin=0.1,
    infinitexaxis=False,
    xticklabel_fontsize=11,
    xlabel_fontsize=12
):
    def extra_bound_ticks(h1_bounds, h0_x_value):
        lb, ub = h1_bounds
        base = [xlo, xhi, h0_x_value]
        tol = 1e-12 * max(1.0, abs(xlo), abs(xhi), abs(h0_x_value), abs(lb), abs(ub))

        extras = []
        for b in (lb, ub):
            if not any(abs(b - v) <= tol for v in base):
                extras.append(b)

        return sorted(set(extras))

    fig, axes = plt.subplots(3, 1, figsize=(8, 8), sharex=False)

    draw_single_study(
        axes[0],
        "Study 1",
        xlo,
        xhi,
        *h1_study1,
        h0_study1,
        xendsopen,
        arrow_height,
        extra_ticks=extra_bound_ticks(h1_study1, h0_study1),
        infinitexaxis=infinitexaxis,
    )
    draw_single_study(
        axes[1],
        "Study 2",
        xlo,
        xhi,
        *h1_study2,
        h0_study2,
        xendsopen,
        arrow_height,
        extra_ticks=extra_bound_ticks(h1_study2, h0_study2),
        infinitexaxis=infinitexaxis,
    )
    draw_single_study(
        axes[2],
        "Study 3",
        xlo,
        xhi,
        *h1_study3,
        h0_study3,
        xendsopen,
        arrow_height,
        extra_ticks=extra_bound_ticks(h1_study3, h0_study3),
        infinitexaxis=infinitexaxis,
    )

    # show x tick labels on all plots
    for ax in axes:
        ax.tick_params(axis="x", labelbottom=True, labelsize=xticklabel_fontsize)

    # only bottom gets x-axis label
    axes[0].set_xlabel("")
    axes[1].set_xlabel("")
    axes[2].set_xlabel(xlab, fontsize=xlabel_fontsize)

    # center x label to midpoint of drawn segment [xlo, xhi]
    x_mid = (xlo + xhi) / 2
    xlim_left = xlo - 0.1 * (xhi - xlo)
    xlim_right = xhi + 0.05 * (xhi - xlo)
    x_mid_axes = (x_mid - xlim_left) / (xlim_right - xlim_left)

    plt.tight_layout(h_pad=h_pad)
    fig.subplots_adjust(bottom=bottom_margin)
    fig.canvas.draw()

    # keep automatic y position, override only x
    label = axes[2].xaxis.label
    x_lbl, y_lbl = label.get_position()
    x_disp, y_disp = label.get_transform().transform((x_lbl, y_lbl))
    _, y_axes = axes[2].transAxes.inverted().transform((x_disp, y_disp))
    axes[2].xaxis.set_label_coords(x_mid_axes, y_axes - 0.1)

    return fig

# %%
if __name__ == "__main__":
    # -------------------------------------------------------
    # Example A: Choice probabilities
    # -------------------------------------------------------
    draw_study_specific_hypotheses(
        xlo=0, xhi=1,
        h1_study1=(0.5, 1),
        h0_study1=0.5,
        h1_study2=(0.5, 1),
        h0_study2=0.5,
        h1_study3=(0.5, 1),
        h0_study3=0.5,
        xlab="Hit rate"
    )
    plt.show()

    # -------------------------------------------------------
    # Example B: Equivalence Testing
    # -------------------------------------------------------
    draw_study_specific_hypotheses(
        xlo=-0.5, xhi=0.5,
        h1_study1=(-0.0625, 0.0625),
        h0_study1=0,
        h1_study2=(-0.1, 0.1),
        h0_study2=0,
        h1_study3=(-0.2, 0.2),
        h0_study3=0,
        xlab="Mean difference",
        xendsopen=True,
        arrow_height=0.1,
        infinitexaxis=True
    )
    plt.show()
# %%
#%%
# Add project root to path so imports work when script is run directly
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import own functions
from functions.study_specific_hypotheses import draw_study_specific_hypotheses
from functions.joint_hypotheses import plot_hypothesis_cube
from functions.multiple_predicted_hypotheses import save_figure3

# Import standard libraries
import plotly.io as pio
pio.renderers.default = "notebook"
from pathlib import Path
import copy
import matplotlib.pyplot as plt
import numpy as np
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# Set up output directories
# Use absolute path relative to script location so it works regardless of cwd
OUT_DIR = Path(__file__).parent.parent / "plots"

OUT_DIR_FIG1 = OUT_DIR / "figure1"
OUT_DIR_FIG2 = OUT_DIR / "figure2"
OUT_DIR_FIG3 = OUT_DIR / "figure3"

OUT_DIR_FIG1.mkdir(parents=True, exist_ok=True)
OUT_DIR_FIG2.mkdir(parents=True, exist_ok=True)
OUT_DIR_FIG3.mkdir(parents=True, exist_ok=True)


#%%
# -------------------------------------------------------
# Helper functions to save plots
# -------------------------------------------------------

def save_matplotlib(fig, name: str, width: int = 4.5, height: int = 5, dpi: int = 100) -> None:
    """Save matplotlib figure as PDF and SVG.
    
    Args:
        fig: matplotlib figure object
        name: filename (without extension)
        width: figure width in inches (default 5)
        height: figure height in inches (default 5)
        dpi: dots per inch (default 100)
    """
    fig.set_size_inches(width, height)
    
    pdf_path = OUT_DIR_FIG1 / f"{name}.pdf"
    fig.savefig(pdf_path, bbox_inches="tight", dpi=dpi)
    print(f"Saved PDF: {pdf_path}")
    
    svg_path = OUT_DIR_FIG1 / f"{name}.svg"
    fig.savefig(svg_path, bbox_inches="tight", format="svg")
    print(f"Saved SVG: {svg_path}")
    
    plt.close(fig)
    
def save_plotly(fig, name: str, out_dir: Path, show: bool = False) -> None:
    """Save Plotly figure as PDF and SVG."""
    # Create a copy for PDF with tight margins, no title, and scene filling the canvas
    fig_pdf = copy.deepcopy(fig)
    fig_pdf.update_layout(
        title=None,
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(domain=dict(x=[0, 1], y=[0, 1])),
        
    )
    pdf_path = out_dir / f"{name}.pdf"
    fig_pdf.write_image(pdf_path, width=500, height=500)
    print(f"Saved PDF: {pdf_path}")
    
    svg_path = out_dir / f"{name}.svg"
    fig_pdf.write_image(svg_path, width=500, height=500)
    print(f"Saved SVG: {svg_path}")

    if show:
        fig.show()

def crop_pdf(pdf_path, crop_box=(0, 10, 350, 320)):
    """Crop a PDF figure.
    
    Args:
        pdf_path: path to PDF file
        crop_box: (left, bottom, right, top) in points (72 points = 1 inch)
                 Default crops 7.5% from each side of 1350x1350 image (15% total reduction)
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.cropbox.lower_left = (crop_box[0], crop_box[1])
        page.cropbox.upper_right = (crop_box[2], crop_box[3])
        writer.add_page(page)
    
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    print(f"Cropped PDF: {pdf_path}")
    

#%%
# -------------------------------------------------------
# Figure 1: Single Hypotheses
# -------------------------------------------------------

# A: Choice probabilities
fig_1a = draw_study_specific_hypotheses(
    xlo=0, xhi=1,
    h1_study1=(0.5, 1),   h0_study1=0.5,
    h1_study2=(0.5, 1),   h0_study2=0.5,
    h1_study3=(0.5, 1),   h0_study3=0.5,
    xlab="Hit rate",
    #xticklabel_fontsize=10,
    #xlabel_fontsize=12
)
save_matplotlib(fig_1a, "fig1_A_choice_probabilities")

# B: Equivalence Testing
fig_1b = draw_study_specific_hypotheses(
    xlo=-0.3, xhi=0.3,
    h1_study1=(-0.0625, 0.0625), h0_study1=0,
    h1_study2=(-0.1, 0.1),       h0_study2=0,
    h1_study3=(-0.2, 0.2),       h0_study3=0,
    xlab="Mean difference",
    xendsopen=True,
    arrow_height=0.1
)
save_matplotlib(fig_1b, "fig1_B_equivalence_testing")


#%%
# -------------------------------------------------------
# Figure 2: Joint Hypotheses (H1 only)
# -------------------------------------------------------

# Define
# CAMERA = dict(
#     eye=dict(x=-1.7564840730006672, y=-1.8514899417366444, z=1.0940931717142417),
#     up=dict(x=0, y=0, z=1),
#     center=dict(x=0, y=0, z=0),
# )
CAMERA = dict(
    eye=dict(x=-1.7564840730006672, y=-1.3, z=1.0940931717142417),
    up=dict(x=0, y=0, z=1),
    center=dict(x=0, y=0, z=0),
)

# A1: Choice probabilities – H1 only
fig = plot_hypothesis_cube(plot_hc_incomplete=False, plot_hc_complete=False, plot_hu=False)
fig.update_layout(title="A1: Choice probabilities – H1 only", scene_camera=CAMERA, scene_aspectmode="cube")
fig.update_yaxes(automargin='left+top')
save_plotly(fig, "fig2_A1_choice_prob_h1_only", OUT_DIR_FIG2)
crop_pdf(OUT_DIR_FIG2 / "fig2_A1_choice_prob_h1_only.pdf")

# A2: Choice probabilities – H1 + Hu
fig = plot_hypothesis_cube(plot_hc_incomplete=False, plot_hu=True)
fig.update_layout(title="A2: Choice probabilities – H1 + Hu", scene_camera=CAMERA, scene_aspectmode="cube")
save_plotly(fig, "fig2_A2_choice_prob_hu", OUT_DIR_FIG2)
crop_pdf(OUT_DIR_FIG2 / "fig2_A2_choice_prob_hu.pdf")

# A3: Choice probabilities – H1 + incomplete Hc
fig = plot_hypothesis_cube()
fig.update_layout(title="A3: Choice probabilities – H1 + incomplete Hc", scene_camera=CAMERA, scene_aspectmode="cube")
save_plotly(fig, "fig2_A3_choice_prob_incomplete_hc", OUT_DIR_FIG2)
crop_pdf(OUT_DIR_FIG2 / "fig2_A3_choice_prob_incomplete_hc.pdf")

# A4: Choice probabilities – H1 + complete Hc
fig = plot_hypothesis_cube(plot_hc_incomplete=False, plot_hc_complete=True)
fig.update_layout(title="A4: Choice probabilities – H1 + complete Hc", scene_camera=CAMERA, scene_aspectmode="cube")
save_plotly(fig, "fig2_A4_choice_prob_complete_hc", OUT_DIR_FIG2)
crop_pdf(OUT_DIR_FIG2 / "fig2_A4_choice_prob_complete_hc.pdf")

# B1: Equivalence testing – H1 only
fig = plot_hypothesis_cube(
    xmin=-0.3, xmax=0.3,
    h1_min=(-0.0625, -0.1, -0.2),
    h1_max=(0.0625, 0.1, 0.2),
    h0=(0, 0, 0),
    tickvals_x=( -0.0625, 0, 0.0625),
    tickvals_y=(-0.1, 0, 0.1),
    tickvals_z=(-0.2, 0, 0.2),
    plot_hc_incomplete=False,
    plot_hc_complete=False,
    plot_hu=False,
)
fig.update_layout(title="B1: Equivalence testing – H1 only", scene_camera=CAMERA, scene_aspectmode="cube")
save_plotly(fig, "fig2_B1_equivalence_h1_only", OUT_DIR_FIG2)
crop_pdf(OUT_DIR_FIG2 / "fig2_B1_equivalence_h1_only.pdf")

# B2: Equivalence testing – H1 + Hu
fig = plot_hypothesis_cube(
    xmin=-0.3, xmax=0.3,
    h1_min=(-0.0625, -0.1, -0.2),
    h1_max=(0.0625, 0.1, 0.2),
    h0=(0, 0, 0),
    tickvals_x=( -0.0625, 0, 0.0625),
    tickvals_y=(-0.1, 0, 0.1),
    tickvals_z=(-0.2, 0, 0.2),
    plot_hc_incomplete=False,
    plot_hu=True,
)
fig.update_layout(title="B2: Equivalence testing – H1 + Hu", scene_camera=CAMERA, scene_aspectmode="cube")
save_plotly(fig, "fig2_B2_equivalence_hu", OUT_DIR_FIG2)
crop_pdf(OUT_DIR_FIG2 / "fig2_B2_equivalence_hu.pdf")

# B3: Equivalence testing – H1 + incomplete Hc
fig = plot_hypothesis_cube(
    xmin=-0.3, xmax=0.3,
    h1_min=(-0.0625, -0.1, -0.2),
    h1_max=(0.0625, 0.1, 0.2),
    h0=(0, 0, 0),
    tickvals_x=( -0.0625, 0, 0.0625),
    tickvals_y=(-0.1, 0, 0.1),
    tickvals_z=(-0.2, 0, 0.2),
)
fig.update_layout(title="B3: Equivalence testing – H1 + incomplete Hc", scene_camera=CAMERA, scene_aspectmode="cube")
save_plotly(fig, "fig2_B3_equivalence_incomplete_hc", OUT_DIR_FIG2)
crop_pdf(OUT_DIR_FIG2 / "fig2_B3_equivalence_incomplete_hc.pdf")

# B4: Equivalence testing – H1 + complete Hc
fig = plot_hypothesis_cube(
    xmin=-0.3, xmax=0.3,
    h1_min=(-0.0625, -0.1, -0.2),
    h1_max=(0.0625, 0.1, 0.2),
    h0=(0, 0, 0),
    tickvals_x=( -0.0625, 0, 0.0625),
    tickvals_y=(-0.1, 0, 0.1),
    tickvals_z=(-0.2, 0, 0.2),
    plot_hc_incomplete=False,
    plot_hc_complete=True,
)
fig.update_layout(title="B4: Equivalence testing – H1 + complete Hc", scene_camera=CAMERA, scene_aspectmode="cube")
save_plotly(fig, "fig2_B4_equivalence_complete_hc", OUT_DIR_FIG2)
crop_pdf(OUT_DIR_FIG2 / "fig2_B4_equivalence_complete_hc.pdf")


#%%
# -------------------------------------------------------
# Figure 3: 2D Hypothesis Spaces
# -------------------------------------------------------

FIG3_WIDTH_IN = 14
FIG3_AXIS_LABEL_SCALE = 1.2
FIG3_HYPOTHESIS_LABEL_SCALE = 1.4
FIG3_AXIS_DASH_COARSENESS = 1.5
FIG3_LIGHTNESS = 0.3

save_figure3(
    out_dir=OUT_DIR_FIG3,
    show=False,
    fig_width=FIG3_WIDTH_IN,
    axis_label_scale=FIG3_AXIS_LABEL_SCALE,
    hypothesis_label_scale=FIG3_HYPOTHESIS_LABEL_SCALE,
    dash_coarseness=FIG3_AXIS_DASH_COARSENESS,
    lightness=FIG3_LIGHTNESS,
)
# %%

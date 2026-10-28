"""Shared color definitions for plotting scripts."""

# ggthemes::Classic_20 approximation (with alpha channel, as used historically).
colors = [
    "#1F77B4FF", "#AEC7E8FF", "#FF7F0EFF", "#FFBB78FF", "#2CA02CFF",
    "#98DF8AFF", "#D62728FF", "#FF9896FF", "#9467BDFF", "#C5B0D5FF",
    "#8C564BFF", "#C49C94FF", "#E377C2FF", "#F7B6D2FF", "#7F7F7FFF",
    "#C7C7C7FF", "#BCBD22FF", "#DBDB8DFF", "#17BECFFF", "#9EDAE5FF",
]

# Colorblind-friendly hypothesis palette
# Based on Paul Tol's qualitative color scheme (safe for all colorblindness types)
# Used in combinations: H2+Hc+H1 (figure 3), H0+Hu+Hc+H1 (study-specific)
hypothesis_palette = {
    "H0": "#4477AA",   # Blue (null hypothesis)
    "H1": "#EE6677",   # Red (main hypothesis)
    "H2": "#66CCEE",   # Cyan (alternative hypothesis)
    "Hu": "#CCBB44",   # Yellow (unconstrained hypothesis)
    "Hc": "#228833",   # Green (complement hypothesis)
}


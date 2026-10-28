"""Shared color definitions for plotting scripts."""

# Colorblind-friendly hypothesis palette
# Based on Paul Tol's "bright" qualitative color scheme (safe for all colorblindness types)
# https://cran.r-project.org/web/packages/khroma/vignettes/tol.html
hypothesis_palette = {
    "H0": "#4477AA",   # Blue (null hypothesis)
    "H1": "#EE6677",   # Pink (main hypothesis)
    "H2": "#66CCEE",   # Cyan (alternative hypothesis)
    "Hu": "#CCBB44",   # Yellow (unconstrained hypothesis)
    "Hc": "#228833",   # Green (complement hypothesis)
}


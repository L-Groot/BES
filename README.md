# Bayesian Evidence Synthesis (BES)

Reproducible code for the empirical examples and figures in *"Specifying meaningful hypotheses across studies: Bayesian evidence synthesis revisited"* by Laura Groot and Daniel W. Heck. [Preprint link coming soon]

## Repository Structure

<pre>
├── analyses/              # Analysis scripts
│   ├── scheibehenne.r    # Example 1 (Table 2 in paper)
│   └── volker.r          # Example 2 (Table 3 in paper)
│   ├── scheibehenne.Rmd  # Source report for Example 1
│   └── volker.Rmd        # Source report for Example 2
├── scheibehenne_original/ # Unmodified materials from Scheibehenne et al. (2016) <a href="https://osf.io/ycx49/">(link to OSF repository)</a>
│   ├── scheibehenne_original.r   # Original analysis script
│   └── towelData.csv             # Raw data
├── reports/
│   ├── html/             # Rendered HTML reports
│   └── pdf/              # Rendered PDF reports
├── functions/
│   ├── compute_joint_complements.r   # Computes joint BFs including complete complement
│   ├── make_figures.py               # Creates Figures 1–2 and S1
│   ├── study_specific_hypotheses.py  # Figure 1: study-specific hypotheses
│   ├── joint_hypotheses.py           # Figure 2: joint hypotheses
│   ├── multiple_predicted_hypotheses.py  # Figure S1: multiple predicted hypotheses
│   └── color_palette.py              # Colorblind-friendly palette for all figures
├── figures/                # Figures 1–2 and S1 (PDF + SVG)
├── requirements.txt      # Python package versions for the figures
├── renv/                 # renv - package management for reproducibility
│   ├── activate.R        # Activates isolated R environment on startup
│   ├── settings.json     # renv configuration
│   └── .gitignore        # Ignores library/ (auto-generated on restore)
├── renv.lock             # Locks exact package versions
└── .Rprofile             # Auto-activates renv
</pre>

## Reproduce Analyses and Figures

**1. Setup the R environment**:
```r
renv::restore()
```
This command installs the exact versions of all required packages that were used to produce the results in the paper. Therefore, you can clone this repo and reproduce the results with identical package versions, regardless of what is currently installed on your system.

**2. Run the analyses:**
```r
source("analyses/scheibehenne.r")   # Example 1: hotel towel reuse
source("analyses/volker.r")         # Example 2: network embeddedness
```

**3. Render the reports (HTML + PDF):**
```r
rmarkdown::render("analyses/scheibehenne.Rmd", output_format = "html_document", output_dir = "reports/html")
rmarkdown::render("analyses/scheibehenne.Rmd", output_format = "pdf_document", output_dir = "reports/pdf")
rmarkdown::render("analyses/volker.Rmd", output_format = "html_document", output_dir = "reports/html")
rmarkdown::render("analyses/volker.Rmd", output_format = "pdf_document", output_dir = "reports/pdf")
```
If PDF rendering fails because no LaTeX distribution is available, install TinyTeX once:
```r
tinytex::install_tinytex()
```

**4. Create the figures (Python):**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python functions/make_figures.py
```
This saves Figures 1–2 and S1 (PDF + SVG) to `figures/`.

## Requirements

- R 4.6.1+
- Python 3.13+ (for the figures only)

## References

Scheibehenne, B., Jamil, T., & Wagenmakers, E.-J. (2016). Bayesian evidence synthesis can reconcile seemingly inconsistent results: The case of hotel towel reuse. *Psychological Science, 27*(7), 1043-1046. https://doi.org/10.1177/0956797616644081

Volker, T. B. (2022). *The future is made today: Concerns for reputation foster trust and cooperation* [Unpublished master's thesis].

## Licence

MIT License for the code, see [LICENSE](LICENSE).

This project reanalyses data published in previous publications. When using this
code, please cite the relevant original studies as referenced above.

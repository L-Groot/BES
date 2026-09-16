# Bayesian Evidence Synthesis (BES)

Reproducible code for the empirical examples in *"Specifying meaningful hypotheses across studies: Bayesian evidence synthesis revisited"* by Laura Groot and Daniel W. Heck. [[Preprint](link-to-preprint)]

## Quick Start

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

## Repository Structure

```
├── analyses/              # Analysis scripts
│   ├── scheibehenne.r    # Example 1 (Table 2 in paper)
│   └── volker.r          # Example 2 (Table 3 in paper)
├── data/
│   └── towelData.csv     # Raw data for scheibehenne.r
├── functions/
│   └── compute_joint_complements.r   # Computes joint BFs including complete complement
├── renv/                 # renv - package management for reproducibility
│   ├── activate.R        # Activates isolated R environment on startup
│   ├── settings.json     # renv configuration
│   └── .gitignore        # Ignores library/ (auto-generated on restore)
├── renv.lock             # Locks exact package versions
└── .Rprofile             # Auto-activates renv
```

## Requirements

- R 4.6.1+

## References

Scheibehenne, B., Jamil, T., & Wagenmakers, E.-J. (2016). Bayesian evidence synthesis can reconcile seemingly inconsistent results: The case of hotel towel reuse. *Psychological Science, 27*(7), 1043-1046. https://doi.org/10.1177/0956797616644081

Volker, T. B. (2022). *The future is made today: Concerns for reputation foster trust and cooperation* [Unpublished master's thesis].

## Licence

MIT License for the code, see [LICENSE](LICENSE).

This project reanalyses data published in previous publications. When using this
code, please cite the relevant original studies as referenced above.

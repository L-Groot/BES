#--------------------------------------
# Analysis Volker (2022)
#--------------------------------------

# ============================================================================
# Citation:
# Volker, T. B. (2022). The future is made today: Concerns for reputation
# foster trust and cooperation [Unpublished master's thesis]. Department of
# Sociology, Utrecht University.
# https://github.com/thomvolker/bes_master_thesis_sasr/blob/main/thesis/thesis_volker.pdf
# ============================================================================


# Load required packages
library(dplyr)
library(here)

# Load complement function
source(here("functions/compute_joint_complements.r"))

# ============================================================================
# (1) Copy data from Table 2 and 4 of Volker (2022)
# ============================================================================

# trustfulness: proportion of initial endowment sent to the trustee
# (p. 27)
# trustworthiness: proportion of the amount sent that is returned to the
# trustor (p. 27)

# Format from Table 2
# BF values taken from Table 4 because reported to 3dp there
table2_df <- data.frame(
    study = c(
        rep("bolton_2004", 2),
        rep("duffy_2013_no_netmin", 2),
        rep("duffy_2013_no_netfull", 2),
        rep("buskens_2010", 2),
        rep("van_miltenburg_2012", 2),
        rep("frey_2019", 2),
        rep("barrera_buskens_2009", 2),
        "seinen_schram_2006",
        "corten_2016"
    ),
    outcome = c(
        rep(c("Trustfulness", "Trustworthiness"), 7),
        "Cooperation (helping)",
        "Cooperation"
    ),
    no_network = c(
        0.67, 0.69, 0.62, 0.68, 0.75, 0.62, 0.83, 0.87,
        0.90, 0.90, 0.77, 0.67, 0.73, 0.46, 0.38, 0.49
    ),
    network = c(
        0.75, 0.61, 0.64, 0.77, 0.86, 0.94, 0.94, 0.94,
        0.88, 0.91, 0.81, 0.88, 0.70, 0.50, 0.61, 0.37
    ),
    bf_iu = c(
        1.474, 0.642, 1.292, 1.823, 1.799, 2.000, 1.848,
        1.680, 0.675, 1.115, 1.426, 1.998, 0.482, 1.450,
        1.902, 0.102
    ),
    bf_ic = c(
        2.799, 0.473, 1.825, 10.319, 8.958, 2.60e+04,
        12.168, 5.255, 0.509, 1.260, 2.486, 1.01e+03,
        0.318, 2.634, 19.351, 0.054
    )
)

#View(table2_df)

# The 'compute_joint_complements()' function requires BF_cu's for each study.
# We have BF_1u's but we still need BF_cu's.
# But since we also have BF_1c's, we can compute the BF_cu's by transitivty:
# -> BF_cu = BF_c1 / BF_u1

table2_ready <- table2_df %>%
    # convert BF_1c to BF_c1
    mutate(bf_c1 = 1 / bf_ic) %>%
    # convert BF_1u to BF_u1
    mutate(bf_u1 = 1 / bf_iu) %>%
    # compute BF_cu
    mutate(bf_cu = bf_c1 / bf_u1) %>%
    # select only relevant columns
    select(study, bf_iu, bf_cu) %>%
    # rename for function compatibility
    rename(Study = study,
           H1 = bf_iu,
           Hc = bf_cu) %>%
    # add P(theta in Hc) column
    mutate(P_theta_in_Hc = 0.5)

print(table2_ready)

# ============================================================================
# (2) Compute joint BFs
# ============================================================================

# BF_1u(joint) ≈ 7.24 (vs 7.27)
bf_1u <- prod(table2_df$bf_iu)

# BF_1c(joint) ≈ 5.23+11 (vs 5.23+11)
bf_1c <- prod(table2_df$bf_ic)

# Compute BF_1u(joint), BF_cu(joint) and BF_c*u(joint)
res <- compute_joint_complements(table2_ready,
                          replace_0_with = 0.001,
                          round_res = FALSE)

# check BF_1c(joint): matches column product from original table
(res["BES_c","H1"] / res["BES_c","Hc"]) # = BF_1u(joint) / BF_cu(joint)

# BF_1c*(joint) ≈ 0.0001
bf_1c_star <- res["BES_c_star","H1"] / res["BES_c_star","Hc*"]

# Study-specific Bayes factors
results_df <- table2_df %>%
    transmute(
        Study = study,
        Outcome = outcome,
        bf_1u = bf_iu,
        bf_1c = bf_ic,
        bf_cu = bf_iu / bf_ic
    )

# ============================================================================
# (3) Display results
# ============================================================================

# Functions to format numbers as strings for display
fmt2 <- function(x) sprintf("%.2f", x) # 2dp
fmtE <- function(x) sprintf("%.2e", x) # 2dp in scientific notation

# Round experiment BFs
rounded_results_df <- results_df %>%
    mutate(across(starts_with("bf_"), \(x) round(x, digits = 2)))

# Save as text for paste()
study_table_text <- capture.output(print(rounded_results_df))

# Full output
output_lines <- c(
    "",
    "",
    "-------------------------------",
    "REANALYSIS VOLKER (2022)",
    "-------------------------------",
    "",
    "Study(experiment)-specific Bayes Factors:",
    "- - - - - - - - - - - - - - - - - - - - -",
    paste(study_table_text, collapse = "\n"),
    "",
    "Joint Bayes Factors:",
    "- - - - - - - - - -",
    paste0("BF_1u(joint) ≈ ", fmt2(bf_1u), " (", fmtE(bf_1u), ")"),
    paste0("BF_1c(joint) ≈ ", fmt2(bf_1c), " (", fmtE(bf_1c), ")"),
    paste0("BF_1c*(joint) ≈ ", fmt2(bf_1c_star), " (", fmtE(bf_1c_star), ")"),
    ""
)

# Print results
cat(paste(output_lines, collapse = "\n"), "\n", sep = "")


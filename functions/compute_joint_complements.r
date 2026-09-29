# Function that computes BFs for complete vs incomplete complement
library(dplyr)
library(tibble)
library(stringr)

# ============================================================================
# HELPER FUNCTION: validate + standardize bf-style input names
# ============================================================================

validate_and_prepare_input_df <- function(df) {
    # Check that df is a data frame
    if (!is.data.frame(df)) {
        stop("df must be a data frame.")
    }

    if (ncol(df) < 4) {
        stop("df must have at least 4 columns: 'Study' (study names), 'bf_1u' (BF for first predicted hypothesis against unconstrained), 'bf_cu' (BF for complement against unconstrained), and 'P_theta_in_Hc'. More columns can be supplied for more predicted hypotheses (e.g., bf_2u, bf_3u, etc.).")
    }

    # Check that first column contains character/string values (study names)
    if (!is.character(df[[1]])) {
        stop("First column of df must contain character strings.")
    }

    # Check that all other columns are numeric
    for (i in 2:ncol(df)) {
        if (!is.numeric(df[[i]])) {
            stop(sprintf(
                "Column %d ('%s') in df must be numeric.",
                i, colnames(df)[i]
            ))
        }
    }

    # Check that a P(theta in Hc) column is present
    if (!("P_theta_in_Hc" %in% colnames(df))) {
        stop("Column 'P_theta_in_Hc' is required.")
    }

    col_lc <- tolower(colnames(df))

    # Detect complement column
    hc_idx <- which(grepl("^bf_?cu$", col_lc))
    if (length(hc_idx) != 1) {
        stop("Could not uniquely identify complement column. Use exactly one of: bf_cu, bfcu.")
    }
    # Detect P_theta column
    p_idx <- which(colnames(df) == "P_theta_in_Hc")
    if (length(p_idx) != 1) {
        stop("Could not uniquely identify column 'P_theta_in_Hc'.")
    }

    # Detect first predicted hypothesis column (bf_1u / bf1u)
    h1_idx <- which(grepl("^bf_?1u$", col_lc))
    if (length(h1_idx) != 1) {
        stop("Could not uniquely identify first predicted hypothesis column. Use 'bf_1u' (or 'bf1u').")
    }

    # Check if at least one predicted hypothesis column is present
    excluded <- c(1, hc_idx, p_idx)
    pred_idx <- setdiff(2:ncol(df), excluded)
    if (length(pred_idx) < 1) {
        stop("At least one predicted BF column is required.")
    }

    # Ensure bf_1u is first among predicted columns
    pred_idx <- c(h1_idx, setdiff(pred_idx, h1_idx))

# Check if all predicted BF column names follow the bf_*u naming convention
    pred_names_lc <- tolower(colnames(df)[pred_idx])
    valid_pred <- grepl("^bf_?[0-9]+u$", pred_names_lc)
    if (!all(valid_pred)) {
        invalid_cols <- colnames(df)[pred_idx][!valid_pred]
        stop(sprintf(
            "Predicted BF column names must follow bf_*u naming (e.g., bf_1u, bf2u). Invalid column(s): %s",
            paste(invalid_cols, collapse = ", ")
        ))
    }

    out <- df[, c(1, pred_idx, hc_idx, p_idx), drop = FALSE]
    pred_names_std <- sub("^bf_?([0-9]+)u$", "bf_\\1u", tolower(colnames(df)[pred_idx]))
    colnames(out) <- c(colnames(df)[1], pred_names_std, "bf_cu", "P_theta_in_Hc")
    out
}

# ============================================================================
# MAIN FUNCTION: compute joint complements
# ============================================================================

compute_joint_complements <- function(
                    # input df
                    # column 1: study names
                    # last column: prob(theta in Hc)
                    # other columns: BF_Hu's for each hypothesis
                    # -> second to last column must be Hc
                    df,
                    # value to replace BFs of 0 with (default: 0.001)
                    replace_0_with = 0.001,
                    # whether to round results to 2dp (default: TRUE)
                    round_res = TRUE
                    ) {

#    df <- table6_df
#    replace_0_with <- 0.001

    # ========================================================================
    # Validate input
    # ========================================================================
  
    # Validate and standardize input
    df <- validate_and_prepare_input_df(df)

    # ========================================================================
    # Prepare data
    # ========================================================================
    
    # Create data matrix with just the BF columns
    df_bf <- df[, c(2:(ncol(df)-1))] %>%
        as.data.frame()
    
    # Mark location of imputed values
    imputed_mask <- df_bf == 0

    # Replace BFs of 0 with specified value
    df_bf <- df_bf %>%
        mutate(across(everything(), ~ifelse(. == 0, replace_0_with, .)))
    
    # Issue warning about replaced zeroes
    n_replaced <- sum(imputed_mask)
    if (n_replaced > 0) {
        warning(sprintf("%d zero value(s) replaced with %g", n_replaced, replace_0_with))
    }
    
    # Calculate nr of studies and hypotheses
    n_studies <- nrow(df_bf)
    n_hypotheses <- ncol(df_bf) # all predicted + complement
    
    # Add P(theta in Hc) column
    df_bf <- df_bf %>%
        mutate(P_theta_in_Hc = df[[ncol(df)]])

    # ========================================================================
    # Compute BF_pu_(t) for each study
    # ========================================================================

    df_bf <- df_bf %>%
        mutate(
            # BF_P,u = (1 - BF_cu * P(theta in Hc)) / (1 - P(theta in Hc))
            bf_pu = (1 - bf_cu * P_theta_in_Hc) / (1 - P_theta_in_Hc)
        ) %>%
        select(-P_theta_in_Hc)


    # ========================================================================
    # Compute joint BFs for bf_1u-bf_nu, bf_cu and bf_pu (multiplication across studies)
    # ========================================================================

    # Transpose df_bf (switch rows and columns)
    bf_table <- df_bf %>%
        t() %>%
        as.data.frame() %>%
        rownames_to_column("Hypothesis") %>%
        rename_with(~paste0("S", 1:n_studies), -Hypothesis)
    
    # Compute joint BFs by taking products across rows for each hypothesis (in log scale)
    bf_table <- bf_table %>%
        rowwise() %>%
        mutate(Joint_c = exp(sum(log(c_across(starts_with("S")))))) %>%
        ungroup()

    # Add row for bf_cu_star (complete complement)
    hc_row <- bf_table %>% filter(Hypothesis == "bf_cu")
    hc_star_row <- hc_row %>%
        mutate(Hypothesis = "bf_cu_star", Joint_c = NA_real_)
    # -> cell for complete joint complement is NA for now, will be filled in later
    bf_table <- bf_table %>%
        bind_rows(hc_star_row)

    # Extract BF_pu^(t)
    bf_pu <- bf_table %>%
        filter(Hypothesis == "bf_pu") %>%
        select(starts_with("S")) %>%
        as.numeric()

    # Extract BF_pu^(joint)
    bf_pu_joint <- bf_table[which(bf_table$Hypothesis == "bf_pu"), "Joint_c"] %>% pull()

    # Remove bf_pu row from table
    bf_table <- bf_table %>%
        filter(Hypothesis != "bf_pu")
    
    # Extract BF_cu^(t)
    bf_cu <- bf_table %>%
        filter(Hypothesis == "bf_cu") %>%
        select(starts_with("S")) %>%
        as.numeric()

    # Extract BF_cu^(joint)
    bf_cu_joint <- bf_table[which(bf_table$Hypothesis == "bf_cu"), "Joint_c"] %>% pull()

    # ========================================================================
    # Compute joint BF for Hc*
    # ========================================================================

    # # Compute BF_pc^(joint) ("incomplete complement")
    # bf_pc_joint <- bf_pu_joint / bf_cu_joint

    # Compute BF_c*,u^(joint)
    # -> sum over all non-empty subsets of studies contributing evidence for Hc
    # -> represent each subset as a binary number from 1 to 2^n_studies - 1
    # -> use log scale for numerical accuracy
    bf_cu_star_joint_log <- log(0)  # Initialize to log(0) = -Inf
    
    # Iterate over all non-empty subsets of studies
    for (i in 1:(2^n_studies - 1)) {

        # Convert i to binary to determine which studies are in Omega_i
        subset_indicator <- as.integer(intToBits(i))[1:n_studies]
        
        # Sum of logs for BF_c,u for studies in Omega_i (replaces product)
        sum_log_in_subset <- sum(log(bf_cu[subset_indicator == 1]))
        
        # Sum of logs for BF_p,u for studies not in Omega_i (replaces product)
        sum_log_out_subset <- sum(log(bf_pu[subset_indicator == 0]))
        
        # Add to the sum (using log-space addition)
        product_term_log <- sum_log_in_subset + sum_log_out_subset
        if (i == 1) {
            bf_cu_star_joint_log <- product_term_log
        } else {
            # logsum(a, b) = max(a,b) + log(1 + exp(-|a-b|))
            max_log <- max(bf_cu_star_joint_log, product_term_log)
            bf_cu_star_joint_log <- max_log + log(1 + exp(-abs(bf_cu_star_joint_log - product_term_log)))
        }
    }
    
    # Convert back from log scale
    bf_cu_star_joint <- exp(bf_cu_star_joint_log)
    
    # Apply uniform weighting across all 2^T - 1 non-empty subsets
    bf_cu_star_joint <- bf_cu_star_joint / (2^n_studies - 1)

    # Add BF_c*,u^(joint) to the table
    # in a new column called "Joint_c_star" for the row bf_cu_star
    bf_table <- bf_table %>%
        mutate(Joint_c_star = ifelse(Hypothesis == "bf_cu_star", bf_cu_star_joint, Joint_c)) %>%
        mutate(Joint_c_star = ifelse(Hypothesis == "bf_cu", NA_real_, Joint_c_star))

   
    # # Calculate BF_p,c*^(joint) ("complete complement")
    # bf_pc_star_joint <- bf_pu_joint / bf_cu_star_joint

    # ========================================================================
    # Create BF output table
    # ========================================================================

    # Create BF output table
    results_bf <- bf_table %>%
        rename(BF_c = Joint_c, BF_c_star = Joint_c_star) %>%
        select(Hypothesis, starts_with("S"), starts_with("BF")) %>%
        rename_with(~str_replace(., "^BF", "BES"), starts_with("BF"))

    # Optional rounding to 2dp
    if(round_res == TRUE) {
        results_bf <- results_bf %>%
            mutate(across(where(is.numeric), ~ ifelse(is.na(.), NA, round(., 2))))
    }

    # Transpose dataframe to have hypotheses as columns and studies as rows
    results_bf <- results_bf %>%
        column_to_rownames("Hypothesis") %>%
        t() %>%
        as.data.frame()

    # ========================================================================
    # Return results
    # ========================================================================

    return(results_bf)

}

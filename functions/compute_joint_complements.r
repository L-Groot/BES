# Function that computes BFs for complete vs incomplete complement
library(dplyr)
library(tibble)
library(stringr)

# ============================================================================
# HELPER FUNCTION: validate input dataframe structure
# ============================================================================

validate_df <- function(df) {
    # Check that df is a data frame
    if (!is.data.frame(df)) {
        stop(sprintf("df must be a data frame."))
    }

    # Check that first column contains character/string values (study names)
    if (!is.character(df[[1]])) {
        stop(sprintf(
            "First column of df must contain character strings."
        ))
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

    # Check that columns are named and ordered correctly
    if (colnames(df)[2] != "H1") {
        stop(
            "Second column must be named 'H1' ",
            "for the first predicted hypothesis."
        )
    }
        if (colnames(df)[ncol(df)-1] != "Hc") {
        stop(
            "Second-to-last column must be named 'Hc' ",
            "for the complement hypothesis."
        )
    }
    if (colnames(df)[ncol(df)] != "P_theta_in_Hc") {
        stop(
            "Last column must be named 'P_theta_in_Hc' ",
            "for the probability of theta in the complement hypothesis."
        )
    }
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
  
    # Validate both input dataframes
    validate_df(df)

    # ========================================================================
    # Prepare data
    # ========================================================================
    
    # Extract study names from first column
    study_names <- df[[1]]
    
    # Extract hypothesis names from column names (excluding "Study")
    hypothesis_names <- colnames(df)[2:(ncol(df)-1)]
    
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
            # BF_cu is the complement
            BF_cu = Hc,
            # BF_P,u = (1 - BF_cu * P(theta in Hc)) / (1 - P(theta in Hc))
            BF_pu = (1 - BF_cu * P_theta_in_Hc) / (1 - P_theta_in_Hc)
        ) %>%
        select(-P_theta_in_Hc) %>%
        rename_with(~paste0("BF_", 1:(n_hypotheses - 1), "u"), 1:(n_hypotheses - 1)) %>%
        # remove duplicate Hc column
        select(-Hc)


    # ========================================================================
    # Compute joint BFs for H1-Hn, Hc and Hp (multiplication across studies)
    # ========================================================================

    # Transpose df_bf (switch rows and columns)
    bf_table <- df_bf %>%
        t() %>%
        as.data.frame() %>%
        rownames_to_column("Hypothesis") %>%
        #as_tibble() %>%
        rename_with(~paste0("S", 1:n_studies), -Hypothesis) %>%
        mutate(Hypothesis = str_replace(Hypothesis, "BF_(.+)u", "H\\1"))
    
    # Compute joint BFs by taking products across rows for each hypothesis (in log scale)
    bf_table <- bf_table %>%
        rowwise() %>%
        mutate(Joint_c = exp(sum(log(c_across(starts_with("S")))))) %>%
        ungroup()

    # Add row for Hc* (complete complement)
    hc_row <- bf_table %>% filter(Hypothesis == "Hc")
    hc_star_row <- hc_row %>%
        mutate(Hypothesis = "Hc*", Joint_c = NA_real_)
    # -> cell for complete joint complement is NA for now, will be filled in later
    bf_table <- bf_table %>%
        bind_rows(hc_star_row)

    # Extract BF_pu^(t)
    bf_pu <- bf_table %>%
        filter(Hypothesis == "Hp") %>%
        select(starts_with("S")) %>%
        as.numeric()

    # Extract BF_pu^(joint)
    bf_pu_joint <- bf_table[which(bf_table$Hypothesis == "Hp"), "Joint_c"] %>% pull()

    # Remove Hp row from table
    bf_table <- bf_table %>%
        filter(Hypothesis != "Hp")
    
    # Extract BF_cu^(t)
    bf_cu <- bf_table %>%
        filter(Hypothesis == "Hc") %>%
        select(starts_with("S")) %>%
        as.numeric()

    # Extract BF_cu^(joint)
    bf_cu_joint <- bf_table[which(bf_table$Hypothesis == "Hc"), "Joint_c"] %>% pull()

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
    # in a new column called "Joint_c_star" for the row Hc*
    bf_table <- bf_table %>%
        mutate(Joint_c_star = ifelse(Hypothesis == "Hc*", bf_cu_star_joint, Joint_c)) %>%
        mutate(Joint_c_star = ifelse(Hypothesis == "Hc", NA_real_, Joint_c_star))

   
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

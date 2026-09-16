#---------------------------------------------------
# Analysis Scheibehenne, Jamil, & Wagenmakers (2016)
#---------------------------------------------------

# ============================================================================
# Citation:
# Scheibehenne, B., Jamil, T., & Wagenmakers, E.-J. (2016). 
# Bayesian Evidence Synthesis Can Reconcile Seemingly Inconsistent Results: The Case of
# Hotel Towel Reuse. Psychological Science, 27(7), 1043–1046.
# https://doi.org/10.1177/0956797616644081
# ============================================================================

# This R script is adapted from the R script "towelReuseDataAnalysis.r"
# provided by the authors, which is available at https://osf.io/ycx49/files/juaq2.
# It requires the raw data file ("towelData.csv", which is available at
# https://osf.io/ycx49/files/qsb3f

# Load required packages
library(BayesFactor)
library(dplyr)
library(here)

# Load complement function and data
source(here("functions/compute_joint_complements.r"))
rawData <- read.table(here("data/towelData.csv"), header=T, sep=";", stringsAsFactors=F)

# n = number of experiments (each experiment has 4 cells: 2x2)
n <- dim(rawData)[1] / 4
# = 7


#add total (assuming a fixed effect)
   bigTable=array(rawData$Count, dim=c(2,2,n))
   total2x2=apply(bigTable, 2, rowSums)
   totalFrame=data.frame(Source=rep("Total",4), 
                         AuthorName=rep("Total",4), 
                         Experiment=rep(NA,4),
                         Year=rep(NA,4), 
                         Group=c("Control", "Social Norm", "Control", "Social Norm"),
                         Towel.Reuse=c("Yes", "Yes", "No", "No"),
                         Count=c(total2x2[1,1], total2x2[2,1], total2x2[1,2], total2x2[2,2]))
   
   rawData=rbind(rawData,totalFrame)


# Calculate BF and Posterior Odds Ratio 

   exList=unique(rawData$Source) #list with unique experiments
   
   # BayesOR=matrix(NA, nrow=length(exList), ncol=10000) #samples from posterior odds ratio distribution 
   # rownames(BayesOR)=exList
   
   # Initialize vectors to store bf_1u and bf_cu for each study
   bf_1u_vec <- rep(NA, times=length(exList))
   bf_cu_vec <- rep(NA, times=length(exList))
   bf_10_vec <- rep(NA, times=length(exList))
   bf_1c_vec <- rep(NA, times=length(exList))

   # Set seed for reproducibility
   set.seed(45)
   
   for (i in 1:length(exList)) {
      
      #extract 2x2 table 
         thisEx=rawData[rawData$Source==exList[i],]
         table2x2=cbind(yes=thisEx[1:2,"Count"],no=thisEx[3:4,"Count"] )
         rownames(table2x2)=c("control", "socialNorm")
   
      #Bayesian posterior odds ratio 
         X=contingencyTableBF(table2x2, sampleType="indepMulti", fixedMargin="rows", priorConcentration = 1)
         
         # Sample from alternative model
         c1 = posterior(X, iterations = 10000)
         # Sample from null model
         c2 = posterior(1/X, iterations = 10000)
         
         data<-as.data.frame(c1,col.names=c("lambda11","lambda21","lambda12","lambda22"))
         
         # BayesOR[i,]<-(data[,2]*data[,3])/(data[,1]*data[,4])
      
      #---------------------------------------------------------
      # Main adaptations start here:
      #---------------------------------------------------------

      # To calculate the directed BF (social norm > control):

      # BF_u0 (unconstrained vs null)
      bf_u0 <- exp(as.numeric(X@bayesFactor$bf))
      # -> referred to as bf1 in the original script, but conceptually,
      # the undirected H1 here is equal to the unconstrained model
      # Therefore, we use "1" here to denote the directed hypothesis
      
      post.result = BayesFactor::posterior(X, iterations = 10000)
      
      index <- grep(pattern="omega", x=colnames(post.result))
      theta <- as.data.frame(post.result[,index])
   
      # The first two columns of theta contain the relevant posterior samples
      # for the hypothesis:
      # column 1: proportion of towel reuse in the control condition
      # column 2: proportion of towel reuse in the social norm condition

      # Therefore, to calculate the directed BF (social norm > control),
      # we need to calculate the proportion of posterior samples in line
      # with the hypothesis
      prop.consistent <- mean(theta[,1] < theta[,2]) 

      # The BF for the directed hypothesis (social norm > control)
      # is then: BF_10 = BF_u0 * BF_1u = BF_u0 * P(H1|D) / P(theta in H1)
      bf_1u <- prop.consistent / 0.5 # since the prior is symmetric, P(theta in H1) = 0.5
      bf_10 <- bf_u0 * bf_1u

      # The complement to the predicted hypothesis 'social norm > control' is
      # 'social norm < control'
      # To compute the BF for the complement against the null, we first
      # compute the evidence in favor of the complement
      prop.complement <- mean(theta[,1] > theta[,2])

      # And then calculate the BF_c0 = BF_u0 * P(Hc|D) / P(Hc)
      bf_c0 <- bf_u0 * prop.complement / 0.5

      # Next, for step (1) of 'computing the complete complement', we need
      # a BF_1u and a BF_cu.
      # Since we have the BF of each H1, Hc and Hu against H0, by transitivity:
      # bf_1u <- bf_10 / bf_u0
      bf_cu <- bf_c0 / bf_u0

      # Finally, compute BF_1c = BF_1u / BF_cu
      bf_1c <- bf_1u / bf_cu
      
      # Store BFs in vectors
      bf_1u_vec[i] <- bf_1u
      bf_cu_vec[i] <- bf_cu
      bf_10_vec[i] <- bf_10
      bf_1c_vec[i] <- bf_1c
   }

# Create data frame with results
   results_df <- data.frame(
     Study = exList,
     bf_10 = bf_10_vec,
     bf_1u = bf_1u_vec,
     bf_1c = bf_1c_vec,
     bf_cu = bf_cu_vec
   )

# Drop row where Study is "Total" (since this is the result from pooled analysis)
   results_df <- results_df %>%
      filter(Study != "Total")

# Print results_df with values rounded to 2 decimal places
   print(results_df %>% mutate(across(starts_with("bf_"), \(x) round(x, digits = 2))))

# Create dataframe that is compatible with the 'compute_joint_complements' function
   final_df <- results_df %>%
      select(Study, bf_1u, bf_cu) %>%
      rename(
         H1 = bf_1u,
         Hc = bf_cu) %>%
      mutate(
         P_theta_in_Hc = 0.5
      )

#----------------------------------------------------------------------------------
# -> BF_10(joint) ≈ 0.0007
bf_10 <- prod(results_df$bf_10)

# -> BF_1u(joint) ≈ 0.40
bf_1u <- prod(results_df$bf_1u)

# -> BF_1c(joint) ≈ 3000
bf_1c <- prod(results_df$bf_1c)

# Now compute complete complement
set.seed(45)
res <- compute_joint_complements(final_df,
                          replace_0_with = 0.001,
                          round_res = FALSE)


# -> BF_1c*(joint) ≈ 0.003
bf_1c_star <- res["BES_c","H1"] / res["BES_c_star","Hc*"] # = BF_1u(joint) / BF_c*u(joint)

#----------------------------------------------------------------------------------
### Display results

# Functions to format numbers as strings for display
fmt2 <- function(x) sprintf("%.2f", x) # 2dp
fmtE <- function(x) sprintf("%.2e", x) # 2dp in scientific notation

# Round study BFs
rounded_results_df <- results_df %>%
   mutate(across(starts_with("bf_"), \(x) round(x, digits = 2)))

# Save as text for paste()
study_table_text <- capture.output(print(rounded_results_df))

# Full output
output_lines <- c(
   "",
   "",
   "-------------------------------",
   "REANALYSIS SCHEIBEHENNE (2016)",
   "-------------------------------",
   "",
   "Study-specific Bayes Factors:",
   "- - - - - - - - - - - - - - -",
   paste(study_table_text, collapse = "\n"),
   "",
   "Joint Bayes Factors:",
   "- - - - - - - - - -",
   paste0("BF_10(joint) ≈ ", fmt2(bf_10), " (", fmtE(bf_10), ")"),
   paste0("BF_1u(joint) ≈ ", fmt2(bf_1u), " (", fmtE(bf_1u), ")"),
   paste0("BF_1c(joint) ≈ ", fmt2(bf_1c), " (", fmtE(bf_1c), ")"),
   paste0("BF_1c*(joint) ≈ ", fmt2(bf_1c_star), " (", fmtE(bf_1c_star), ")"),
   ""
)

# Print results
cat(paste(output_lines, collapse = "\n"), "\n", sep = "")




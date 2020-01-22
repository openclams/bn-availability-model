this.dir <- dirname(parent.frame(2)$ofile)
setwd(this.dir)
a <- list()
a <- c(a,list(cptable( ~D1, values=c(0.0002,0.9998), levels=c("D1_0","D1_1"))))
a <- c(a,list(cptable( ~D2, values=c(0.0,1.0), levels=c("D2_0","D2_1"))))
df <- read.table("R1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~R1+D1, values=b, levels=c("R1_0","R1_1"))))
df <- read.table("R2.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~R2+D1, values=b, levels=c("R2_0","R2_1"))))
df <- read.table("R3.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~R3+D2, values=b, levels=c("R3_0","R3_1"))))
df <- read.table("H1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~H1+R1, values=b, levels=c("H1_0","H1_1"))))
df <- read.table("H2.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~H2+R1, values=b, levels=c("H2_0","H2_1"))))
df <- read.table("H3.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~H3+R1, values=b, levels=c("H3_0","H3_1"))))
df <- read.table("H4.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~H4+R2, values=b, levels=c("H4_0","H4_1"))))
df <- read.table("H5.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~H5+R2, values=b, levels=c("H5_0","H5_1"))))
df <- read.table("H6.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~H6+R2, values=b, levels=c("H6_0","H6_1"))))
df <- read.table("H7.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~H7+R3, values=b, levels=c("H7_0","H7_1"))))
df <- read.table("H8.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~H8+R3, values=b, levels=c("H8_0","H8_1"))))
df <- read.table("H9.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~H9+R3, values=b, levels=c("H9_0","H9_1"))))
df <- read.table("N1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~N1+R1, values=b, levels=c("N1_0","N1_1"))))
df <- read.table("N2.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~N2+R1, values=b, levels=c("N2_0","N2_1"))))
df <- read.table("N3.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~N3+R2, values=b, levels=c("N3_0","N3_1"))))
df <- read.table("N4.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~N4+R3, values=b, levels=c("N4_0","N4_1"))))
df <- read.table("G1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~G1+R1, values=b, levels=c("G1_0","G1_1"))))
a <- c(a,list(cptable( ~N5, values=c(0.0,1.0), levels=c("N5_0","N5_1"))))
df <- read.table("er_R_0.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_R_0+H1, values=b, levels=c("er_R_0_0","er_R_0_1"))))
df <- read.table("er_R_1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_R_1+H2, values=b, levels=c("er_R_1_0","er_R_1_1"))))
df <- read.table("er_R_2.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_R_2+H4, values=b, levels=c("er_R_2_0","er_R_2_1"))))
df <- read.table("er_R_3.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_R_3+H5, values=b, levels=c("er_R_3_0","er_R_3_1"))))
df <- read.table("er_R_4.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_R_4+H6, values=b, levels=c("er_R_4_0","er_R_4_1"))))
df <- read.table("er_R_5.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_R_5+H7, values=b, levels=c("er_R_5_0","er_R_5_1"))))
df <- read.table("er_R_6.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_R_6+H7, values=b, levels=c("er_R_6_0","er_R_6_1"))))
df <- read.table("er_0_G1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_0_G1+er_0_G1_OR+G1+er_R_0, values=b, levels=c("er_0_G1_0","er_0_G1_1"))))
df <- read.table("er_1_G1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_1_G1+er_1_G1_OR+G1+er_R_1, values=b, levels=c("er_1_G1_0","er_1_G1_1"))))
df <- read.table("er_2_G1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_2_G1+er_2_G1_OR+G1+er_R_2, values=b, levels=c("er_2_G1_0","er_2_G1_1"))))
df <- read.table("er_3_G1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_3_G1+er_3_G1_OR+G1+er_R_3, values=b, levels=c("er_3_G1_0","er_3_G1_1"))))
df <- read.table("er_4_G1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_4_G1+er_4_G1_OR+G1+er_R_4, values=b, levels=c("er_4_G1_0","er_4_G1_1"))))
df <- read.table("er_5_G1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_5_G1+er_5_G1_OR+G1+er_R_5, values=b, levels=c("er_5_G1_0","er_5_G1_1"))))
df <- read.table("er_6_G1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_6_G1+er_6_G1_OR+G1+er_R_6, values=b, levels=c("er_6_G1_0","er_6_G1_1"))))
df <- read.table("erP_1.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~erP_1+N5+N3+N2+N1, values=b, levels=c("erP_1_0","erP_1_1"))))
df <- read.table("erP_2.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~erP_2+N2+N1, values=b, levels=c("erP_2_0","erP_2_1"))))
df <- read.table("erP_3.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~erP_3+N2+N3, values=b, levels=c("erP_3_0","erP_3_1"))))
df <- read.table("erP_4.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~erP_4+N5+N3, values=b, levels=c("erP_4_0","erP_4_1"))))
df <- read.table("erP_5.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~erP_5+N5+N3+N2+N4, values=b, levels=c("erP_5_0","erP_5_1"))))
df <- read.table("erP_6.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~erP_6+N2+N4, values=b, levels=c("erP_6_0","erP_6_1"))))
df <- read.table("er_0_G1_OR.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_0_G1_OR+erP_2+erP_1, values=b, levels=c("er_0_G1_OR_0","er_0_G1_OR_1"))))
df <- read.table("er_1_G1_OR.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_1_G1_OR+erP_2+erP_1, values=b, levels=c("er_1_G1_OR_0","er_1_G1_OR_1"))))
df <- read.table("er_2_G1_OR.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_2_G1_OR+erP_4+erP_3, values=b, levels=c("er_2_G1_OR_0","er_2_G1_OR_1"))))
df <- read.table("er_3_G1_OR.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_3_G1_OR+erP_4+erP_3, values=b, levels=c("er_3_G1_OR_0","er_3_G1_OR_1"))))
df <- read.table("er_4_G1_OR.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_4_G1_OR+erP_4+erP_3, values=b, levels=c("er_4_G1_OR_0","er_4_G1_OR_1"))))
df <- read.table("er_5_G1_OR.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_5_G1_OR+erP_6+erP_5, values=b, levels=c("er_5_G1_OR_0","er_5_G1_OR_1"))))
df <- read.table("er_6_G1_OR.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er_6_G1_OR+erP_6+erP_5, values=b, levels=c("er_6_G1_OR_0","er_6_G1_OR_1"))))
df <- read.table("er.csv",header=FALSE)
b <- df[[1]]
a <- c(a,list(cptable( ~er+er_6_G1+er_5_G1+er_4_G1+er_3_G1+er_2_G1+er_1_G1+er_0_G1, values=b, levels=c("er_0","er_1"))))
plist <- compileCPT(a)
net1 <- grain(plist)

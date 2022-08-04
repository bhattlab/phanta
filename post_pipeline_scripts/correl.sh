#!/bin/bash
otu=$1 #otu table
outdir=$2 #output directory
threads=${3:-10} #number of threads
permutations=${4:-100} #number of permutations
p=${5-0.05} #minimal p-value
base=`basename $otu`
prefix=${base%.*}

echo $prefix
echo  $outdir"/"$prefix"_correl.txt"
#run fastspar to calculate median correlation
fastspar --otu_table "$otu" --correlation $outdir"/"$prefix"_correl.txt"  --covariance $outdir"/"$prefix"_cov.txt" --threads $threads

mkdir -p  $outdir"/bootstrap_counts"
mkdir -p $outdir"/bootstrap_correlation" 

##create permutations of counts
fastspar_bootstrap --otu_table "$otu" --number $permutations --prefix  $outdir/bootstrap_counts/count

#calculate correlation per permutation
parallel fastspar --otu_table {} --correlation  $outdir/bootstrap_correlation/cor_{/} --covariance  $outdir/bootstrap_correlation/cov_{/} -i $threads :::  $outdir/bootstrap_counts/*   

#calculate p-value
fastspar_pvalues --otu_table "$otu" --correlation  $outdir"/"$prefix"_correl.txt" --prefix  $outdir/bootstrap_correlation/cor_count_ --permutations $permutations --outfile $outdir"/"$prefix"_pvalues.tsv"

#filter for interkingdom correlations below specified p-value
#python filter_interkingdom.py  $outdir"/"$prefix"_correl.txt" $outdir"/"$prefix"_pvalues.tsv" $p $outdir"/"$prefix"_interkingdom_correlations.tsv"

#delete temporary directories
rm -R $outdir"/bootstrap_counts/"
rm -R $outdir"/bootstrap_correlation/"

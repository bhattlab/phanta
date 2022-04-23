#!/bin/bash

# arguments: 1) sample name, 2) directory where Kraken2/Bracken reports are, 3) path to output file

# first - calculate total reads in the sample - add total reads classified under root
# by Kraken2 and total reads unclassified by Kraken2

root=$(grep 'root' $2/$1.krak.report | head -n 1 | cut -f 2 | xargs)
unclassified_krak=$(grep 'unclassified' $2/$1.krak.report | head -n 1 | cut -f 2 | xargs)
tot_reads=$(($root+$unclassified_krak))

# next - calculate total BRACKEN-CLASSIFIED reads in the sample
tot_reads_bracken=$(head -n 1 $2/$1.krak.report_bracken_species.filtered | cut -f 2 | xargs)

# how many reads were left out by Bracken?
unclassified_brack="$((tot_reads-tot_reads_bracken))"

echo -e "$1\t${tot_reads}\t${unclassified_krak}\t${tot_reads_bracken}\t${unclassified_brack}" > $3

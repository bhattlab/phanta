#!/bin/bash

# arguments: 1) sample name, 2) directory where Kraken2/Bracken reports are, 3) path to output file

# Check if "bc" command is available
if ! command -v bc &> /dev/null; then
    echo "Error: 'bc' calculator is not installed."
    exit 1
fi

# first - calculate total reads in the sample - add total reads classified under root
# by Kraken2 and total reads unclassified by Kraken2

root=$(grep 'root' $2/$1.krak.report | head -n 1 | cut -f 2 | xargs)
unclassified_krak=$(grep 'unclassified' $2/$1.krak.report | head -n 1 | cut -f 2 | xargs)
if [[ -z $root ]] && [[ -z $unclassified_krak ]]
then
  echo "No reads in sample"
  exit 64
elif [[ -z $root ]]
then
  tot_reads=$unclassified_krak
elif [[ -z $unclassified_krak ]]
then
  tot_reads=$root
else
  tot_reads=$(($root+$unclassified_krak))
fi

# next - calculate total BRACKEN-CLASSIFIED reads in the sample
tot_reads_bracken=$(cut -f 6 $2/$1.krak.report.filtered.bracken | tail -n +2 | paste -sd+ | bc)

# how many reads were left out by Bracken?
unclassified_brack="$((tot_reads-tot_reads_bracken))"

echo -e "$1\t${tot_reads}\t${unclassified_krak}\t${tot_reads_bracken}\t${unclassified_brack}" > $3

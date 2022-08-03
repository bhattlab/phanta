# The HumGut+MGVAll Database: Overview, How to Download, and Instructions to Build from Scratch

# TODO - Fill this page in at some point.

## Overview of the database

This database is compatible with Kraken2 and Bracken. These programs use taxonomic information to classify metagenomic sequence reads and estimate taxonomic abundances. Therefore, the database includes not only genomes and other sequences (below) but also taxonomic information for all of these genomes/sequences.

## Genomes and sequences present
### Prokaryotes
- 30,691 prokaryotic genomes from the HumGut database (https://doi.org/10.1186/s40168-021-01114-w)
### Viruses
- All 189,680 genomes from the Metagenomic Gut Virus (MGV) database (https://doi.org/10.1038/s41564-021-00928-6)
- All (~12,000) complete viral genomes/proteins from RefSeq (downloaded using Kraken2's download-library functionality; see below)
### Eukaryotes
- Human genome
- All (~75) complete fungal genomes/proteins from RefSeq (downloaded using Kraken2's download-library functionality; see below)
### Other
- UniVec_Core: a subset of an NCBI-supplied database of common 'contaminant' sequences in sequencing projects (downloaded using Kraken2's download-library functionality - see below)

## To download the database that we built

Navigate to the following link:
# TODO INSERT LINK HERE

## Instructions for building the database from scratch

### Step One - gather sequences and taxonomy information for the HumGut genomes and the human genome.

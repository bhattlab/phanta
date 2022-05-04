# Instructions for building the HumGut+MGVAll Kraken2/Bracken Databases

## Genomes and sequences in the database
### Prokaryotes
- 30,691 prokaryotic genomes from the HumGut database (https://doi.org/10.1186/s40168-021-01114-w)
### Viruses
- All 189,680 genomes from the Metagenomic Gut Virus (MGV) database (https://doi.org/10.1038/s41564-021-00928-6)
- All complete viral genomes/proteins from RefSeq (downloaded using Kraken2's download-library functionality; see below)
### Eukaryotes
- Human genome
- All complete fungal genomes/proteins from RefSeq (downloaded using Kraken2's download-library functionality; see below)
### Other
- UniVec_Core: a subset of an NCBI-supplied database of common 'contaminant' sequences in sequencing projects (downloaded using Kraken2's download-library functionality - see below)

### Note that, as required for all Kraken2/Bracken databases, the database contains
### taxonomy information for all the genomes and sequences listed above.

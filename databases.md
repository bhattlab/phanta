# Currently available Phanta databases

| Name/Link  | Prokaryotic Portion | Viral Portion  | Prophage-masked? | Taxonomy for Prokaryotic Portion | Comments |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| [Default database](http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/unmasked_db_v1.01.tar.gz)  | HumGut | MGV + RefSeq viral  | N | NCBI | Default database (as described in our manuscript) |
| [Masked version of default database](http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/masked_db_v1.tar.gz)  | HumGut | MGV + RefSeq viral  | Y | NCBI | Prophage-masked version of default database (as described in our manuscript) |
| [Default database - GTDB](http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/unmasked_db_v1_gtdb.tar.gz)  | HumGut | MGV + RefSeq viral  | N | GTDB | Default database with GTDB taxonomy for prokaryotic portion |
| [UHGGV2 + MGV](http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/uhgg2_mgv_v1.tar.gz)  | UHGGV2 | MGV + RefSeq viral  | N | GTDB | Default database with UHGGv2 replacing HumGut. UHGGv2 includes low-prevalence prokaryotes filtered by HumGut |
| [HumGut + UHGV "MQ+"](http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/humgut_uhgv_mqplus_v1.tar.gz)  | HumGut | UHGV ($\ge$ medium-quality genomes)  | N | NCBI | Same as default database but replacing the viral portion with new viral genome catalog [UHGV](https://github.com/snayfach/UHGV). Here we included UHGV genomes $\ge$ medium-quality |
| [HumGut + UHGV "HQ+"](http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/humgut_uhgv_hqplus_v1.tar.gz)  | HumGut | UHGV ($\ge$ high-quality genomes)  | N | NCBI | Same as previous line but using only $\ge$ high-quality UHGV genomes |
| [UHGGv2 + UHGV "MQ+"](http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/uhgg2_uhgv_v1.tar.gz)  | UHGGV2 | UHGV ($\ge$ medium-quality genomes)  | N | GTDB | UHGGv2 for prokaryotic portion; UHGV for viral portion ($\ge$ medium-quality genomes) |

## Each database should include the following files:

Kraken2 database
1. hash.k2d
2. taxo.k2d
3. opts.k2d
4. seqid2taxid.map

Bracken databases (built for use with various read lengths N):
1. databaseNmers.kmer_distrib

Additional files required for pipeline to run:
1. inspect.out
2. taxonomy/nodes.dmp
3. taxonomy/names.dmp
4. library/species_genome_size.txt

For use with post-processing scripts:
1. host_prediction_to_genus.tsv
2. species_name_to_vir_score.txt
 
*Note*: Phanta was developed with human gut metagenomes in mind. Phanta's default database was built based on human-gut viral and bacterial genomes. If you wish to apply Phanta on non human gut metagenomes you'll probably need to supply a custom database. In such cases please open new [discussion](https://github.com/bhattlab/phanta/discussions/categories/phanta-dbs) and we can discuss the best way to help/collaborate on that.

The total tar.gz file should be about 20-25 GB (depends on the exact version).

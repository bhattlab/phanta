# Currently available Phanta databases

Each database should include the following files:


Kraken2 database
1. hash.k2d
2. taxo.k2d
3. opts.k2d
4. seqid2taxid.map

Bracken databases (built for use with various read lengths N):
1. database<N>mers.kmer_distrib

Additional files required for pipeline to run:
1. inspect.out
2. taxonomy/nodes.dmp
3. taxonomy/names.dmp
4. library/species_genome_size.txt

For use with post-processing scripts:
1. host_prediction_to_genus.tsv
2. species_name_to_vir_score.txt
 
*Note*: Phanta was developed with human gut metagenomes in mind. Phanta's default database was built based on human-gut viral and bacterial genomes. If you wish to apply Phanta on non human gut metagenomes you'll probably need to supply a custom database. In such cases please open new [discussion](https://github.com/bhattlab/phanta/discussions/categories/phanta-dbs) and we can discuss the best way to help/collaborate on that.

The total tar.gz file should be about 20-25 GB (depends on exact version).

 # Version 1
* Default database (as described in our manuscript)- http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/test_dataset.tar.gz
* Prophage masked database (as described in our manuscript) http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/masked_db_v1.tar.gz. See [Advanced Usage](#https://github.com/bhattlab/phanta#advanced-usage).
* Default database that uses the GTDB taxonomy for bacteria and Archaea (instead of NCBI taxonomy). http://ab_phanta.os.scg.stanford.edu/Phanta_DBs/unmasked_db_v1_gtdb.tar.gz This taxonomy is equivalent to that provided by HumGut, with the exception that taxonomic IDs for GTDB nodes starts with 5,000,000 rather than 4,000,000. See Humgut [documentation](#https://arken.nmbu.no/~larssn/humgut/)

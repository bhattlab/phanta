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

## Creating a custom database

Phanta is based on Kraken2/Bracken. As a result, as you can see above, the main components of a Phanta database are a Kraken2 database and Bracken database(s). After you have these, you’re almost there! More details below.

### Steps to make a Phanta database

### Step one: create a custom Kraken2 database.

You can either follow the recommendations of the Kraken2 developers [here](https://github.com/DerrickWood/kraken2/blob/master/docs/MANUAL.markdown#custom-databases), or the recommendations below. 

#### Step 1A: define taxonomic relationships between the genomes in your database.

For every genome in the database, you will need to have both a taxonomic ID and the name. Additionally, you will need this information for all higher taxonomic ranks in the lineage of each genome. 

Then, you will use this information to make the following two files:

- names.dmp
- nodes.dmp

The names.dmp file specifies the taxid and name of each taxon in the database. To enter lines in our names.dmp file, we use the following Python code (generally as part of a “for loop”):

```jsx
names_file.write(str(taxid) + "\t|\t" + name + "\t|\t-\t|\tscientific name\t|\n")
```

Each line of the nodes.dmp file specifies a parent-child taxonomic relationship. To enter lines in our nodes.dmp file, we use the following Python code (generally as part of a “for loop”):

```jsx
nodes_file.write(str(taxid) + "\t|\t" + str(parent_taxid) + "\t|\t" + rank + "\t|\t-\t|\n")
```

If you would like some suggestions about how to designate taxonomic relationships between viral genomes, please see “Suggestions for viral taxonomy” below.

Now, create a new empty folder for your database. **Put the names.dmp/nodes.dmp** into a subfolder called `taxonomy`.

#### Step 1B: gather all the genomes that you would like to include in your database.

Create a multifasta file with all the genomes that you would like to add to your database. Then assign each genome a unique taxonomic ID. Put this unique taxonomic ID in the header line for each genome, in the following format:

```jsx
>genome_name|kraken:taxid|XXXXX

# example
>MGYG000000001_1|kraken:taxid|3012254
```

Then formally “add” them to the database using the following command (adjusting the threads as needed):

`kraken2-build --add-to-library path_to_fasta_file --db path_to_database_folder --threads 8`

#### Step 1C: create the Kraken2 database via the following command.

`kraken2-build --build --db path_to_database_folder --threads 8`  

#### Step 1D: “inspect” the Kraken2 database to check that the taxonomic relationships in the database are consistent with what you aimed to specify.

`kraken2-inspect --db path_to_database_folder --report-zero-counts --threads 8 > inspect.out`

This command will generate an “inspection report” - we recommend checking the taxonomy that is specified for a few species in various domains.

### Step 2: build the Bracken-compatible portion of the database by running the following command.

`bracken-build -d path_to_database_folder -t 10 -l 150`

Adjust the threads and -l argument as necessary (this specifies the read length for the sequences that will be classified with this Bracken database). Note that you can create multiple Bracken DBs for each database, for each of the different read lengths you desire.

#### Step 3: calculate genome size.

Utilize the `calculate_genome_size.py` script provided in the `pipeline_scripts` subfolder of this repo. 

Usage: `python calculate_genome_size.py /path/to/database/folder` 

#### Step 4 (optional): create files necessary for using the postprocessing scripts.

There are two files you will need to create:

1. host_prediction_to_genus.tsv
    1. This tab-separated file should contain two columns, named `species_taxa` and `Host genus`. The first column should contain viral species taxids, and the second should contain the predicted host.  
    2. You can predict a host using many different tools, for example using [iPHoP](https://bitbucket.org/srouxjgi/iphop/src/main/). You do not need to assign a host for every viral species and thus you can omit some viral species from the host_prediction_to_genus file.
    3. Here are the first five lines of host_prediction_to_genus.tsv for the default Phanta database, as an example:

```jsx
species_taxa	Host genus
4005213	d__Bacteria;p__Firmicutes_A;c__Clostridia;o__Oscillospirales;f__Ruminococcaceae;g__Ruminococcus_D
4005409	d__Bacteria;p__Firmicutes_A;c__Clostridia;o__Oscillospirales;f__Ruminococcaceae;g__Ruminococcus_D
4005420	d__Bacteria;p__Firmicutes_A;c__Clostridia;o__Oscillospirales;f__Acutalibacteraceae;g__Ruminococcus_E
4005427	d__Bacteria;p__Firmicutes_A;c__Clostridia;o__Oscillospirales;f__Oscillospiraceae;g__UBA738
```

1. species_name_to_vir_score.txt
    1. This tab-separated file should contain two columns with no header.
    2. First column contains the species name - second column contains the predicted ‘virulence score’ (from 0 to 1). To get this score, you can use [BACPHLIP](https://github.com/adamhockenberry/bacphlip) or a similar tool.
    3. Here are the first five lines of species_name_to_vir_score.txt for the default Phanta database, as an example:

```jsx
Yak enterovirus 0.8118782016546136
Mycobacterium phage Contagion   0.012499999999999956
Kadipiro virus  0.8118782016546136
Rotavirus C     0.8118782016546136
Alfalfa mosaic virus    0.8118782016546136
```

#### Suggestions for viral taxonomy

- Cluster the genomes to the species-level using a 95% ANI threshold (85% alignment fraction), as recommended by [MIUViG](https://www.nature.com/articles/nbt.4306). In the default Phanta database, we chose to include all the genomes in the final database; we designated each genome as a “strain” of the relevant species cluster.
- Then assign higher ranks. As described in the [methods](https://www.nature.com/articles/s41587-023-01799-4#Sec19) of the Phanta paper, you can use clustering to assign some of the higher ranks (e.g., genus). However, as also mentioned in the methods, we recommend to eventually merge the clustering-based taxonomy with a well-recognized viral taxonomy, such as ICTV.

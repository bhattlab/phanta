# Run Phanta

At the root of this repository you will find a helper script to automatically
run Phanta given an input directory with the FASTQ files: `run_phanta.py`.

The script will create a config file (`config.yaml`) and a samplesheet (`mapping.txt`)
and can be run, from the same environment as Phanta, as follows:

```bash
python run_phanta.py --db <DB_DIR> -i <input_dir> -o <output_dir>  [--run]
```

## Synopsis

```text
usage: Run Phanta [-h] [-i INPUT_DIR] [-s SAMPLE_SHEET] [-p PHANTA_DIR] [-d DB_DIR] -o OUTPUT_DIR [-c CORES] [-t THREADS] [-w WORK_DIR] [--fwd FWD] [--rev REV]
                  [--verbose] [--run] [--wait]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input-dir INPUT_DIR
                        Input directory with the FASTQ files
  -s SAMPLE_SHEET, --sample-sheet SAMPLE_SHEET
                        Alternative to input directory
  -p PHANTA_DIR, --phanta-dir PHANTA_DIR
                        Phanta directory [default: /qib/platforms/Informatics/telatin/git/phanta]
  -d DB_DIR, --db-dir DB_DIR
                        Phanta directory [default: /qib/platforms/Informatics/transfer/outgoing/databases/phanta_dbs/default_V1/]
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory
  -c CORES, --cores CORES
                        Total cores [default: 1]
  -t THREADS, --threads THREADS
                        Total threads [default: 16]
  -w WORK_DIR, --work-dir WORK_DIR
                        Scripts directory [default: tempdir]
  --fwd FWD             Forward read suffix [default: _R1]
  --rev REV             Reverse read suffix [default: _R2]
  --verbose             Verbose output
  --run                 Run the pipeline
  --wait                Wait for pipeline execution end (not recommended)
  ```

## Notable options

* `-w WORKDIR`: in this directory the script will create the configuration file and mapping file. By default will create a new directory in the system `$TMPDIR` (e.g. /tmp/tmpx72tkdko), but to store the mapping file you can specify a new directory (will be created)
* `-c CORES`: number of cores to use for the pipeline
* `--run`: will run snakemake, otherwise will just create the configuration files and print the command to run

## Environment variables

To avoid passing the database path, you can set:

```bash
export PHANTA_DB=/path/to/phanta_db
```

if you install the script in a location different from the root of the repository:

```bash
export PHANTA_DIR=/path/to/phanta
```


# Run Phanta

At the root of this repository you will find a helper script to automatically
run Phanta given an input directory with the FASTQ files: `run_phanta.py` - helpfully contributed by @telatin.

The script will create a config file (`config.yaml`) and a samplesheet (`mapping.txt`)
and can be run, from the same environment as Phanta, as follows:

```text
usage: python run_phanta.py [-h] [-i INPUT_DIR] [-s SAMPLE_SHEET] [-p PHANTA_DIR] [-d DB_DIR] -o OUTPUT_DIR
                  [-l READ_LENGTH] [-c CORES] [-t THREADS] [-w WORK_DIR] [-b BAC_COV] [-v VIR_COV]
                  [-e EUK_COV] [-a ARC_COV] [-f CONFIDENCE] [-br BRACKEN_FILTER] [-ng] [-k] [--fwd FWD]
                  [--rev REV] [--verbose] [--run] [--wait]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input-dir INPUT_DIR
                        Input directory with the FASTQ files
  -s SAMPLE_SHEET, --sample-sheet SAMPLE_SHEET
                        Alternative to input directory
  -p PHANTA_DIR, --phanta-dir PHANTA_DIR
                        Phanta directory 
  -d DB_DIR, --db-dir DB_DIR
                        Phanta database directory [default: None]
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory
  -l READ_LENGTH, --read_length READ_LENGTH
                        Read length [default: 150]
  -c CORES, --cores CORES
                        Total cores [default: 1]
  -t THREADS, --threads THREADS
                        Total threads [default: 16]
  -w WORK_DIR, --work-dir WORK_DIR
                        Scripts directory [default: tempdir]
  -b BAC_COV, --bac_cov BAC_COV
                        Bacterial coverage threshold [default: 0.01]
  -v VIR_COV, --vir_cov VIR_COV
                        Viral coverage threshold [default: 0.1]
  -e EUK_COV, --euk_cov EUK_COV
                        Eukaryotic coverage threshold [default: 0]
  -a ARC_COV, --arc_cov ARC_COV
                        Archaeal coverage threshold [default: 0.01]
  -f CONFIDENCE, --confidence CONFIDENCE
                        Kraken2 classification confidence [default: 0.1]
  -br BRACKEN_FILTER, --bracken_filter BRACKEN_FILTER
                        Bracken reads threshold [default: 10]
  -ng, --nongzipped     Specify if your files aren't gzipped
  -k, --keepintermediate
                        Specify if you want to keep intermediate files
  --fwd FWD             Forward read suffix [default: _R1]
  --rev REV             Reverse read suffix [default: _R2]
  --verbose             Verbose output
  --run                 Run the pipeline
  --wait                Wait for pipeline execution end (not recommended)
  ```

## Notes about specific arguments

* `-w WORK_DIR`: in this directory the script will create the configuration file and mapping file. By default will create a new directory in the system `$TMPDIR` (e.g. /tmp/tmpx72tkdko), but you can specify a new directory instead (will be created)
* `-c CORES`: number of cores to use for the pipeline
* `--run`: will run snakemake, otherwise will just create the config/mapping files and print the command to run. Please note, the snakemake command in the runner script may not work for your system. Specifically, you may have to replace the --cores and max-threads arguments with a [profile for Snakemake execution](https://github.com/Snakemake-Profiles/) depending on your setup (e.g., replace with --profile slurm)).

If your FASTQ files are not denoted by `_R1` and `_R2` to demark the paired ends,
you can specify the suffixes with `--fwd` and `--rev`:
* `--fwd`: forward read suffix [default: `_R1`]
* `--rev`: reverse read suffix [default: `_R2`]

## Environment variables

To avoid having to pass the database path as an argument, you can set:

```bash
export PHANTA_DB=/path/to/phanta_db
```


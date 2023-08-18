#!/usr/bin/env python3
"""
Use Python 3.6+ to run Phanta

Tip, to avoid typing paths:
export PHANTA_DIR=/path/to/phanta-repo
export PHANTA_DB=/path/to/phanta_dbs/default_V1/

Andrea Telatin, 2023
"""
import yaml
import argparse
import logging
import os
import tempfile
import subprocess
import sys
import shutil


VERSION = "0.3.0"

def which_dep(command):
    """
    
    """
    try:
        which = shutil.which(command)
        logger.info("Found %s at %s" % (command, which))
        return True
    except Exception as e:
        logger.info("Dependency %s not found: %s" % (command, e))
        return False

def check_dep(command):
    # Get output
    logger.info("Running %s" % " ".join(command))
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        logger.debug("Checking %s got: %s" % (" ".join(command), output.decode("utf-8")))
        return True
    except subprocess.CalledProcessError as e:
        logger.debug("Dependency %s not found:\n  %s" % (command, e))
        return False
    except Exception as e:
        logger.info("Dependency %s not found:\n  %s" % (command, e))
def make_mapping(input_dir, output_file, for_tag, rev_tag):
    files = {}
    # Why limiting the extensions? Because enough is enough, that's why.
    # You can forget your .FASTQ or .FastQ files to be analysed. 
    extensions = [".fastq.gz", ".fq.gz", ".fastq", ".fq"]
    for root, dirs, filenames in os.walk(input_dir):
        for filename in filenames:
            for ext in extensions:
                if filename.endswith(ext):
                    stripped = filename.replace(ext, "")
                    if stripped.endswith(for_tag):
                        sample = stripped.replace(for_tag, "")
                        if sample not in files:
                            files[sample] = {}
                        files[sample]["forward"] = os.path.join(root, filename)
                    elif stripped.endswith(rev_tag):
                        sample = stripped.replace(rev_tag, "")
                        if sample not in files:
                            files[sample] = {}
                        files[sample]["reverse"] = os.path.join(root, filename)
                    else:
                        logging.warning("Skipping file %s: does not match any tag (%s, %s)" % (filename, for_tag, rev_tag))
    
    found = 0
    with open(output_file, "w") as fh:
        for basename, paths in files.items():
            if "forward" in paths and "reverse" in paths:
                found += 1
                print(basename, paths["forward"], paths["reverse"], sep="\t", file=fh)
                logger.debug("Adding sample: %s" % basename)
    logger.info("Found %d samples" % found)
    
    return found


def getDefaults():
    """
    Try to find Phanta dir and DB dir, check:
    - Self dir
    - $ENV{"PHANTA_DIR"}
    - $ENV{"PHANTA_DB"}
    - inside phanta dir check files
    """
    phanta_dir, phanta_db = None, None
    
    # Check self dir: is the runner inside the phanta repository?
    self_dir = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists(os.path.join(self_dir, "pipeline_scripts")):
        phanta_dir = self_dir
    
    # Check environment variables $PHANTA_DIR and $PHANTA_DB
    if "PHANTA_DIR" in os.environ:
        if os.path.exists(os.path.join(os.environ["PHANTA_DIR"], "pipeline_scripts")):
            phanta_dir = os.environ["PHANTA_DIR"]
        else:
            print("WARNING: $PHANTA_DIR is set but not pointing to a valid installation. Will be ignored.", file=sys.stderr)

    if "PHANTA_DB" in os.environ:
        if os.path.exists(os.path.join(os.environ["PHANTA_DB"], "species_name_to_vir_score.txt")):
            phanta_db = os.environ["PHANTA_DB"]
        else:
            print("WARNING: $PHANTA_DB is set but not pointing to a valid installation (should contain 'species_name_to_vir_score.txt'). Will be ignored.", file=sys.stderr)
            
    
    if phanta_db is None and phanta_dir is not None:
        # Try loading config.yaml from phanta_dir
        config_file = os.path.join(phanta_dir, "config.yaml")
        if os.path.exists(config_file):
            with open(config_file, "r") as fh:
                config = yaml.load(fh, Loader=yaml.FullLoader)
                if "database" in config:
                    if os.path.exists(os.path.join(config["database"], "species_name_to_vir_score.txt")):
                        phanta_db = config["db_dir"]
    
    if phanta_dir is not None or phanta_db is not None:
        # If only one is valid, it's OK to print both as I assume
        # the intended use of ENV vars is to pass both
        print("--- PHANTA RUNNER ---", file=sys.stderr)
        print("Inferred Phanta installation: ", phanta_dir, file=sys.stderr)
        print("Inferred DB location:         ", phanta_db, file=sys.stderr)
    return phanta_dir, phanta_db
            
if __name__=="__main__":
    DEFAULT_PHANTA_DIR, DEFAULT_PHANTA_DB_DIR = getDefaults()
    args = argparse.ArgumentParser("Run Phanta")
    args.add_argument("-i", "--input-dir", help="Input directory with the FASTQ files")
    args.add_argument("-s", "--sample-sheet", help="Alternative to input directory")

    args.add_argument("-p", "--phanta-dir", help="Phanta directory [default: %(default)s]", default=DEFAULT_PHANTA_DIR)
    args.add_argument("-d", "--db-dir", help="Phanta database directory [default: %(default)s]", default=DEFAULT_PHANTA_DB_DIR)
    args.add_argument("-o", "--output-dir", help="Output directory", required=True)
    args.add_argument("-l", "--read_length", help="Read length [default: 150]", type=int, default=150)
    args.add_argument("-c", "--cores", help="Total cores [default: %(default)s]", type=int, default=1)
    args.add_argument("-t", "--threads", help="Total threads [default: %(default)s]", type=int, default=16)
    args.add_argument("-w", "--work-dir", help="Directory for the newly created config + sample sheet files [default: tempdir]")
    
    args.add_argument("-b", "--bac_cov", help="Bacterial coverage threshold [default: 0.01]", type=float, default=0.01)
    args.add_argument("-v", "--vir_cov", help="Viral coverage threshold [default: 0.1]", type=float, default=0.1)
    args.add_argument("-e", "--euk_cov", help="Eukaryotic coverage threshold [default: 0]", type=float, default=0)
    args.add_argument("-a", "--arc_cov", help="Archaeal coverage threshold [default: 0.01]", type=float, default=0.01)
    args.add_argument("-f", "--confidence", help="Kraken2 classification confidence [default: 0.1]", type=float, default=0.1)
    args.add_argument("-br", "--bracken_filter", help="Bracken reads threshold [default: 10]", type=int, default=10)
    
    args.add_argument("-ng", "--nongzipped", help="Specify if your files aren't gzipped", action="store_false")
    args.add_argument("-k", "--keepintermediate", help="Specify if you want to keep intermediate files ", action="store_false")
    args.add_argument("--fwd", help="Forward read suffix [default: %(default)s]", default="_R1")
    args.add_argument("--rev", help="Reverse read suffix [default: %(default)s]", default="_R2")
    args.add_argument("--verbose", help="Verbose output", action="store_true")
    args.add_argument("--run", help="Run the pipeline", action="store_true")
    args.add_argument("--wait", help="Wait for pipeline execution end (not recommended)", action="store_true")
    
    args = args.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    logger = logging.getLogger("Phanta")
    
    # Check dependencies
    if not check_dep(["snakemake", "--version"]):
        logger.error("ARE YOU IN THE PHANTA ENVIRONMENT? Snakemake not found.")
        sys.exit(1)

    # Workin directory
    tmpdir = None
    
    if args.work_dir is not None:
        try:
            logger.info("Attempting to set workdir: %s" % args.work_dir)
            tmpdir = os.path.abspath(args.work_dir)
            os.makedirs(tmpdir, exist_ok=True)
        except Exception as e:
            logger.error("Unable to create workdir: %s\nERROR: %s" % (args.work_dir, e))
            quit(1)
    else:
        tmpdir = tempfile.mkdtemp()
    
    logger.info("TMPDIR: Temporary directory set to: %s" % tmpdir)
        
    if args.input_dir is not None:
        logger.info("SOURCE: Input directory: %s" % args.input_dir)
        input_dir = os.path.abspath(args.input_dir)
        mapping_file = os.path.join(tmpdir, "mapping.txt")
        # Make mapping file
        found = make_mapping(input_dir, mapping_file, args.fwd, args.rev)

    elif args.sample_sheet is not None:
        logger.info("SOURCE: Sample sheet: %s" % args.sample_sheet)
        # Read mapping file: count lines of args.sample_sheet
        with open(args.sample_sheet) as fh:
            found = sum(1 for line in fh)
        mapping_file = os.path.abspath(args.sample_sheet)
    else:
        logger.error("No input directory or sample sheet provided")
        sys.exit(1)

    if args.phanta_dir is None:
        logger.error("Phanta directory not found, try setting $PHANTA_DIR or pass -p DIR")
        sys.exit(1)

    if args.db_dir is None:
        logger.error("Phanta database directory not found, try setting $PHANTA_DB or pass -d DIR")
        sys.exit(1)

    yaml_file    = os.path.join(tmpdir, "config.yaml")
    phanta_dir = os.path.abspath(args.phanta_dir)
    db_dir = os.path.abspath(args.db_dir)
    template_config = os.path.join(phanta_dir, "testing", "config_test.yaml")
    
    
    output_dir = os.path.abspath(args.output_dir)
    snakefile = os.path.join(phanta_dir, "Snakefile")
    
    # Check dirs
    if not os.path.isdir(phanta_dir):
        logger.error("Phanta directory %s not found" % phanta_dir)
        sys.exit(1)
    if not os.path.isdir(db_dir):
        logger.error("Database directory %s not found" % db_dir)
        sys.exit(1)
    if not os.path.isfile(os.path.join(db_dir, "hash.k2d")):
        logger.error("Database not found in %s" % db_dir)
        sys.exit(1)

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    logger.info("Outdir: %s" % output_dir)
    
    
    if found == 0:
        logger.error("No samples found with tags %s or %s" % (args.fwd, args.rev))
        sys.exit(1)
    logger.info("Creating mapping file %s" % mapping_file)

    # Make config file
    # load yaml from template_config
    with open(template_config, 'r') as file:
        config_base = yaml.safe_load(file)
    
    try:
        config_base["pipeline_directory"] = phanta_dir
        config_base["sample_file"] = mapping_file
        config_base["outdir"] = output_dir
        config_base["cov_thresh_bacterial"] = args.bac_cov
        config_base["cov_thresh_viral"] = args.vir_cov
        config_base["cov_thresh_arc"] = args.arc_cov
        config_base["cov_thresh_euk"] = args.euk_cov
        config_base["confidence_threshold"] = args.confidence
        config_base["filter_thresh"] = args.bracken_filter
        config_base["gzipped"] = args.nongzipped
        config_base["delete_intermediate"] = args.keepintermediate
        config_base["read_length"] = args.read_length
        config_base["database"] = db_dir
        
    except Exception as e:
        logger.error("Error while setting up config file: %s" % e)
        sys.exit(1)
    
    # Save config_base as yaml_file
    with open(yaml_file, 'w') as file:
        documents = yaml.dump(config_base, file)
    run_cmd = ["snakemake", "-s", snakefile, 
        "--configfile", yaml_file,
        "--jobs", "99", "--cores", str(args.cores), "--max-threads", str(args.threads)]

    # Cmd String: join run_cmd with spaces and convert each element to string
    cmd_str = " ".join([str(x) for x in run_cmd])
    logger.info("Running Phanta with command: %s" % cmd_str)
    # Execute run_cmd
    if args.run:
        
        if not args.wait:
            # Default running mode: give PID to child
            os.execlp("snakemake", *run_cmd)
            # Quitting...
            
        # If --wait is specified
        try:
            phanta = subprocess.run(run_cmd, capture_output=True)
            if phanta.returncode != 0:
                logger.error("Phanta returned an error")
                logger.error(phanta.stderr.decode("utf-8"))
                sys.exit(1)
            else:
                logger.info("Phanta finished successfully")
                logger.info(phanta.stdout.decode("utf-8"))
        except Exception as e:
            logger.error("Error while running Phanta: %s" % e)
            # Try removing lock file
            snakemake_dir = os.path.join(output_dir, ".snakemake")
            if os.path.isdir(snakemake_dir):
                logger.info("Moving snakemake directory %s to %s.old" % snakemake_dir)
                if os.path.isdir(f"{snakemake_dir}.old"):
                    logger.info("Removing previous snakemake backup %s.old" % snakemake_dir)
                    shutil.rmtree(f"{snakemake_dir}.old", ignore_errors=True)
                shutil.move(snakemake_dir, f"{snakemake_dir}.old")

            sys.exit(1)
    else:
        print("Run the following command:", file=sys.stderr)
        print(cmd_str)

#!/bin/bash

snakemake -s /labs/asbhatt/mchakra/phaging/phage_abundance_pipeline/Snakefile \
--configfile /labs/asbhatt/mchakra/phaging/phage_abundance_pipeline/testing/config_test.yaml \
--jobs 999 --reason --profile scg

#!/bin/bash

snakemake -s /labs/asbhatt/mchakra/phaging/phage_abundance/Snakefile \
--configfile /labs/asbhatt/mchakra/phaging/phage_abundance/testing/config_test.yaml \
--jobs 999 --reason --profile scg

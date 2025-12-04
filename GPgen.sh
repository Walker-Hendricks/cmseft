#!/bin/bash

# Defining storing locations
outdir="$(pwd)/gridpacks"
mkdir $outdir
mkdir $outdir/$spew
mkdir $outdir/$spew/outfiles
mkdir $outdir/$spew/errfiles

# Declaring Wilson coefficient array
declare -A WC_ARR
# Define your w.c.s here and their values (comma-delimited)
WC_ARR["cbWRe"]="7,-7"
WC_ARR["cHQ3"]="7,-7"
WC_ARR["cHQ1"]="16,-12"
WC_ARR["cHt"]="15,-20"
WC_ARR["cHtbRe"]="15,-15"
WC_ARR["ctWRe"]="2,-2"
WC_ARR["ctBRe"]="2,-2"
WC_ARR["ctHRe"]="40,-10"

# Submitting all WC combos
for wc in "${!WC_ARR[@]}"; do
    IFS=',' read -r -a VALS_ARR <<< "${WC_ARR[$wc]}"
    for val in "${VALS_ARR[@]}"; do
	echo "Submitting gridpack generation for ${wc}=${val}..."
	qsub -N "${wc}_${val}_ttZ" -v "WC=$wc,WC_VAL=$val,outdir=$outdir" \
		-o $outdir/$spew/outfiles/ \
		-e $outdir/$spew/errfiles/ \
	      	testGP.pbs
	printf '%.0s-' {1..20}
    done
done

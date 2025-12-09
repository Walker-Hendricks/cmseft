#!/bin/bash

# Defining storing locations
outdir="$(pwd)/gridpacks"
mkdir -p $outdir
mkdir -p $outdir/spew
mkdir -p $outdir/spew/outfiles
mkdir -p $outdir/spew/errfiles

# Declaring WC array
declare -A WC_ARR
# Define your w.c.s here and their values (comma-delimited)
#WC_ARR["cbWRe"]="7,-7"
#WC_ARR["cHQ3"]="7,-7"
#WC_ARR["cHQ1"]="16,-12"
#WC_ARR["cHt"]="15,-20"
#WC_ARR["cHtbRe"]="15,-15"
#WC_ARR["ctWRe"]="2,-2"
#WC_ARR["ctBRe"]="2,-2"
#WC_ARR["ctHRe"]="40,-10"

# Multi-valued edits
WC_ARR["ctBRe/ctWRe"]="2,-2;-2,2"	# Two WC edits simultaneously: ctB=2, ctW=-2; ctB=-2, ctW=2

# Submitting all WC combos
for wc in "${!WC_ARR[@]}"; do
    # Check if multi-WC entry (contains '/')
    if [[ "$wc" == *"/"* ]]; then
        # Multi-WC: split wcs by semicolon ';'
        IFS=';' read -r -a VALS_ARR <<< "${WC_ARR[$wc]}"
    else
        # Single-WC: split values by comma ','
        IFS=',' read -r -a VALS_ARR <<< "${WC_ARR[$wc]}"
    fi
    for val in "${VALS_ARR[@]}"; do
        # Sanitize strings for job name (replace '/' and ',' with '_')
        job_wc_name=${wc//\//_}  
        job_val_name=${val//,/_}
	
	# Replace ',' with ':' so qsub doesn't break
        pass_val=${val//,/:}

        echo "Submitting gridpack generation for ${wc}=${val}..."
        qsub -N "${job_wc_name}_${job_val_name}_ttZ" \
             -v "WC=$wc,WC_VAL=$pass_val,outdir=$outdir" \
             -o $outdir/spew/outfiles/ \
             -e $outdir/spew/errfiles/ \
             GPgen.pbs
             
        printf '%.0s-' {1..20}
        echo "" 
    done
done

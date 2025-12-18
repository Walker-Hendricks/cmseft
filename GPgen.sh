#!/bin/bash

# Writing help docs
show_help() {
cat << EOF
Usage: ${0##*/} [-b DIRECTORY] [-e DIRECTORY] [-o DIRECTORY] [-a FILE]
Takes a set of directories with an optional Wilson coefficient array and
generates fixed-sample gridpacks for the specific combinations of W.C.s

    -b          The base/home directory where the gridpack generation script
		is (usually cmseft/generation/genproductions/bin/MadGra-
		ph5_aMCatNLO)
    -d  	The default directory containing the default datacard, process
		card, etc. (usually \$BASEDIR/addons/models/SMEFTsim_topU3l
		_MwScheme_UFO)
    -o          The final output directory (where all of the gridpacks will go;
		suggestion is cmseft/gridpacks)
    -a		(Optional) A file containing the array of Wilson coefficients 
		you want to edit. Must be a .csv or .xlsx
EOF
}

# Argument parser
while getopts "b:e:o:a:" opt; do
	case $opt in
		b)
			BASEDIR=$OPTARG
			;;
		d)
			DEFAULTDIR=$OPTARG
			;;
		o)
			OUTDIR=$OPTARG
			;;
		a)
			# Generates WC_ARR from input file
			eval $(python wcarrparser.py  --file=$OPTARG)
			;;
		\?) 
			echo "Invalid option: -$OPTARG" >&2
			exit 1
			;;
	esac
done


# Validating necessary inputs
if [[ -z $BASEDIR ]]; then
	echo "Error: no -b argument passed."
	show_help
	exit 1
fi

if [[ -z $DEFAULTDIR ]]; then
	echo "Error: no -d argument passed."
	show_help
	exit 1
fi

if [[ -z $OUTDIR ]]; then
	echo "Error: no -o argument passed."
	show_help
	exit 1
fi

if [[ ! -v WC_ARR ]]; then	# If the WC_ARR does not exist...
	declare -A WC_ARR	# Declaring array
fi

if [[ ${#WC_ARR[@]} -eq 0 ]]; then 	# If WC_ARR is empty... (manual fallback)
	# Define your w.c.s here and their values (comma-delimited)
	WC_ARR["cbWRe"]="7,-7"
	WC_ARR["cHQ3"]="7,-7"
	WC_ARR["cHQ1"]="16,-12"
	WC_ARR["cHt"]="15,-20"
	WC_ARR["cHtbRe"]="15,-15"
	WC_ARR["ctWRe"]="2,-2"
	WC_ARR["ctBRe"]="2,-2"
	WC_ARR["ctHRe"]="40,-10"

	# Multi-valued edits
	#WC_ARR["ctBRe/ctWRe"]="2,-2;-2,2"	# Two WC edits simultaneously: ctB=2, ctW=-2; ctB=-2, ctW=2
fi

# Defining storing locations
mkdir -p $OUTDIR
mkdir -p $OUTDIR/spew
mkdir -p $OUTDIR/spew/outfiles
mkdir -p $OUTDIR/spew/errfiles


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
	
	# Replace comma with colon ':' so qsub doesn't break
        pass_val=${val//,/:}

        echo "Submitting gridpack generation for ${wc}=${val}..."
        qsub -N "${job_wc_name}_${job_val_name}_ttZ" \
             -v "WC=$wc,WC_VAL=$pass_val,BASEDIR=$BASEDIR,DEFAULTDIR=$DEFAULTDIR,OUTDIR=$OUTDIR" \
             -o $OUTDIR/spew/outfiles/ \
             -e $OUTDIR/spew/errfiles/ \
             GPgen.pbs
             
        printf '%.0s-' {1..20}
        echo "" 
    done
done

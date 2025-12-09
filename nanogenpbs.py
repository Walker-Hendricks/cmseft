import os
import sys
from argparse import ArgumentParser
from array import array
import random

"""
example:
python nanogenpbs.py --tag=test --gridpack=/cms/data/jsamudio/cmseft/generation/genproductions/bin/MadGraph5_aMCatNLO/TT_madjax_5_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz  --dir=./ --neventstotal=1000 --neventsperjob=500
"""

parser = ArgumentParser()
parser.add_argument('--tag', default="LHE_production_pbs",help='A specific tag name to create log files etc.')
parser.add_argument('--gridpack', default=os.getcwd()+"/test_tarball.tar.xz",help='input tarball from the gridpack production')
parser.add_argument('--dir', default=os.getcwd(),help='master directory for all output with enough space for the LHE files and with write priviledges (example: EOS)')
# Only add two of the following three!
parser.add_argument('--neventstotal', type=int, default=None,help='total number of simulated LHE events')
parser.add_argument('--neventsperjob', type=int, default=None,help='number of events per pbs job')
parser.add_argument('--njobs', type=int, default=None, help='number of pbs jobs')

args = parser.parse_args()


# Create master directory
if args.dir:                                                # Check to see if a directory was passed
    directory = os.path.abspath(args.dir)
    if not os.path.isdir(directory):
        os.mkdir(directory)
        if not os.path.isdir(directory):
            print("Creating directory failed (do you have proper acces rights?)")
            print("Exiting...")
            sys.exit(1)
else:
    parser.error("No master directory passed!\nUse '--dir directory' to specify.\n"
                "Exiting...")


# Create output directory (-ies)
output_dir = os.path.join(directory, "output")
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
# Making directory for standard output
spewdir = os.path.join(directory, 'spew')
if not os.path.isdir(spewdir):
    os.mkdir(spewdir)


# Finding other important directories
gpdir = os.path.abspath(os.path.dirname(args.gridpack))
genmatchdir = os.getcwd()       # Presumably, the file nanogen_matching.py is in the same directory as this file

targetdir = 'cmseft'                            # Directory we want to find
path_components = gpdir.split(os.sep)           # Splitting path by '/' character
if targetdir in path_components:            # Checking gridpack absolute path for 'cmseft'
    index = path_components.index(targetdir)    # Finding index of 'cmseft' directory
    keep = path_components[:index+1]            # Part of path we want to keep
    cmseftdir = os.path.join(*keep)             # Recreating the absolute path of 'cmseft'
elif targetdir in directory.split(os.sep):  # Checking master directory absolute path for 'cmseft'
    path = directory.split(os.sep)
    index = path.index(targetdir)
    keep = path[:index+1]
    cmseftdir = os.path.join(*keep)
elif targetdir in os.getcwd().split(os.sep):# Checking current directory's path for 'cmseft'
    path = os.getcwd().split(os.sep)
    index = path.index(targetdir)
    keep = path[:index+1]
    cmseftdir = os.path.join(*keep)
elif targetdir in os.listdir():
    cmseftdir = os.getcwd() + '/cmseft'


# Checking for sufficient information
passed_args = [i for i in [args.neventstotal, args.neventsperjob, args.njobs] if i is not None]
print(passed_args)
if len(passed_args) < 2: # We need at least two of the above to continue!
    passed_arg = (
            f"--neventstotal {args.neventstotal}" if passed_args[0] == 0 else
            f"--neventsperjob {args.neventsperjob}" if passed_args[0] == 1 else
            f"--njobs {args.njobs}"
            )
    parser.error(
            "You must pass 2 of 3:\n--neventstotal\t--neventsperjob\t--njobs\n"
            "You passed:\n"
            f"{passed_arg}\n"
            "Please pass one of the remaining two arguments."
            )

# We really only want two of the three arguments (if you allowed three, what if they're not consistent?)
if len(passed_args) == 3:
    parser.error("Please only pass 2 of 3:\n--neventstotal\t--neventsperjob\t--njobs")


# At this point, we should have two of the three parameters defined above
# Check them to calculate the third quantity (also slightly shortening names)
if args.neventstotal == None:
    neventstotal = args.njobs * args.neventsperjob
    njobs = args.njobs
    neventsperjob = args.neventsperjob
elif args.neventsperjob == None:
    neventstotal = args.neventstotal
    njobs = args.njobs
    neventsperjob = (neventstotal + njobs - 1) // njobs # Using ceiling integer division
else:
    neventstotal = args.neventstotal
    njobs = (args.neventstotal + args.neventsperjob - 1) // args.neventsperjob
    neventsperjob = args.neventsperjob





# Creating production parameter text file
print(f"preparing {njobs} jobs")                
initial_seed = int(random.uniform(1,1000))                  # Initializing seed
remaining_events = neventstotal                             # Initializing remaining events
with open(f"{directory}/params_pbs.txt", 'w') as params:    # Writing text file
    for i in range(njobs):
        seed = initial_seed + 2*i*neventsperjob + int(random.uniform(1,neventsperjob))  # Updating seed
        nevents = neventsperjob
        if remaining_events < neventsperjob:nevents = remaining_events                  # For final iteration
        params.write(f"{i+1} {seed} {nevents}\n")       # Writing the file parameters
        remaining_events -= neventsperjob               # Updating the number of remaining events



# Create the pbs submission file
with open(f"{directory}/submit.pbs",'w') as pbsfile:
    # File header/setup
    pbsfile.write("#!/bin/bash\n")
    pbsfile.write("#PBS -q batch\n")
    pbsfile.write("#PBS -l nodes=1:ppn=1\n")
    pbsfile.write("#PBS -l mem=20gb\n")
    pbsfile.write("#PBS -m ea\n")
    pbsfile.write(f"#PBS -J 1-{njobs}\n")
    pbsfile.write(f"#PBS -N {args.tag.replace(' ', '_')}_job_${{PBS_ARRAY_INDEX}}\n")
    pbsfile.write(f"#PBS -e {spewdir}/job${{PBS_ARRAY_INDEX}}.err\n")
    pbsfile.write(f"#PBS -o {spewdir}/job${{PBS_ARRAY_INDEX}}.out\n")

    # Setup vars
    pbsfile.write(f"MASTER_DIR={directory}\n")
    pbsfile.write(f"OUTPUT_DIR={output_dir}\n")
    pbsfile.write(f"GENMATCH_DIR={genmatchdir}\n")
    pbsfile.write(f"CMSEFT_DIR={cmseftdir}\n")

    # Reading params
    pbsfile.write('PARAM_FILE="${MASTER_DIR}/params_pbs.txt"\n')
    pbsfile.write('PARAMS=$(sed -n "${PBS_ARRAY_INDEX}p" ${PARAM_FILE})\n')
    pbsfile.write('read job_num rnd nevents <<< "$PARAMS"\n')

    # Setup cmssw
    pbsfile.write(f"cd ${{CMSEFT_DIR}}/generation\n")
    pbsfile.write('cmssw-el8\n')
    pbsfile.write(". setup.sh\n")

    # Create scratch area (temporary directory for output when it's all named the same)
    pbsfile.write('SCRATCH_DIR=/tmp/${USER}_job_${PBS_JOBID}_${PBS_ARRAY_INDEX}\n')
    pbsfile.write('mkdir -p ${SCRATCH_DIR}\n')
    pbsfile.write('cd ${SCRATCH_DIR}\n')
    
    # Running (write log file to final destination
    pbsfile.write(f'echo "running: cmsRun ${{GENMATCH_DIR}}/nanogen_matching.py {args.gridpack} ${{nevents}} ${{rnd}}"\n')
    pbsfile.write(f"cmsRun ${{GENMATCH_DIR}}/nanogen_matching.py {args.gridpack} ${{nevents}} ${{rnd}} &> ${{OUTPUT_DIR}}/nanogen_${{PBS_ARRAY_INDEX}}.log\n")
    
    # Moving final files
    pbsfile.write('echo "Moving root file to output directory..."\n')
    pbsfile.write('find . -maxdepth 1 -name "*.root" -exec mv {} ${OUTPUT_DIR}/nanogen_${PBS_ARRAY_INDEX}.root \;\n')

    # Cleanup temp dir
    pbsfile.write('cd ${MASTER_DIR}\n')
    pbsfile.write('rm -rf ${SCRATCH_DIR}\n')


print("You can now submit the job by running 'qsub submit.pbs' in your master directory.")
print("Check the job status by running 'qstat -u [username]'")

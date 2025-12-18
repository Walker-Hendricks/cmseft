import pandas as pd
import os
from argparse import ArgumentParser

def dict_to_aarr(dic):
    """
    Converts a Python dictionary to a Bash associative array.
    """
    bash_line="declare -A WC_ARR=("
    for key, value in dic.items():
        if '/' in key:
            values = ';'.join(value)
        else:
            values = ','.join(value)
        bash_line += f" [{key}]={values}"
    bash_line += " )"
    return bash_line


# Parsing input file
parser=ArgumentParser()
parser.add_argument('--file', help='Input file containg your Wilson coefficients (must be a csv or Excel file).')

wcfile = parer.parse_args().file

# Determining input file type
ext = os.path.splittext(wcfile)[1]

# Parsing from dataframe to list based on file extension
class WrongFileTypeImSadError(Exception):
    """
    Raised when the input file type is not either .csv or .xlsx
    
    Im Sad
    """
    pass

if ext == '.xlsx':
    WC_ARR = pd.read_excel(wcfile).to_dict(orient='list')
elif ext == '.csv':
    WC_ARR = pd.read_csv(wcfile).to_dict(orient='list')
else:
    raise WrongFileTypeImSadError("Your file is not either a .csv or .xlsx file!")


# Sending output to command line
print(dict_to_aarr(WC_ARR))

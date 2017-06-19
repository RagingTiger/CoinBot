"""
Author: John D. Anderson
Email: jander43@vols.utk.edu
Description: Module for managing API tokens.
"""

# libs
import os
import sys


# funcs
def get_toke(tokefile='.tokens', token_names=None):
    # create token dict
    tdict = {}

    # read in file and split
    try:
        with open(tokefile, 'r') as toke_file:
            for line in toke_file:
                key, val = line.split('=')
                tdict[key] = val.strip()
    except IOError:
        if token_names:
            for token in token_names:
                tdict[token] = os.environ.get(token)

    # return dict
    return tdict

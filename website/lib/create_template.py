#!/usr/bin/python3
# encoding: utf-8
'''
 -- Creates xlsx files for logging samples or sampling activities
@author:     Luke Marsden
@contact:    lukem@unis.no

Based on https://github.com/SIOS-Svalbard/darwinsheet/blob/master/scripts/make_xlsx.py
'''

import xlsxwriter
import pandas as pd
import sys
from os.path import os
import json
config_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'config'))

sys.path.append(config_dir)
import fields as fields
#import metadata_fields as metadata_fields
from .pull_cf_standard_names import cf_standard_names_to_dic
from .pull_acdd_conventions import acdd_to_df
from .get_configurations import get_config_fields_dic
import os
from argparse import Namespace
#from website.database.get_data import get_data, get_personnel_list, get_cruise
import numpy as np
from datetime import datetime

def create_template(filepath, template_fields_dict, metadata=None, conversions=True, data=None, metadata_df=None):
    """
    Method for calling from other python programs
    Parameters
    ----------
    filepath: string
        The output file
    template_fields_dict : dictionary
        A dictionary of the fields to include in the template. Divided first by sheet. Includes descriptions, formats and validations
    metadata: string
        Metadata to be written. ACDD, EML or None
        Default: None
    conversions: Boolean
        Should the conversions sheet be written
        Default: True
    data: pandas.core.frame.DataFrame
        Optional parameter. Option to add data from a dataframe to the 'data' sheet.
        Default: False
    metadata_df: pandas.core.frame.DataFrame
        Optional parameter. Option to add metadata from a dataframe to the 'metadata' sheet.
        Default: False
    """
    args = Namespace()
    args.verbose = 0
    args.dir = os.path.dirname(filepath)
    args.filepath = filepath

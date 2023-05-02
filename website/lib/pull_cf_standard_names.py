#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 08:53:13 2022

@author: lukem
"""

import pandas as pd
import json
import sys
from os.path import os
config_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'config'))

sys.path.append(config_dir)
from .check_internet import have_internet

class CF_standard_names_json():
    '''
    Class for pulling CF standard names to a json file
    Only try to pull latest CF standard names if online
    Otherwise pull CF standard name from existing JSON
    So the JSON overwrites each time the script runs if online
    '''

    def __init__(self, path):
        """
        Initialises the json file
        Parameters
        ----------
        filename: string
            The name of the json file to be written
        """
        self.filename = path + '/cf_standard_names.json'


    def pull_from_online(self):
        '''
        Script to harvest the CF standard names from XML on the conventions page to a pandas dataframe
        Includes description and canonical units

        Returns
        -------
        df: pandas dataframe
            Standard names in a dataframe

        '''
        self.df = pd.read_xml('https://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml', xpath="entry")
        self.df = self.df.drop(['grib','amip'], axis=1)

    def create_json(self):
        self.dic1 = self.df.to_dict(orient='records')

        self.dic2 = []
        for cf_standard_name in self.dic1:

            if cf_standard_name['id'] == 'time':
                cf_standard_name['description'] = '''
                To encode time in CF standards, set "time" variable units using UDUNITS syntax (e.g. "days since 1970-01-01"),

                e.g. time = 0,1,2
                for dates 1970-01-01, 1970-01-02, 1970-01-03
                '''

            cf_standard_name['valid'] = {
                'validate': 'decimal',
                'input_title': cf_standard_name['id'],
                'input_message': cf_standard_name['description'],
                'criteria': '>=',
                'value': '-1e100',
                'error_title': 'Error',
                'error_message': 'Values should usually be numbers for CF standard names'
                }
            cf_standard_name['disp_name'] = cf_standard_name['id']
            cf_standard_name['format'] = 'double precision'
            cf_standard_name['grouping'] = 'CF standard name'

            self.dic2.append(cf_standard_name)

        with open(self.filename, 'w', encoding='utf-8') as f:
           json.dump(self.dic2, f, ensure_ascii=False, indent=4)

    def load_json(self):
        f = open(self.filename)
        self.dic = json.load(f)

def cf_standard_names_update(path):
    errors = []
    cf_standard_names_json = CF_standard_names_json(path)
    if not have_internet():
        errors.append('Could not update CF standard names. Not connected to the internet')
        return errors
    try:
        cf_standard_names_json.pull_from_online()
    except:
        errors.append("Could not update CF standard names. Couldn't access data from source URL")
        return errors
    try:
        cf_standard_names_json.create_json()
    except:
        errors.append("Could not update CF standard names. Issue creating JSON file")
        return errors
    return errors

def cf_standard_names_to_dic(path):
    cf_standard_names_json = CF_standard_names_json(path)
    cf_standard_names_json.load_json()
    return cf_standard_names_json.dic

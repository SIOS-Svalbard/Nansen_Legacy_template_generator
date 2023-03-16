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

    def __init__(self, filename):
        """
        Initialises the json file
        Parameters
        ----------
        filename: string
            The name of the json file to be written
        """
        self.filename = filename


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

        self.dic = self.df.to_dict(orient='records')
        # Uncomment when in production
        #with open(self.filename, 'w', encoding='utf-8') as f:
        #    json.dump(self.dic, f, ensure_ascii=False, indent=4)

    def load_json(self):

        f = open(self.filename)
        self.dic = json.load(f)

def cf_standard_names_to_dic():
    cf_standard_names_json = CF_standard_names_json('Learnings_from_AeN_template_generator/config/cf_standard_names.json')
    if have_internet():
        cf_standard_names_json.pull_from_online()
        cf_standard_names_json.create_json()
    else:
        cf_standard_names_json.load_json()

    return cf_standard_names_json.dic

if __name__ == '__main__':
    cf_standard_names_to_dic()

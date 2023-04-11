#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: lukem
"""

import pandas as pd
import sys
from os.path import os
config_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'config'))

sys.path.append(config_dir)
from .check_internet import have_internet

class Darwin_Core_Terms_CSV():
    '''
    Class for pulling Darwin Core terms to a CSV
    Only try to pull latest DwC terms if online
    Otherwise pull DwC term from existing CSV
    So the CSV overwrites each time the script runs if online
    '''

    def __init__(self):
        """
        Initialises the json file
        Parameters
        ----------
        filename: string
            The name of the json file to be written
        """
        self.filename = 'website/config/dwc_terms.csv'


    def pull_from_online(self):
        '''
        Script to harvest the CF standard names from XML on the conventions page to a pandas dataframe
        Includes description and canonical units

        Returns
        -------
        df: pandas dataframe
            Standard names in a dataframe

        '''

        # URL of the CSV file to download
        url = 'https://raw.githubusercontent.com/tdwg/rs.tdwg.org/master/terms/terms.csv'
        self.df = pd.read_csv(url)

        # Remove depricated terms
        self.df = self.df[self.df['term_deprecated'] != True]
        self.df.reset_index(inplace=True, drop=True)


    def save_CSV(self):

        self.df.to_csv(self.filename)


    def load_CSV(self):

        self.df = pd.read_csv(self.filename)

def dwc_terms_to_df():

    dwc_terms_csv = Darwin_Core_Terms_CSV()
    #if have_internet():
    #dwc_terms_csv.pull_from_online()
    #dwc_terms_csv.save_CSV()
    #else:
    dwc_terms_csv.load_CSV()

    return dwc_terms_csv.df

if __name__ == '__main__':
    dwc_terms_to_df()

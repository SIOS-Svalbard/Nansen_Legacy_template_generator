#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 08:53:13 2022

@author: lukem
"""

import pandas as pd
import numpy as np
import sys
from os.path import os
config_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'config'))

sys.path.append(config_dir)
from .check_internet import have_internet

class global_attributes_df():
    '''
    Class for pulling global attributes to a pandas dataframe
    '''

    def __init__(self, path):
        """
        Initialises the json file
        Parameters
        ----------
        filename: string
            The name of the json file to be written
        """
        self.filename = path + '/global_attributes.csv'


    def pull_from_online(self):
        '''
        Script to harvest the global attributes to a pandas dataframe
        Take them from the ADC page

        Returns
        -------
        df: pandas dataframe
            global attributes in a dataframe

        '''
        url = 'https://adc.met.no/node/4'
        tables = pd.read_html(url)
        df1 = tables[0]
        df2 = tables[1]
        self.df = pd.concat([df1, df2], ignore_index=True)
        self.df = self.df.dropna(how='all')
        self.df.reset_index(inplace=True, drop=True)

    def add_recommendations_column(self):
        '''
        '''
        # Add a new column based on the values in the 'Comment' column
        conditions = [
            self.df['Comment'].str.contains('Required', case=False, na=False),
            self.df['Comment'].str.contains('Optional', case=False, na=False),
            self.df['Comment'].str.contains('Recommended', case=False, na=False),
            self.df['Comment'].str.contains('Yes if not hosted by MET', case=False, na=False)
        ]
        choices = ['Required', 'Optional', 'Recommended', 'Required']
        self.df['Requirement'] = np.select([c.values for c in conditions], choices, default='')

    def output_to_csv(self):
        '''
        '''
        self.df.to_csv(self.filename, index=False)

    def read_csv(self):
        '''
        '''
        self.df = pd.read_csv(self.filename, index_col=False)

def global_attributes_update(path):
    errors = []
    global_attributes = global_attributes_df(path)
    if not have_internet():
        errors.append('Could not update global attributes. Not connected to the internet')
        return errors
    try:
        global_attributes.pull_from_online()
    except:
        errors.append("Could not update global attributes. Couldn't access data from source URL")
        return errors
    try:
        global_attributes.add_recommendations_column()
    except:
        errors.append("Could not update global attributes. Error adding recommendations column")
        return errors
    try:
        global_attributes.output_to_csv()
    except:
        errors.append("Could not update global attributes. Couldn't save the CSV file.")
        return errors
    return errors

def global_attributes_to_df(path):
    global_attributes = global_attributes_df(path)
    global_attributes.read_csv()
    return global_attributes.df

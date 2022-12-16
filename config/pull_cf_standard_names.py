#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 08:53:13 2022

@author: lukem
"""

import pandas as pd


def pull_standard_names():
    '''
    Script to harvest the CF standard names from XML on the conventions page to a pandas dataframe
    Includes description and canonical units

    Returns
    -------
    df: pandas dataframe
        Standard names in a dataframe

    '''
    df = pd.read_xml('https://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml', xpath="entry")

    df = df.drop(['grib','amip'], axis=1)
    return df


def group_standard_names(df):
    '''
    Assining standard names to groups based upon a text search
    Based on the javascript behind the grouping on this page, but with my own grouping:
    http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html

    Parameters
    ----------
    df: pandas dataframe
        Standard names in a dataframe

    Returns
    -------
    df: pandas dataframe
        Standard names in a dataframe, grouping added as new columns, True if in that group, False if not

    '''

    # Key = group name
    # Item = list of terms to search for. If standard_name contains any of terms in list, standard_name assigned to that group
    groups = {
        'Sea water': ['sea_water'],
        'Sea ice': ['sea_ice'],
        'Wind': ['wind'],
        'Snow': ['snow']
        }

    groups_list = groups.keys()

    for group, lst in groups.items():
        terms = '('+'|'.join(lst)+')'
        df[group] = df["id"].str.contains(terms, regex=True)

    return df, groups_list

def create_cf_standard_names_json():

    df = pull_standard_names()
    df_grouped, groups_list = group_standard_names(df)
    standard_names_json = df.to_dict(orient='records')

    return standard_names_json, groups_list

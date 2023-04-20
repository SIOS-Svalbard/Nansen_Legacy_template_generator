#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 08:53:13 2022

@author: lukem
"""

import json

class Other_fields_json():
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


    def load_json(self):
        f = open(self.filename)
        self.dic = json.load(f)

PATH = 'website/config/other_fields.json'

def other_fields_to_dic():
    other_fields_json = Other_fields_json(PATH)
    other_fields_json.load_json()
    return other_fields_json.dic

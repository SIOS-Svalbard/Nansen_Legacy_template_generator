#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
import threading

class Darwin_Core_Terms_json():
    '''
    Class for pulling Darwin Core terms to a JSON
    '''

    def __init__(self, path):
        """
        Initialises the json file
        Parameters
        ----------
        filename: string
            The name of the json file to be written
        """
        self.filename = path + '/dwc_terms.json'

    def pull_from_online(self):
        '''
        Script to harvest the CF standard names from XML on the conventions page to a pandas dataframe
        Includes description and canonical units

        Returns
        -------
        df: pandas dataframe
            Standard names in a dataframe

        '''

        url = 'https://raw.githubusercontent.com/tdwg/rs.tdwg.org/master/terms/terms.csv'
        self.df = pd.read_csv(url)

        # Remove depricated terms
        self.df = self.df[self.df['term_deprecated'] != True]
        self.df.reset_index(inplace=True, drop=True)

    def create_json(self):
        self.dic1 = self.df.to_dict(orient='records')

        self.dic2 = []
        for term in self.dic1:

            term['disp_name'] = term['id'] = term['term_localName']
            term['format'] = 'text'
            term['grouping'] = 'Darwin Core term'

            try:
                term['description'] = term['rdfs_comment']
            except:
                term['description'] = ''

            try:
                term['description'] = term['description'] + '\n\n' + term['dcterms_description']
            except:
                pass

            try:
                term['description'] = term['description'] + '\n\nExamples: ' + term['examples']
            except:
                pass

            if term['id'] == 'decimalLatitude':
                term["valid"] = {
                    "validate": "decimal",
                    "criteria": "between",
                    "minimum": -90,
                    "maximum": 90,
                    "input_title": term['id'],
                    "input_message": term['description'],
                    "error_title": "Error",
                    "error_message": "Not in range [-90, 90]"
                }
                term['cell_format'] = {
                    "num_format": "0.0000"
                }
                term['format'] = 'double precision'

            elif term['id'] == 'decimalLongitude':
                term["valid"] = {
                    "validate": "decimal",
                    "criteria": "between",
                    "minimum": -180,
                    "maximum": 180,
                    "input_title": term['id'],
                    "input_message": term['description'],
                    "error_title": "Error",
                    "error_message": "Not in range [-180, 180]"
                }
                term['cell_format'] = {
                    "num_format": "0.0000"
                }
                term['format'] = 'double precision'

            elif term['id'] in ['minimumDepthInMeters', 'maximumDepthInMeters', 'minimumElevationInMeters', 'maximumElevationInMeters', 'minimumDistanceAboveSurfaceInMeters', 'maximumDistanceAboveSurfaceInMeters']:
                term["valid"] = {
                    "validate": "decimal",
                    "criteria": "between",
                    "minimum": 0,
                    "maximum": 99999,
                    "input_title": term['id'],
                    "input_message": term['description'],
                    "error_title": "Error",
                    "error_message": "Enter a number in range [0, 99999]"
                }
                term['format'] = 'double precision'

            else:
                term['valid'] = {
                    'validate': 'any',
                    'input_title': term['term_localName'],
                    'input_message': term['description']
                    }

            self.dic2.append(term)

        with open(self.filename, 'w', encoding='utf-8') as f:
           json.dump(self.dic2, f, ensure_ascii=False, indent=4)


    def load_json(self):
        with open(self.filename, 'r', encoding='utf-8', errors='ignore') as f:
           content = f.read()
           cleaned_content = content.encode('utf-8').decode('utf-8', 'ignore')
           self.dic = json.loads(cleaned_content)

class Darwin_Core_Extension():
    '''
    Class for pulling Darwin Core extension to a JSON
    '''
    def __init__(self, source, filename):
        """
        Initialises the json file
        Parameters
        ----------
        filename: string
            The name of the json file to be written
        """
        self.filename = filename
        self.source = source

    def pull_from_online(self):
        '''
        Script to harvest the CF standard names from XML on the conventions page to a pandas dataframe
        Includes description and canonical units

        Returns
        -------
        df: pandas dataframe
            Standard names in a dataframe

        '''

        self.df = pd.read_xml(self.source)

    def create_json(self):
        self.dic1 = self.df.to_dict(orient='records')
        columns = self.df.columns

        self.dic2 = []
        for term in self.dic1:
            term['disp_name'] = term['id'] = term['name']
            print(term['id'])
            term['grouping'] = 'Darwin Core term'
            term['description'] = ''
            if 'dc:description' in columns:
                term['description'] = str(term['dc:description'])
            if 'comments' in columns:
                term['description'] = term['description'] + '\n\n' + str(term['comments'])
            if 'examples' in columns:
                term['description'] = term['description'] + '\n\nExamples: ' + str(term['examples'])

            if term['id'] == 'decimalLatitude':
                term["valid"] = {
                    "validate": "decimal",
                    "criteria": "between",
                    "minimum": -90,
                    "maximum": 90,
                    "input_title": term['id'],
                    "input_message": term['description'],
                    "error_title": "Error",
                    "error_message": "Not in range [-90, 90]"
                }
                term['cell_format'] = {
                    "num_format": "0.0000"
                }
                term['format'] = 'double precision'

            elif term['id'] == 'decimalLongitude':
                term["valid"] = {
                    "validate": "decimal",
                    "criteria": "between",
                    "minimum": -180,
                    "maximum": 180,
                    "input_title": term['id'],
                    "input_message": term['description'],
                    "error_title": "Error",
                    "error_message": "Not in range [-180, 180]"
                }
                term['cell_format'] = {
                    "num_format": "0.0000"
                }
                term['format'] = 'double precision'

            elif term['id'] in ['minimumDepthInMeters', 'maximumDepthInMeters', 'minimumElevationInMeters', 'maximumElevationInMeters', 'minimumDistanceAboveSurfaceInMeters', 'maximumDistanceAboveSurfaceInMeters']:
                term["valid"] = {
                    "validate": "decimal",
                    "criteria": "between",
                    "minimum": 0,
                    "maximum": 99999,
                    "input_title": term['id'],
                    "input_message": term['description'],
                    "error_title": "Error",
                    "error_message": "Enter a number in range [0, 99999]"
                }
                term['format'] = 'double precision'

            elif 'type' in term:

                if term['type'] == 'integer':
                    term['valid'] = {
                        "validate": "integer",
                        "criteria": ">=",
                        "value": 0,
                        "input_title": term['name'],
                        "input_message": term['description'],
                        "error_title": "Error",
                        "error_message": "Integer >= 0"
                    }
                    term['format'] = 'int'

                elif term['type'] == 'decimal':
                    term['valid'] = {
                        "validate": "integer",
                        "criteria": ">=",
                        "value": "-1e100",
                        "input_title": term['name'],
                        "input_message": term['description'],
                        "error_title": "Error",
                        "error_message": "Must be a number"
                    }
                    term['cell_format'] = {
                        "num_format": "0.0000"
                    }
                    term['format'] = 'double precision'

                else:
                    term['valid'] = {
                        "validate": "any",
                        "input_title": term['name'],
                        "input_message": term['description']
                    }
                    term['format'] = 'text'

            else:
                term['valid'] = {
                    "validate": "any",
                    "input_title": term['name'],
                    "input_message": term['description']
                }
                term['format'] = 'text'

            self.dic2.append(term)

        with open(self.filename, 'w', encoding='utf-8') as f:
           json.dump(self.dic2, f, ensure_ascii=False, indent=4)


    def load_json(self):
        with open(self.filename, 'r', encoding='utf-8', errors='ignore') as f:
           content = f.read()
           cleaned_content = content.encode('utf-8').decode('utf-8', 'ignore')
           self.dic = json.loads(cleaned_content)


extensions = {
    'Event Core': {
        'file': 'dwc_event.json',
        'source': 'https://rs.gbif.org/core/dwc_event_2022-02-02.xml',
        },
    'Occurrence Extension': {
        'file': 'dwc_occurrence.json',
        'source': 'https://rs.gbif.org/core/dwc_occurrence_2022-02-02.xml',
        },
    'Occurrence Core': {
        'file': 'dwc_occurrence.json',
        'source': 'https://rs.gbif.org/core/dwc_occurrence_2022-02-02.xml',
        },
    'Extended MoF Extension': {
        'file': 'dwc_emof.json',
        'source': 'https://rs.gbif.org/extension/obis/extended_measurement_or_fact.xml',
        },
    'Material Sample Extension': {
        'file': 'dwc_materialsample.json',
        'source': 'https://rs.gbif.org/extension/ggbn/materialsample.xml',
        },
    'Resource Relationship Extension': {
        'file': 'dwc_resourcerelationship.json',
        'source': 'https://rs.gbif.org/extension/dwc/resource_relationship_2022-02-02.xml',
        },
    'Simple Multimedia Extension': {
        'file': 'dwc_multimedia.json',
        'source': 'https://rs.gbif.org/extension/gbif/1.0/multimedia.xml',
        }
}

def dwc_terms_update(path):
    errors = []
    dwc_terms_json = Darwin_Core_Terms_json(path)
    if not have_internet():
        errors.append('Could not update Darwin Core terms. Not connected to the internet')
        return errors

    try:
        t = threading.Thread(target=dwc_terms_json.pull_from_online)
        t.start()
        t.join(timeout=5)

        if t.is_alive():
            errors.append("Could not update Darwin Core terms. Couldn't access data from source URL. It took longer than it should.")
            return errors

    except TimeoutError:
        errors.append("Could not update Darwin Core terms. Couldn't access data from source URL")
        return errors

    try:
        dwc_terms_json.create_json()
    except:
        errors.append("Could not update Darwin Core terms. Issue creating JSON file")
        return errors

def dwc_terms_to_dic(path):
    dwc_terms_json = Darwin_Core_Terms_json(path)
    dwc_terms_json.load_json()
    return dwc_terms_json.dic

def dwc_extensions_update(path):
    for extension, vals in extensions.items():
        dwc_extension = Darwin_Core_Extension(vals['source'], path + '/' + vals['filename'])
        dwc_extension.pull_from_online()
        dwc_extension.create_json()

def dwc_extension_to_dic(path, extension):
    filepath = path + '/' + extensions[extension]['file']
    dwc_extension = Darwin_Core_Extension(extension, filepath)
    dwc_extension.load_json()
    return dwc_extension.dic

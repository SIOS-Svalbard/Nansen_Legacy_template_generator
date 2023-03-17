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

DEBUG = 1

DEFAULT_FONT = 'Calibri'
DEFAULT_SIZE = 10

def add_line_breaks(text, n):
    """Add line breaks to a long string every n characters or fewer if n characters falls within a word."""
    lines = []
    while len(text) > n:
        # Find the last space within the limit
        space_index = text.rfind(' ', 0, n+1)
        if space_index == -1:
            # No space found, just break at the limit
            space_index = n
        lines.append(text[:space_index].strip())
        text = text[space_index:].strip()
    lines.append(text)
    return '\n'.join(lines)

def split_personnel_df(df, col):
    '''
    Use to split personnel columns (pi_details, recordedBy_details) into separate columns
    Number of columns based on maximum number of personnel logged

    Parameters
    ----------
    df : pandas dataframe
        Pandas Dataframe of metadata including personnel column
    col : string
        Name of personnel column to split

    Returns
    -------
    df : pandas dataframe
        Pandas Dataframe of metadata including personnel column
    max_n_people : int
        Maximum number of people

    '''
    # Find maximum number of personnel
    max_n_people = 1
    for idx, row in df.iterrows():
        n_people = len(row[col].split(' | '))
        if n_people > max_n_people:
            max_n_people = n_people

    # If all cells are empty, i.e. if there are no personnel logged
    # Then printing 3 blank columns
    if df[col].replace(r'^\s*$', np.nan, regex=True).isna().all():
        max_n_people = 3

    # Create a column for each personnel
    for n in range(max_n_people):
        df[col+str(n)] = ''

    # Divide personnel into separate columns
    for idx, row in df.iterrows():
        pis = row[col].split(' | ')
        for n, pi in enumerate(pis):
            df[col+str(n)][idx] = pi

    return df, max_n_people

class Variable_sheet(object):
    """
    Class for handling the variable sheet
    """

    def __init__(self, workbook):
        """
        Initialises the sheet
        Parameters
        ----------
        workbook: Xlsxwriter workbook
            The parent workbook where the sheet is added
        """
        self.workbook = workbook
        self.name = 'Variables'  # The name of the worksheet
        self.sheet = workbook.add_worksheet(self.name)
        # For holding the current row to add variables on
        self.current_column = 0
        self.sheet.hide()  # Hide the sheet

    def add_row(self, variable, parameter_list):
        """
        Adds a row of parameters to a variable and returns the ref for the list
        Parameters
        ----------
        variable : str
            The name of the variable
        parameter_list :
            List of parameters to be added
        Returns
        ----------
        ref : str
            The range of the list in Excel format
        """

        self.sheet.write(0, self.current_column, variable)
        name = 'Table_' + variable.replace(' ', '_').capitalize()

        self.sheet.add_table(
            1, self.current_column,
            1 + len(parameter_list), self.current_column,
            {'name': name,
                'header_row': 0}
        )

        for ii, par in enumerate(sorted(parameter_list, key=str.lower)):
            self.sheet.write(1 + ii, self.current_column, par)
        ref = '=INDIRECT("' + name + '")'

        # Increment row such that the next gets a new row
        self.current_column = self.current_column + 1
        return ref

def derive_content(mfield, data=False, DB=None):
    '''
    Derives values for the metadata sheet
    based on dataframe for data sheet or cruise details table

    Parameters
    ----------
    mfield: dictionary
        Dictionary of the field
    DB: string
        Name of the database where the metadata catalogue is hosted
        Default: None, for when template generator used independent of the database
    data: pandas dataframe
        Pandas dataframe of data to be written in data sheet
        Default: False, for when template generated without data

    Returns
    ----------
    Content of the field to be printed on the metadata sheet upon creation
    '''

    if 'derive_from' in mfield.keys() and type(data) == pd.core.frame.DataFrame and 'derive_from_table' not in mfield.keys() and 'derive_by' in mfield.keys():
        if mfield['name'] == 'geospatial_vertical_min':
            if 'minimumDepthInMeters' in data.columns and 'minimumElevationInMeters' in data.columns:
                content = ''
            elif 'minimumDepthInMeters' in data.columns:
                data['minimumDepthInMeters'].replace('',np.nan,inplace=True)
                content = np.nanmin(data['minimumDepthInMeters'])
            elif 'minimumElevationInMeters' in data.columns:
                data['minimumElevationInMeters'].replace('',np.nan,inplace=True)
                content = np.nanmin(data['minimumElevationInMeters'])
            else:
                content = ''
        elif mfield['name'] == 'geospatial_vertical_max':
            if 'maximumDepthInMeters' in data.columns and 'maximumElevationInMeters' in data.columns:
                content = ''
            elif 'maximumDepthInMeters' in data.columns:
                data['maximumDepthInMeters'].replace('',np.nan,inplace=True)
                content = np.nanmax(data['maximumDepthInMeters'])
            elif 'maxnimumElevationInMeters' in data.columns:
                data['maximumElevationInMeters'].replace('',np.nan,inplace=True)
                content = np.nanmax(data['maximumElevationInMeters'])
            else:
                content = ''

        elif mfield['name'] == 'time_coverage_start':
            data['eventDateTime'] = data['eventDate'].astype(str)+'T'+data['eventTime'].astype(str)+'Z'
            data['eventDateTime'].replace('TZ','9999',inplace=True)
            content = str(np.nanmin(data['eventDateTime']))
        elif mfield['name'] == 'time_coverage_end':
            data['eventDateTime'] = data['eventDate'].astype(str)+'T'+data['eventTime'].astype(str)+'Z'
            data['endDateTime'] = data['endDate'].astype(str)+'T'+data['endTime'].astype(str)+'Z'
            data['eventDateTime'].replace('TZ','0000',inplace=True)
            data['endDateTime'].replace('TZ','0000',inplace=True)
            content = str(np.nanmax(data[['eventDateTime','endDateTime']]))

        elif mfield['derive_by'] == 'min':
            data[mfield['derive_from']].replace('',np.nan,inplace=True)
            content = np.nanmin(data[mfield['derive_from']])
        elif mfield['derive_by'] == 'max':
            data[mfield['derive_from']].replace('',np.nan,inplace=True)
            content = np.nanmax(data[mfield['derive_from']])
        elif mfield['derive_by'] == 'up/down':
            if 'maximumDepthInMeters' in data.columns and 'maximumElevationInMeters' in data.columns:
                content = ''
            elif 'maximumDepthInMeters' in data.columns:
                content = 'down'
            elif 'maximumElevationInMeters' in data.columns:
                content = 'up'
            else:
                content = ''
        elif mfield['derive_by'] == 'concat':
            if type(mfield['derive_from']) == list:
                lst = []
                for ii in mfield['derive_from']:
                    lst = lst + list(data[ii])

                unique_lst = list(set(lst)) # Only need unique values

                for ii in unique_lst:
                    if ' | ' in ii:
                        # Splitting cells with multiple values separated by pipe, appending to list, removing original
                        unique_lst = unique_lst + ii.split(' | ')
                        unique_lst.remove(ii)

                unique_lst = list(set(unique_lst)) # Checking still unique after splitting

                content = ' | '.join(unique_lst)
            else:
                if mfield['name'] in ['instrument', 'instrument_vocabulary']:
                    gears = list(set(data[mfield['derive_from']]))
                    gears_df = get_data(DB, 'gear_types')

                    if mfield['name'] == 'instrument':
                        instruments = []
                        for gear in gears:
                            vocabLabel = gears_df.loc[gears_df['geartype'] == gear, 'vocablabel'].item()
                            if vocabLabel == '':
                                instruments.append(gear)
                            else:
                                instruments.append(vocabLabel)
                        content = ' | '.join(instruments)


                    elif mfield['name'] == 'instrument_vocabulary':
                        instrument_vocabs = []
                        for gear in gears:
                            vocabURI = gears_df.loc[gears_df['geartype'] == gear, 'vocaburi'].item()
                            instrument_vocabs.append(vocabURI)
                        content = ' | '.join(instrument_vocabs)

                else:
                    content = ' | '.join(list(set(data[mfield['derive_from']])))

    elif not DB:
        content = ''

    elif 'derive_from_table' in mfield.keys():
        if mfield['derive_from_table'] == 'cruise_details':
            df = get_cruise(DB)
            try:
                content = df[mfield['name']][0]
            except:
                content = ''
        else:
            content = ''

    else:
        content = ''

    return content

def write_conversion(args, workbook):
    """
    Adds a conversion sheet to workbook
    Parameters
    ----------
    args : argparse object
        The input arguments
    workbook : xlsxwriter Workbook
        The workbook for the conversion sheet
    """

    sheet = workbook.add_worksheet('Conversion')

    parameter_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'right': True,
        'bottom': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'left',
        'font_size': DEFAULT_SIZE + 2,
        'bg_color': '#B9F6F5',
    })
    center_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'right': True,
        'bottom': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'center',
        'font_size': DEFAULT_SIZE + 2,
        'bg_color': '#23EEFF',
    })
    output_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'right': True,
        'bottom': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'left',
        'font_size': DEFAULT_SIZE + 2,
        'bg_color': '#FF94E8',
    })

    sheet.set_column(0, 2, width=30)

    sheet.write(1, 0, "Coordinate conversion ", parameter_format)
    sheet.merge_range(2, 0, 2, 1, "Degree Minutes Seconds ", center_format)
    sheet.write(3, 0, "Degrees ", parameter_format)
    sheet.write(4, 0, "Minutes ", parameter_format)
    sheet.write(5, 0, "Seconds ", parameter_format)
    sheet.write(6, 0, "Decimal degrees ", output_format)
    sheet.write(6, 1, "=B4+B5/60+B6/3600 ", output_format)
    sheet.merge_range(7, 0, 7, 1, "Degree decimal minutes", center_format)
    sheet.write(8, 0, "Degrees ", parameter_format)
    sheet.write(9, 0, "Decimal minutes ", parameter_format)
    sheet.write(10, 0, "Decimal degrees ", output_format)
    sheet.write(10, 1, "=B9+B10/60 ", output_format)

def write_readme(args, workbook, config=None):
    """
    Adds a README sheet to workbook
    Parameters
    ----------
    args : argparse object
        The input arguments
    workbook : xlsxwriter Workbook
        The workbook for the README sheet
    configuration: string
        Name of configuration
        Default: None
    """

    sheet = workbook.add_worksheet('README')

    sheet.set_column(0, 0, width=150)

    readme_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'font_size': 12,
        'bg_color': '#ffffff',
    })

    if config == 'CF-NetCDF':
        readme_file = 'website/config/cfnetcdf_readme.txt'
    elif config == 'Learnings from Nansen Legacy logging system':
        readme_file = 'website/config/lfnl_readme.txt'
    elif config == 'Darwin Core':
        readme_file = 'website/config/dwc_readme.txt'

    with open(readme_file, 'r') as file:
        for idx, line in enumerate(file):

            line = line.replace('\n','')

            sheet.write(idx, 0, line, readme_format)
            sheet.set_row(idx, 25)

    sheet.activate()

def write_metadata(args, workbook, variable_sheet_obj, data, metadata_df, DB=None, CRUISE_NUMBER=None, configuration=None):
    """
    Adds a metadata sheet to workbook
    Parameters
    ----------
    args : argparse object
        The input arguments
    workbook : xlsxwriter Workbook
        The workbook for the metadata sheet
    data: pandas.core.frame.DataFrame
        Optional parameter. Option to derive metadata from the data dataframe for the metadata dataframe.
    variable_sheet_obj:
        Sheet that holds the values in drop-down lists
    metadata_df: pandas.core.frame.DataFrame
        Optional parameter. Option to add metadata from an existing dataframe to the 'metadata' sheet.
    DB: string
        Name of the database where the metadata catalogue is hosted
        Default: None, for when template generate used independent of the database
    CRUISE_NUMBER: string
        Cruise number
        Default: None, for when template generate used independent of the database
    configuration: string
        Name of configuration
        If configuration is 'lfnl_logging_system', some of the metadata sheet are populated for the user
    """

    sheet = workbook.add_worksheet('Metadata')

    header_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'font_color': '#FFFFFF',
        'right': True,
        'bottom': 5,
        'bold': True,
        'text_wrap': True,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 2,
        'bg_color': '#4a4a4a',
    })

    content_format = workbook.add_format({
        'bold': False,
        'font_name': DEFAULT_FONT,
        'text_wrap': True,
        'valign': 'vcenter',
        'bg_color': '#e6ffff',
        'bottom': True,
        'right': True,
        'font_size': DEFAULT_SIZE,
        })

    blank_format = workbook.add_format({
        'bold': False,
        'font_name': DEFAULT_FONT,
        'text_wrap': True,
        'valign': 'vcenter',
        'bottom': True,
        'right': True,
        'font_size': DEFAULT_SIZE,
        })

    required_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#F06292'
        })

    recommended_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#F8BBD0'
        })

    optional_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#F5E1E8'
        })

    header_row = 8
    start_row = header_row + 2

    acdd_df = acdd_to_df()
    acdd_df['Content'] = ''
    df_metadata = acdd_df
    last_col = len(df_metadata.columns)-1

    for ii, col in enumerate(df_metadata.columns):
        sheet.write(header_row, ii, col, header_format)
        sheet.write(header_row+1, ii, col, blank_format)
        sheet.set_row(header_row+1, None, None, {'hidden': True})

    for idx, row in df_metadata.iterrows():

        row_num = start_row + idx

        if row['Requirement'] == 'Required':
            cell_format = required_format
        elif row['Requirement'] == 'Recommended':
            cell_format = recommended_format
        else:
            cell_format = optional_format

        for col, val in enumerate(row):

            if col == last_col:
                cell_format = content_format

            sheet.write(row_num, col, val, cell_format)

            if col == last_col:
                valid = {}
                if row['Attribute'] in ['geospatial_lat_max', 'geospatial_lat_min']:
                    valid['validate'] = 'decimal'
                    valid['criteria'] = 'between'
                    valid['minimum'] = -90
                    valid['maximum'] = 90
                    valid['error_title'] = 'Error'
                    valid['error_message'] = 'Not in range [-90, 90]'
                elif row ['Attribute'] in ['geospatial_lon_max', 'geospatial_lon_min']:
                    valid['validate'] = 'decimal'
                    valid['criteria'] = 'between'
                    valid['minimum'] = -180
                    valid['maximum'] = 180
                    valid['error_title'] = 'Error'
                    valid['error_message'] = 'Not in range [-180, 180]'
                elif row['Attribute'] == 'featureType':
                    valid['validate'] = 'list'
                    valid['source'] = ['point','timeSeries','trajectory','profile','timeSeriesProfile','trajectoryProfile']
                    valid['error_title'] = 'Error'
                    valid['error_message'] = 'Not in range [-180, 180]'
                else:
                    valid['validate'] = 'any'

                sheet.data_validation(first_row=row_num,
                                  first_col=col,
                                  last_row=row_num,
                                  last_col=col,
                                  options=valid)

        length = len(row['Description'])

        if row['Attribute'] == 'summary':
            height = 150
        elif length > 0:
            height = int(length/4)
        else:
            height = 15

        sheet.set_row(row_num, height)

    # Hide requirements column.
    sheet.set_column(3, 3, None, None, {'hidden': True})

    # Key
    sheet.merge_range('A2:B2', 'Required term', required_format)
    sheet.merge_range('A3:B3', 'Recommended term', recommended_format)
    sheet.merge_range('A4:B4', 'Optional term', optional_format)
    sheet.merge_range('A6:B6', 'More attributes can be selected from')
    sheet.merge_range('A7:B7', 'https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3')

    sheet.set_column(0, 0, width=20)
    sheet.set_column(1, 1, width=60)
    sheet.set_column(2, 2, width=30)
    sheet.set_column(4, 4, width=60)

    # Freeze the rows at the top
    sheet.freeze_panes(header_row+1, 1)

def make_xlsx(args, fields_list, metadata, conversions, data, metadata_df, DB, CRUISE_NUMBER=None, configuration=None, subconfiguration=None):
    """
    Writes the xlsx file based on the wanted fields
    Parameters
    ----------
    args : argparse object
        The input arguments
    fields_list : list
        A list of the wanted fields
    metadata: Boolean
        Should the metadata sheet be written
    conversions: Boolean
        Should the conversions sheet be written

    data: pandas.core.frame.DataFrame
        Optional parameter. Option to add data from a dataframe to the 'data' sheet.

    metadata_df: pandas.core.frame.DataFrame
        Optional parameter. Option to add metadata from a dataframe to the 'metadata' sheet.
    DB: string
        Name of the database where the metadata catalogue is hosted
        Default: None, for when template generate used independent of the database
    CRUISE_NUMBER: string
        Cruise number
        Default: None, for when template generate used independent of the database
    configuration: string
        Name of configuration
        If configuration is 'lfnl_logging_system', some of the metadata sheet are populated for the user
        Default: None
    subconfiguration: string
        Name of sub-configuration
        If configuration is 'lfnl_logging_system', some of the metadata sheet are populated for the user
        Default: None
    """

    output = args.filepath
    workbook = xlsxwriter.Workbook(output)

    # Set font
    workbook.formats[0].set_font_name(DEFAULT_FONT)
    workbook.formats[0].set_font_size(DEFAULT_SIZE)

    variable_sheet_obj = Variable_sheet(workbook)

    if metadata:
        write_metadata(args, workbook, variable_sheet_obj, data, metadata_df, DB, CRUISE_NUMBER, configuration)

    # Create sheet for data
    data_sheet = workbook.add_worksheet('Data')

    write_readme(args, workbook, configuration)

    required_field_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bottom': True,
        'right': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 1,
        'bg_color': '#B74F6F'
    })

    recommended_field_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bottom': True,
        'right': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 1,
        'bg_color': '#F49E4C'
    })

    optional_field_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bottom': True,
        'right': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 1,
        'bg_color': '#C0DF85'
    })

    cf_field_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bottom': True,
        'right': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 1,
        'bg_color': '#A4BFEB'
    })

    bounds_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bottom': True,
        'right': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 1,
        'bg_color': '#BCE7FD'
    })

    date_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bold': False,
        'text_wrap': False,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE,
        'num_format': 'dd/mm/yy'
        })

    time_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bold': False,
        'text_wrap': False,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE,
        'num_format': 'hh:mm:ss'
        })

    paste_message = "When pasting use 'paste special' / 'paste only' so not to overwrite cell restrictions"

    # Key
    if configuration == 'Learnings from Nansen Legacy logging system':
        title_row = 7  # starting row
        data_sheet.merge_range('A2:D2', 'Required', required_field_format)
        data_sheet.merge_range('A3:D3', 'Recommended', recommended_field_format)
        data_sheet.merge_range('A4:D4', 'Optional', optional_field_format)
        data_sheet.merge_range('A5:D5', 'CF standard name', cf_field_format)
        data_sheet.merge_range('A6:D6', paste_message)
    elif configuration == 'CF-NetCDF':
        title_row = 6
        data_sheet.merge_range('A2:D2', 'CF standard name', cf_field_format)
        data_sheet.merge_range('A3:D3', 'Cell bounds', bounds_format)
        data_sheet.merge_range('A4:D4', 'Other fields', optional_field_format)
        data_sheet.merge_range('A5:D5', paste_message)
    else:
        title_row = 2
        data_sheet.merge_range('A1:D1', paste_message)

    start_row = title_row + 2
    parameter_row = title_row + 1  # Parameter row, hidden
    end_row = 20000  # ending row

    config_dict = get_config_fields_dic(config=configuration, subconfig=subconfiguration)
    list_of_lists = list(config_dict.values())
    config_fields_list = []
    for sublist in list_of_lists:
        config_fields_list.extend(sublist)

    if configuration == 'Learnings from Nansen Legacy logging system':
        required_fields = config_dict['Required']
        recommended_fields = config_dict['Recommended']
    else:
        required_fields = recommended_fields = []

    # Loop over all the variables/columns needed
    ii = 0

    for field in fields.fields:
        if field['name'] in fields_list:

            if field['name'] in ['pi_details','recordedBy_details'] and DB:
                if type(data) == pd.core.frame.DataFrame:
                    data, duplication = split_personnel_df(data, field['name'])
                else:
                    duplication = 3 # 3 copies of these columns
            else:
                duplication = 1 # One copy of all other columns

            while duplication > 0:

                # Write title row
                if field['name'] in required_fields:
                    data_sheet.write(title_row, ii, field['disp_name'], required_field_format)
                elif field['name'] in recommended_fields:
                    data_sheet.write(title_row, ii, field['disp_name'], recommended_field_format)
                else:
                    data_sheet.write(title_row, ii, field['disp_name'], optional_field_format)

                data_sheet.set_row(title_row, height=45)

                # Write row below with parameter name
                if field['name'] in ['pi_details','recordedBy_details']:
                    data_sheet.write(parameter_row, ii, field['name']+ '_' + str(3-duplication))
                else:
                    data_sheet.write(parameter_row, ii, field['name'])

                # Write validation
                if 'valid' in field.keys():

                    if not DB and field['name'] in ['stationName', 'pi_details', 'recordedBy_details']:
                        # These fields require drop-down lists only when onboard during a cruise
                        pass
                    else:

                        if args.verbose > 0:
                            print("Writing validation for", field['name'])

                        # Need to make sure that 'input_message' is not more than 255
                        valid_copy = field['valid'].copy()

                        if len(field['description']) > 255:
                            valid_copy['input_message'] = field['description'][:252] + '...'
                        else:
                            valid_copy['input_message'] = field['description']

                        valid_copy['input_message'].replace('\n', '\n\r')

                        if len(field['disp_name']) > 32:
                            valid_copy['input_title'] = field['disp_name'][:32]
                        else:
                            valid_copy['input_title'] = field['disp_name']

                        if 'long_list' in field.keys():

                            # Add the validation variable to the hidden sheet
                            table = valid_copy['source']
                            if not DB:
                                df = pd.read_csv(f'website/config/{table}.csv')
                            else:
                                try:
                                    df = get_data(DB, table)
                                except:
                                    df = get_data(DB, table+'_'+CRUISE_NUMBER)

                            if field['name'] in ['pi_details', 'recordedBy_details']:
                                lst_values = get_personnel_list(DB=DB, CRUISE_NUMBER=CRUISE_NUMBER, table='personnel')

                            else:
                                lst_values = list(df[field['name'].lower()])

                            if lst_values:
                                ref = variable_sheet_obj.add_row(
                                    field['name']+str(duplication), lst_values)

                                valid_copy.pop('source', None)
                                valid_copy['value'] = ref



                            data_sheet.data_validation(first_row=start_row,
                                                       first_col=ii,
                                                       last_row=end_row,
                                                       last_col=ii,
                                                       options=valid_copy)

                        else: # if 'long_list' not in field.keys()

                            data_sheet.data_validation(first_row=start_row,
                                                       first_col=ii,
                                                       last_row=end_row,
                                                       last_col=ii,
                                                       options=valid_copy)

                if 'cell_format' in field.keys():
                    if 'font_name' not in field['cell_format']:
                        field['cell_format']['font_name'] = DEFAULT_FONT
                    if 'font_size' not in field['cell_format']:
                        field['cell_format']['font_size'] = DEFAULT_SIZE
                    cell_format = workbook.add_format(field['cell_format'])
                    data_sheet.set_column(
                        ii, ii, width=20, cell_format=cell_format)
                else:
                    data_sheet.set_column(first_col=ii, last_col=ii, width=20)

                ii = ii + 1
                duplication = duplication - 1

    cf_standard_names = cf_standard_names_to_dic()

    for cf_standard_name in cf_standard_names:
        if cf_standard_name['id'] in config_fields_list and cf_standard_name['id'] in fields_list:

            # Write title row
            data_sheet.write(title_row, ii, cf_standard_name['id'], cf_field_format)

            # Write row below with parameter name
            data_sheet.write(parameter_row, ii, cf_standard_name['id'])

            valid = {
                'validate': 'decimal',
                'input_title': cf_standard_name['id'],
                'criteria': '>=',
                'value': '-1e100'
                }

            if cf_standard_name['description'] == None:
                cf_standard_name['description'] = ''

            if len(cf_standard_name['description']) > 230:
                valid['input_message'] = f"{cf_standard_name['description'][:227]}... \ncanonical units: {cf_standard_name['canonical_units']}"
            else:
                valid['input_message'] = f"{cf_standard_name['description']} \ncanonical units: {cf_standard_name['canonical_units']}"

            valid['input_message'] = add_line_breaks(valid['input_message'], 35)

            if len(cf_standard_name['id']) > 32:
                valid['input_title'] = cf_standard_name['id'][:29] + '...'
            else:
                valid['input_title'] = cf_standard_name['id']

            valid['input_message'].replace('\n', '\n\r')

            data_sheet.data_validation(first_row=start_row,
                                       first_col=ii,
                                       last_row=end_row,
                                       last_col=ii,
                                       options=valid)

            data_sheet.set_column(first_col=ii, last_col=ii, width=20)

            ii = ii + 1

    # BOUNDS
    for field in fields_list:

        if 'bounds' in field:

            duplication = 2 # 2 copies of these columns, one for the minimum bound and one for the maximum
            while duplication > 0:

                field = field.replace('_bounds','')
                if duplication == 2:
                    name = 'Minimum ' + field
                elif duplication == 1:
                    name = 'Maximum ' + field

                # Write title row
                data_sheet.write(title_row, ii, name, bounds_format)

                # Write row below with parameter name
                data_sheet.write(parameter_row, ii, name.replace(' ','_'))

                valid = {
                    'validate': 'decimal',
                    'input_title': name,
                    'criteria': '>=',
                    'value': '-1e100'
                    }

                valid['input_message'] = add_line_breaks('For use when a data point does not represent a single point in space or time, but a cell of finite size. Use this variable to encode the extent of the cell (e.g. the minimum and maximum depth that a data point is representative of).', 35)

                valid['input_message'].replace('\n', '\n\r')

                data_sheet.data_validation(first_row=start_row,
                                           first_col=ii,
                                           last_row=end_row,
                                           last_col=ii,
                                           options=valid)

                data_sheet.set_column(first_col=ii, last_col=ii, width=20)

                ii = ii + 1
                duplication = duplication - 1

    for cf_standard_name in cf_standard_names:
        if cf_standard_name['id'] in fields_list and cf_standard_name['id'] not in config_fields_list:

            # Write title row
            data_sheet.write(title_row, ii, cf_standard_name['id'], cf_field_format)

            # Write row below with parameter name
            data_sheet.write(parameter_row, ii, cf_standard_name['id'])

            valid = {
                'validate': 'decimal',
                'input_title': cf_standard_name['id'],
                'criteria': '>=',
                'value': '-1e100'
                }

            if cf_standard_name['description'] == None:
                cf_standard_name['description'] = ''

            if len(cf_standard_name['description']) > 230:
                valid['input_message'] = f"{cf_standard_name['description'][:227]}... \ncanonical units: {cf_standard_name['canonical_units']}"
            else:
                valid['input_message'] = f"{cf_standard_name['description']} \ncanonical units: {cf_standard_name['canonical_units']}"

            valid['input_message'] = add_line_breaks(valid['input_message'], 35)

            if len(cf_standard_name['id']) > 32:
                valid['input_title'] = cf_standard_name['id'][:29] + '...'
            else:
                valid['input_title'] = cf_standard_name['id']

            valid['input_message'].replace('\n', '\n\r')

            data_sheet.data_validation(first_row=start_row,
                                       first_col=ii,
                                       last_row=end_row,
                                       last_col=ii,
                                       options=valid)

            data_sheet.set_column(first_col=ii, last_col=ii, width=20)

            ii = ii + 1



    if type(data) == pd.core.frame.DataFrame:
        ii = 0 # loop over columns

        for field in fields.fields:
            if field['name'] in fields_list:
                if field['name'] in ['pi_details','recordedBy_details']:
                    if type(data) == pd.core.frame.DataFrame:
                        data, duplication = split_personnel_df(data, field['name'])
                    else:
                        duplication = 3 # 3 copies of these columns
                else:
                    duplication = 1 # One copy of all other columns

                tot_duplicates = duplication

                while duplication > 0:

                    if field['name'] in data.columns:
                        data[field['name']].fillna('',inplace=True)
                        if field['name'] in ['eventDate', 'start_date', 'end_date']:
                            data_sheet.write_column(start_row,ii,list(data[field['name']]), date_format)
                        elif field['name'] in ['eventTime', 'start_time', 'end_time']:
                            data_sheet.write_column(start_row,ii,list(data[field['name']]), time_format)
                        elif field['name'] in ['pi_details','recordedBy_details']:
                            n = tot_duplicates - duplication
                            data_sheet.write_column(start_row,ii,list(data[field['name']+str(n)]), time_format)
                        else:
                            data_sheet.write_column(start_row,ii,list(data[field['name']]))

                    ii = ii + 1
                    duplication = duplication - 1


    # Add header, done after the other to get correct format
    #data_sheet.write(0, 0, '', header_format)

    # Set height of row
    data_sheet.set_row(0, height=24)

    # Freeze the rows at the top
    data_sheet.freeze_panes(start_row, 0)

    # Hide ID row
    data_sheet.set_row(parameter_row, None, None, {'hidden': True})

    if conversions:
        write_conversion(args, workbook)

    workbook.close()

def write_file(filepath, fields_list, metadata=True, conversions=True, data=None, metadata_df=None, DB=None, CRUISE_NUMBER=None, configuration=None, subconfiguration=None):
    """
    Method for calling from other python programs
    Parameters
    ----------
    filepath: string
        The output file
    fields_list : list
        A list of the wanted fields
    metadata: Boolean
        Should the metadata sheet be written
        Default: True
    conversions: Boolean
        Should the conversions sheet be written
        Default: True
    data: pandas.core.frame.DataFrame
        Optional parameter. Option to add data from a dataframe to the 'data' sheet.
        Default: False
    metadata_df: pandas.core.frame.DataFrame
        Optional parameter. Option to add metadata from a dataframe to the 'metadata' sheet.
        Default: False
    DB: string
        Name of the database where the metadata catalogue is hosted
        Default: False, for when template generate used independent of the database
    CRUISE_NUMBER: string
        Cruise number
        Default: False, for when template generate used independent of the database
    configuration: string
        Name of configuration
        If configuration is 'lfnl_logging_system', some of the metadata sheet are populated for the user
        Default: None
    subconfiguration: string
        Name of sub-configuration
        If configuration is 'lfnl_logging_system', some of the metadata sheet are populated for the user
        Default: None
    """
    args = Namespace()
    args.verbose = 0
    args.dir = os.path.dirname(filepath)
    args.filepath = filepath

    make_xlsx(args, fields_list, metadata, conversions, data, metadata_df, DB, CRUISE_NUMBER, configuration, subconfiguration)

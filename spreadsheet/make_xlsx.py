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
import metadata_fields as metadata_fields
from pull_cf_standard_names import create_cf_standard_names_json
import os
from argparse import Namespace
#from website.database.get_data import get_data, get_personnel_list, get_cruise
import numpy as np
from datetime import datetime

DEBUG = 1

DEFAULT_FONT = 'Calibri'
DEFAULT_SIZE = 10

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
        self.sheet.hide()  # Hide the sheet
        # For holding the current row to add variables on
        self.current_column = 0

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

def write_readme(args, workbook):
    """
    Adds a README sheet to workbook
    Parameters
    ----------
    args : argparse object
        The input arguments
    workbook : xlsxwriter Workbook
        The workbook for the README sheet
    """

    sheet = workbook.add_worksheet('README')

    sheet.set_column(0, 2, width=30)

    header_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'right': True,
        'bottom': True,
        'bold': True,
        'text_wrap': True,
        'valign': 'center',
        'font_size': 25,
        'bg_color': '#B9F6F5',
    })

    sheet.write(1, 0, "README", header_format)
    sheet.set_row(1, 30)

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

    parameter_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE + 1,
            'bg_color': '#B9F6F5'
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

    hidden_col_format = workbook.add_format({
        'bold': False,
        'font_name': DEFAULT_FONT,
        'text_wrap': True,
        'valign': 'vcenter',
        'bottom': True,
        'right': 5,
        'font_size': DEFAULT_SIZE,
        })

    input_optional_format = workbook.add_format({
        'bold': False,
        'font_name': DEFAULT_FONT,
        'text_wrap': True,
        'valign': 'vcenter',
        'bottom': True,
        'right': 5,
        'font_size': DEFAULT_SIZE,
        'left': 5
        })

    input_datetime_format = workbook.add_format({
        'bold': False,
        'font_name': DEFAULT_FONT,
        'text_wrap': True,
        'valign': 'vcenter',
        'bottom': True,
        'right': 5,
        'font_size': DEFAULT_SIZE,
        'left': 5,
        'num_format': 'yyyy-mm-ddThh:mm:ssZ'
        })

    input_required_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#F5E69E',
            'left': 5,
            'right': 5
        })

    input_required_key_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#F5E69E',
            'left': True,
            'right': True
        })

    acdd_highly_recommended_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#F06292'
        })

    acdd_recommended_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#F8BBD0'
        })

    acdd_suggested_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#F5E1E8'
        })


    eml_required_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#AED581'
        })

    eml_optional_format = workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#DCEDC8'
        })

    bottom_border_format = workbook.add_format({
        'bold': False,
        'font_name': DEFAULT_FONT,
        'text_wrap': True,
        'valign': 'vcenter',
        'top': 5,
        'font_size': DEFAULT_SIZE,
        })

    cols = [
            'Field name',
            'systemName',
            'Content',
            'ACDD term',
            'ACDD description',
            'EML term',
            'EML description'
            'Link'
            ]

    header_row = 5
    start_row = header_row + 2

    for ii, col in enumerate(cols):
        sheet.write(header_row, ii, col, header_format)
        sheet.write(header_row+1, ii, col, blank_format)
        sheet.set_row(header_row+1, None, None, {'hidden': True})

    metadata_fields_df = pd.DataFrame(columns=(cols))

    for ii, mfield in enumerate(metadata_fields.metadata_fields):

        row = start_row + ii

        if 'acdd' in mfield.keys():
            acdd_term = mfield['acdd']['name']
            acdd_description = mfield['acdd']['description']
            if mfield['acdd']['recommendations'] == 'Highly Recommended':
                acdd_format = acdd_highly_recommended_format
            elif mfield['acdd']['recommendations'] == 'Recommended':
                acdd_format = acdd_recommended_format
            else:
                acdd_format = acdd_suggested_format
        else:
            acdd_term = ''
            acdd_description = ''
            acdd_format = blank_format

        if 'eml' in mfield.keys():
            eml_term = mfield['eml']['name']
            eml_description = mfield['eml']['description']
            if mfield['eml']['recommendations'] == 'Required':
                eml_format = eml_required_format
            else:
                eml_format = eml_optional_format
        else:
            eml_term = ''
            eml_description = ''
            eml_format = blank_format

        if mfield['format'] == 'datetime':
            input_format = input_datetime_format
        else:
            input_format = input_optional_format

        if 'default' in mfield.keys():
            content = mfield['default']
        elif 'derive_from' in mfield.keys() and DB:
            content = derive_content(mfield, data=data, DB=DB)
        else:
            content = ''

        if 'link' in mfield.keys():
            link = mfield['link']
        else:
            link = ''

        # Column A: Display name
        sheet.write(row, 0, mfield['disp_name'], parameter_format)

        # Column B (hidden): System field name
        sheet.write(row, 1, mfield['name'], hidden_col_format)
        sheet.set_column(1, 1, None, None, {'hidden': True})

        # Column C: Content
        if type(metadata_df) == pd.core.frame.DataFrame:
            try:
                sheet.write(row,2,metadata_df[mfield][0], input_format)
            except:
                sheet.write(row, 2, content, input_format)
                continue
        else:
            if configuration == 'lfnl_logging_system':
                sheet.write(row, 2, content, input_format)
            else:
                sheet.write(row, 2, '', input_format)

        if 'valid' in mfield.keys():
            valid_copy = mfield['valid'].copy()

            if len(valid_copy['input_message']) > 255:
                valid_copy['input_message'] = valid_copy[
                    'input_message'][:252] + '...'

            if len(mfield['disp_name']) > 32:
                valid_copy['input_title'] = mfield['disp_name'][:32]
            else:
                valid_copy['input_title'] = mfield['disp_name']

            if 'long_list' in mfield.keys():

                # Add the validation variable to the hidden sheet
                lst_values = mfield['valid']['source']

                ref = variable_sheet_obj.add_row(
                    mfield['name'], lst_values)

                valid_copy.pop('source', None)
                valid_copy['value'] = ref

            sheet.data_validation(first_row=row,
                                  first_col=2,
                                  last_row=row,
                                  last_col=2,
                                  options=valid_copy)

        # Column D: ACDD name
        sheet.write(row, 3, acdd_term, acdd_format)

        # Column E: ACDD description
        sheet.write(row, 4, acdd_description, acdd_format)

        # Column F: EML name
        sheet.write(row, 5, eml_term, eml_format)

        # Column G: EML description
        sheet.write(row, 6, eml_description, eml_format)

        # Column H: Link
        sheet.write(row, 7, link, blank_format)

        length = max([len(acdd_description), len(eml_description)])

        if mfield['name'] == 'summary':
            height = 150
        elif length > 0:
            height = int(length/4)
        else:
            height = 15

        sheet.set_row(row, height)

    for col in range(len(cols)):
        sheet.write(row+1, col,'',bottom_border_format)

    #sheet.merge_range('C2:C4', 'Required for metadata catalogue', input_required_key_format)

    sheet.merge_range('D2:E2', 'Highly recommended ACDD term', acdd_highly_recommended_format)
    sheet.merge_range('D3:E3', 'Recommended ACDD term', acdd_recommended_format)
    sheet.merge_range('D4:E4', 'Suggested ACDD term', acdd_suggested_format)

    sheet.merge_range('F2:G2', 'Required EML term', eml_required_format)
    sheet.merge_range('F3:G3', 'Optional EML term', eml_optional_format)

    sheet.set_column(0, 0, width=20)
    sheet.set_column(2, 2, width=40)
    sheet.set_column(3, 3, width=20)
    sheet.set_column(4, 4, width=60)
    sheet.set_column(5, 5, width=20)
    sheet.set_column(6, 6, width=60)
    sheet.set_column(7, 7, width=60)

    # Freeze the rows at the top
    sheet.freeze_panes(6, 1)

def make_xlsx(args, fields_list, metadata, conversions, data, metadata_df, DB, CRUISE_NUMBER=None, configuration=None):
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


    header_format = workbook.add_format({
        'font_color': '#FF0000',
        'font_name': DEFAULT_FONT,
        'bold': False,
        'text_wrap': False,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 2
    })

    field_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bottom': True,
        'right': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 1,
        'bg_color': '#B9F6F5'
    })

    cf_field_format = workbook.add_format({
        'font_name': DEFAULT_FONT,
        'bottom': True,
        'right': True,
        'bold': False,
        'text_wrap': True,
        'valign': 'vcenter',
        'font_size': DEFAULT_SIZE + 1,
        'bg_color': '#BDB9F6'
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

    title_row = 1  # starting row
    start_row = title_row + 2
    parameter_row = title_row + 1  # Parameter row, hidden
    end_row = 20000  # ending row

    # Loop over all the variables needed
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
                data_sheet.write(title_row, ii, field['disp_name'], field_format)

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
                                df = pd.read_csv(f'Learnings_from_AeN_template_generator/config/{table}.csv')
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

    cf_standard_names, cf_groups = create_cf_standard_names_json()

    for cf_standard_name in cf_standard_names:
        if cf_standard_name['id'] in fields_list:
            # Write title row
            data_sheet.write(title_row, ii, cf_standard_name['id'], cf_field_format)

            # Write row below with parameter name
            data_sheet.write(parameter_row, ii, cf_standard_name['id'])

            valid = {
                'validate': 'any',
                'input_title': cf_standard_name['id']
                }

            if len(cf_standard_name['description']) > 255:
                valid['input_message'] = cf_standard_name['description'][:252] + '...'
            else:
                valid['input_message'] = cf_standard_name['description']

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
    data_sheet.write(0, 0, '', header_format)
    # Add hint about pasting
    data_sheet.merge_range(0, 1, 0, 7,
                           "When pasting only use 'paste special' / 'paste only', selecting numbers and/or text ",
                           header_format)
    # Set height of row
    data_sheet.set_row(0, height=24)

    # Freeze the rows at the top
    data_sheet.freeze_panes(start_row, 0)

    # Hide ID row
    data_sheet.set_row(parameter_row, None, None, {'hidden': True})

    if conversions:
        write_conversion(args, workbook)

    write_readme(args, workbook)

    workbook.close()

def write_file(filepath, fields_list, metadata=True, conversions=True, data=None, metadata_df=None, DB=None, CRUISE_NUMBER=None, configuration=None):
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
    """
    args = Namespace()
    args.verbose = 0
    args.dir = os.path.dirname(filepath)
    args.filepath = filepath

    make_xlsx(args, fields_list, metadata, conversions, data, metadata_df, DB, CRUISE_NUMBER, configuration)

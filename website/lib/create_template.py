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
import math
from argparse import Namespace
from .get_configurations import get_field_requirements
from .pull_global_attributes import global_attributes_to_df
import os
import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
target_dir = script_dir / "../config/fields/CF_Attributes"
sys.path.insert(0, str(target_dir.resolve()))

from process_cf_attributes import CF_Attributes

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

class Template(object):
    """
    Spreadsheet template object
    """

    def __init__(self, filepath, fields_filepath, config, subconfig):
        self.filepath = filepath
        self.config = config
        self.subconfig = subconfig
        self.workbook = xlsxwriter.Workbook(self.filepath)
        self.fields_filepath = fields_filepath

        # Set font
        self.workbook.formats[0].set_font_name(DEFAULT_FONT)
        self.workbook.formats[0].set_font_size(DEFAULT_SIZE)

    def add_global_attributes(self):
        global_attributes = Global_Attributes_Sheet(self)
        global_attributes.add_global_attributes()

    def add_variable_attributes(self, sheetname, content):
        variable_attributes = Variable_Attributes_Sheet(sheetname, content, self)
        variable_attributes.add_variable_attributes()

    def add_data_sheet(self, sheetname, sheet_info, content, split_personnel_columns):
        data_sheet = Data_Sheet(sheetname, sheet_info, content, self)
        data_sheet.write_key()
        data_sheet.write_columns(split_personnel_columns)

    def add_conversions(self):
        Conversions_Sheet(self)

    def add_readme(self):
        Readme_Sheet(self)

    def close_and_save(self):
        self.workbook.close()

class Data_Sheet(object):
    """
    Data sheet object
    """
    def __init__(self, sheetname, sheet_info, content, template):
        self.sheetname = sheetname
        self.sheet_info = sheet_info
        self.sheet_description = sheet_info['description']
        self.sheet_source = sheet_info['source']
        self.content = content
        self.template = template
        self.sheet = self.template.workbook.add_worksheet(self.sheetname)

        self.required_field_format = self.template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE + 1,
            'bg_color': '#B74F6F'
        })

        self.recommended_field_format = self.template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE + 1,
            'bg_color': '#F49E4C'
        })

        self.optional_field_format = self.template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE + 1,
            'bg_color': '#C0DF85'
        })

        self.cf_field_format = self.template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE + 1,
            'bg_color': '#A4BFEB'
        })

        self.dwc_term_format = self.template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE + 1,
            'bg_color': 'green'
        })

        self.bounds_format = self.template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE + 1,
            'bg_color': '#BCE7FD'
        })

        self.date_format = self.template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': False,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'num_format': 'dd/mm/yy'
            })

        self.time_format = self.template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bold': False,
            'text_wrap': False,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'num_format': 'hh:mm:ss'
            })

        self.sheet_description_format = self.template.workbook.add_format({
            'bold': True,
            'font_size': DEFAULT_SIZE,
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })

    def write_key(self):
        '''
        Writing a key for colours at the top of the data sheet
        '''

        paste_message = "Use 'paste special' / 'paste only' so not to overwrite cell restrictions"

        # Key
        if self.template.config == 'Nansen Legacy logging system':
            self.title_row = 10  # starting row
            self.sheet.merge_range('A2:D2', 'Required', self.required_field_format)
            self.sheet.merge_range('A3:D3', 'Recommended', self.recommended_field_format)
            self.sheet.merge_range('A4:D4', 'Optional', self.optional_field_format)
            self.sheet.merge_range('A5:D5', 'CF standard name', self.cf_field_format)
            self.sheet.merge_range('A6:D6', 'Darwin Core term', self.dwc_term_format)
            self.sheet.merge_range('A7:D7', paste_message)
            self.sheet.merge_range('A9:G9', f'{self.sheetname}: {self.sheet_description}', self.sheet_description_format)
        elif self.template.config == 'CF-NetCDF':
            self.title_row = 10
            self.sheet.merge_range('A2:D2', 'CF standard name', self.cf_field_format)
            self.sheet.merge_range('A3:D3', 'Cell bounds', self.bounds_format)
            self.sheet.merge_range('A4:D4', 'Other fields', self.optional_field_format)
            self.sheet.merge_range('A5:D5', 'Darwin Core term', self.dwc_term_format)
            self.sheet.merge_range('A6:D6', paste_message)
            self.sheet.merge_range('A8:G8', f'{self.sheetname}: {self.sheet_description}', self.sheet_description_format)
            self.sheet.merge_range('A9:G9', self.sheet_source, self.sheet_description_format)
        elif self.template.config == 'Darwin Core':
            self.title_row = 11
            self.sheet.merge_range('A2:D2', 'Required', self.required_field_format)
            self.sheet.merge_range('A3:D3', 'Recommended', self.recommended_field_format)
            self.sheet.merge_range('A4:D4', 'Other fields', self.optional_field_format)
            self.sheet.merge_range('A5:D5', 'CF standard name', self.cf_field_format)
            self.sheet.merge_range('A6:D6', 'Darwin Core term', self.dwc_term_format)
            self.sheet.merge_range('A7:D7', paste_message)
            self.sheet.merge_range('A9:G9', f'{self.sheetname}: {self.sheet_description}', self.sheet_description_format)
            self.sheet.merge_range('A10:G10', self.sheet_source, self.sheet_description_format)

    def write_columns(self, split_personnel_columns):
        '''
        Writing one column for each field
        '''
        start_row = self.title_row + 2
        parameter_row = self.title_row + 1  # Parameter row, hidden
        end_row = 20000  # final row to extend formatting and cell restrictions to

        (
        required_fields,
        recommended_fields,
        dwc_terms,
        cf_standard_names
        ) = get_field_requirements(
            fields_filepath=self.template.fields_filepath,
            config=self.template.config,
            subconfig=self.template.subconfig,
            sheetname=self.sheetname
            )

        # Sort the fields to determine the order of the columns
        # Fields ordered based on fields_order list
        # Fields not included in list are in random order at the end
        fields_order = []
        if self.sheetname == 'Data':
            fields_order = [
                'id',
                'parentID',
                'catalogNumber',
                'eventDate',
                'eventTime',
                'endDate',
                'endTime',
                'stationName',
                'statID',
                'decimalLatitude',
                'decimalLongitude',
                'endDecimalLatitude',
                'endDecimalLongitude',
                'minimumDepthInMeters',
                'maximumDepthInMeters',
                'minimumElevationInMeters',
                'maximumElevationInMeters',
                'gearType',
                'sampleType'
                ]

        sorted_dict = {}
        for field in fields_order:
            if field in self.content:
                sorted_dict[field] = self.content[field]
        for field, vals in self.content.items():
            if field not in fields_order:
                sorted_dict[field] = vals

        # Loop over all the variables/columns needed
        ii = 0

        for field, vals in sorted_dict.items():

            if 'bounds' in field:
                duplication = 2
                while duplication > 0:

                    field = field.replace('_bounds','')
                    if duplication == 2:
                        name = 'Minimum ' + field
                    elif duplication == 1:
                        name = 'Maximum ' + field

                    self.sheet.write(self.title_row, ii, name, self.bounds_format) # Write title row
                    self.sheet.write(parameter_row, ii, name.replace(' ', '_')) # Write title row

                    valid = {
                        'validate': 'decimal',
                        'input_title': name,
                        'criteria': '>=',
                        'value': '-1e100'
                        }
                    valid['input_message'] = add_line_breaks('For use when a data point does not represent a single point in space or time, but a cell of finite size. Use this variable to encode the extent of the cell (e.g. the minimum and maximum depth that a data point is representative of).', 35)
                    valid['input_message'].replace('\n', '\n\r')

                    self.sheet.data_validation(
                        first_row=start_row,
                        first_col=ii,
                        last_row=end_row,
                        last_col=ii,
                        options=valid
                        )

                    ii = ii + 1
                    duplication = duplication - 1

            else:
                if field in ['recordedBy', 'pi_details'] and split_personnel_columns == True:
                    duplication = 3
                else:
                    duplication = 1

                while duplication > 0:

                    # Write title row
                    if self.template.config == 'Nansen Legacy logging system' and field in ['recordedBy', 'pi_details'] and duplication == 3:
                        self.sheet.write(self.title_row, ii, vals['disp_name'], self.required_field_format)
                    elif field in required_fields:
                        self.sheet.write(self.title_row, ii, vals['disp_name'], self.required_field_format)
                    elif field in recommended_fields:
                        self.sheet.write(self.title_row, ii, vals['disp_name'], self.recommended_field_format)
                    elif field in cf_standard_names:
                        self.sheet.write(self.title_row, ii, vals['disp_name'], self.cf_field_format)
                    elif field in dwc_terms:
                        self.sheet.write(self.title_row, ii, vals['disp_name'], self.dwc_term_format)
                    else:
                        self.sheet.write(self.title_row, ii, vals['disp_name'], self.optional_field_format)

                    # Write row below with parameter name
                    if field in ['recordedBy', 'pi_details'] and split_personnel_columns == True:
                        self.sheet.write(parameter_row, ii, field+ '_' + str(3-duplication))
                    else:
                        self.sheet.write(parameter_row, ii, field)

                    # Write validations and cell restrictions
                    if 'valid' in vals:

                        # Need to make sure that 'input_message' is not more than 255
                        valid_copy = vals['valid'].copy()

                        if 'input_message' in valid_copy:
                            if len(valid_copy['input_message']) > 252:
                                valid_copy['input_message'] = valid_copy['input_message'][:249] + '...'
                        else:
                            if len(vals['description']) > 252:
                                valid_copy['input_message'] = vals['description'][:249] + '...'

                        valid_copy['input_message'] = add_line_breaks(valid_copy['input_message'], 35)
                        valid_copy['input_message'].replace('\n', '\n\r')

                        if len(vals['disp_name']) > 32:
                            valid_copy['input_title'] = vals['disp_name'][:32]
                        else:
                            valid_copy['input_title'] = vals['disp_name']

                        if 'long_list' in vals:
                            if field in ['recordedBy', 'pi_details'] and split_personnel_columns == True:
                                ref = self.template.variables_sheet.add_row(
                                    vals['id']+str(duplication), valid_copy['source']
                                    )
                            else:
                                ref = self.template.variables_sheet.add_row(
                                    vals['id'], valid_copy['source']
                                    )
                            valid_copy.pop('source', None)
                            valid_copy['value'] = ref

                        self.sheet.data_validation(
                            first_row=start_row,
                            first_col=ii,
                            last_row=end_row,
                            last_col=ii,
                            options=valid_copy
                            )

                    if 'cell_format' in vals:
                        if 'font_name' not in vals['cell_format']:
                            vals['cell_format']['font_name'] = DEFAULT_FONT
                        if 'font_size' not in vals['cell_format']:
                            vals['cell_format']['font_size'] = DEFAULT_SIZE
                        cell_format = self.template.workbook.add_format(vals['cell_format'])
                        self.sheet.set_column(
                            ii, ii, width=20, cell_format=cell_format)

                    # Add optional data to sheet
                    if 'data' in vals.keys():
                        vals['data'] = ['' if x == 'NULL' or (isinstance(x, float) and math.isnan(x)) else x for x in vals['data']]
                        if 'cell_format' in vals:
                            self.sheet.write_column(start_row,ii,vals['data'], cell_format)
                        else:
                            self.sheet.write_column(start_row,ii,vals['data'])

                    ii = ii + 1
                    duplication = duplication - 1

        # Set height of row
        self.sheet.set_row(0, height=24)
        self.sheet.set_column(0,ii-1,20)

        # Freeze the rows at the top
        self.sheet.freeze_panes(start_row, 0)

        # Hide ID row
        self.sheet.set_row(parameter_row, None, None, {'hidden': True})

class Variable_Attributes_Sheet(object):
    """
    Variable_Attributes sheet object
    """
    # TODO: Clean up code, e.g. remove duplicated code e.g. styles
    # TODO: Prefill some variable attributes e.g. bounds
    def __init__(self, sheetname, content, template):
        if sheetname == 'Data':
            self.sheetname = 'Variable_Attributes'
        else:
            self.sheetname = sheetname + '_Variable_Attributes'
        self.template = template
        self.content = content
        self.sheet = self.template.workbook.add_worksheet(self.sheetname)
        self.header_row = 8
        self.start_row = self.header_row + 2
        self.template = template

        self.cf_field_format = self.template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE + 1,
            'bg_color': '#A4BFEB'
        })

        self.required_format = template.workbook.add_format({
                'font_name': DEFAULT_FONT,
                'bottom': True,
                'right': True,
                'bold': False,
                'text_wrap': True,
                'valign': 'vcenter',
                'font_size': DEFAULT_SIZE,
                'bg_color': '#F06292'
            })

        self.recommended_format = template.workbook.add_format({
                'font_name': DEFAULT_FONT,
                'bottom': True,
                'right': True,
                'bold': False,
                'text_wrap': True,
                'valign': 'vcenter',
                'font_size': DEFAULT_SIZE,
                'bg_color': '#F8BBD0'
            })

        self.content_format = template.workbook.add_format({
            'bold': False,
            'font_name': DEFAULT_FONT,
            'text_wrap': True,
            'valign': 'vcenter',
            'bg_color': '#e6ffff',
            'bottom': True,
            'right': True,
            'font_size': DEFAULT_SIZE,
            })

        self.optional_format = template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'bottom': True,
            'right': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'vcenter',
            'font_size': DEFAULT_SIZE,
            'bg_color': '#F5E1E8'
        })

        self.sheet_description_format = self.template.workbook.add_format({
            'bold': True,
            'font_size': DEFAULT_SIZE,
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })

    def add_variable_attributes(self):
        cf_attributes = CF_Attributes()
        variable_attributes = cf_attributes.variable_attributes

        variable_attributes['coverage_content_type'] = {
            'Type': 'S',
            'Use': 'C, D', # Could be more
            'Description': 'An ISO 19115-1 code to indicate the source of the data (image, thematicClassification, physicalMeasurement, auxiliaryInformation, qualityInformation, referenceInformation, modelResult, or coordinate).'
        }

        highly_recommended_variable_attributes = [
            'standard_name',
            'long_name',
            'units',
            'coverage_content_type'
        ]

        (
        required_fields,
        recommended_fields,
        dwc_terms,
        cf_standard_names
        ) = get_field_requirements(
            fields_filepath=self.template.fields_filepath,
            config=self.template.config,
            subconfig=self.template.subconfig,
            sheetname=self.sheetname
            )

        parameter_row = self.header_row + 1  # Parameter row, hidden
        attribute_row = parameter_row + 1
        column = 0

        # Adding attributes, one attribute per row
        for attr in highly_recommended_variable_attributes:
            self.sheet.write(attribute_row, column, attr, self.required_format)
            description = variable_attributes[attr]['Description']
            self.sheet.write(attribute_row, column+1, description, self.required_format)

            if attr in ['long_name']:
                height = 200
            elif len(description) > 75:
                height = int(len(description)/3)
            else:
                height = 25

            self.sheet.set_row(attribute_row, height)

            attribute_row = attribute_row + 1

        for attr, vals in variable_attributes.items():
            if attr not in highly_recommended_variable_attributes:
                self.sheet.write(attribute_row, column, attr, self.optional_format)
                description = variable_attributes[attr]['Description']
                self.sheet.write(attribute_row, column+1, description, self.optional_format)

                if len(description) > 75:
                    height = int(len(description)/3)
                else:
                    height = 25

                self.sheet.set_row(attribute_row, height)

                attribute_row = attribute_row + 1

        # Loop over all the variables/columns needed to add column headers
        column = column + 2

        for field, vals in self.content.items():

            # TODO: What about bounds?
            # Write row for variable name to be added
            self.sheet.write(self.header_row, 0, 'variable_name',self.optional_format)
            variable_name_description = '''Name to be assigned to the variable in the NetCDF file.
            Note that this is not a variable attribute, but the name assigned to the variable itself.
            This is normally short and not necessarily standardised except for on some specific
            CF profiles'''
            variable_name_description = ' '.join(line.strip() for line in variable_name_description.splitlines())
            self.sheet.write(self.header_row, 1, variable_name_description,self.optional_format)
            if vals['disp_name'] in cf_standard_names:
                variable_name = ''
            else:
                variable_name = vals['disp_name']
            self.sheet.write(self.header_row, column, variable_name, self.cf_field_format)
            self.sheet.set_row(self.header_row, 50)
            # Write row below with parameter name
            self.sheet.write(parameter_row, column, field)

            attribute_row = parameter_row + 1

            # Adding empty cells for user to enter values
            for attr in highly_recommended_variable_attributes:
                if attr == 'standard_name' and vals['disp_name'] in cf_standard_names:
                    value = vals['disp_name']
                else:
                    value = ''
                self.sheet.write(attribute_row, column, value, self.content_format)
                attribute_row = attribute_row + 1
            for attr, vals in variable_attributes.items():
                if attr not in highly_recommended_variable_attributes:
                    value = ''
                    self.sheet.write(attribute_row, column, value, self.content_format)
                    attribute_row = attribute_row + 1

            self.sheet.set_column(column, column, width=40)

            column = column + 1

        # Key
        sheet_description = 'Template for entering variable attributes, metadata that describe each variable'
        source = "Mostly from the 'Appendix A: Attributes' section of the CF conventions document"
        self.sheet.merge_range('A2:E2', sheet_description, self.sheet_description_format)
        self.sheet.merge_range('A3:E3', source)
        self.sheet.merge_range('A5:E5', 'Required attribute (in most cases)', self.required_format)
        self.sheet.merge_range('A6:E6', 'Other attributes', self.optional_format)

        self.sheet.set_column(0, 0, width=25)
        self.sheet.set_column(1, 1, width=60)

        # Freeze the rows at the top
        self.sheet.freeze_panes(self.header_row, 0)

        # Hide ID row
        self.sheet.set_row(parameter_row, None, None, {'hidden': True})

class Global_Attributes_Sheet(object):
    """
    Global_Attributes sheet object
    Global attributes or EML metadata
    """
    def __init__(self, template):
        self.sheetname = 'Global_Attributes'
        self.sheet = template.workbook.add_worksheet(self.sheetname)
        self.header_row = 10
        self.start_row = self.header_row + 2
        self.template = template

        self.header_format = template.workbook.add_format({
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

        self.content_format = template.workbook.add_format({
            'bold': False,
            'font_name': DEFAULT_FONT,
            'text_wrap': True,
            'valign': 'vcenter',
            'bg_color': '#e6ffff',
            'bottom': True,
            'right': True,
            'font_size': DEFAULT_SIZE,
            })

        self.blank_format = template.workbook.add_format({
            'bold': False,
            'font_name': DEFAULT_FONT,
            'text_wrap': True,
            'valign': 'vcenter',
            'bottom': True,
            'right': True,
            'font_size': DEFAULT_SIZE,
            })

        self.required_format = template.workbook.add_format({
                'font_name': DEFAULT_FONT,
                'bottom': True,
                'right': True,
                'bold': False,
                'text_wrap': True,
                'valign': 'vcenter',
                'font_size': DEFAULT_SIZE,
                'bg_color': '#F06292'
            })

        self.recommended_format = template.workbook.add_format({
                'font_name': DEFAULT_FONT,
                'bottom': True,
                'right': True,
                'bold': False,
                'text_wrap': True,
                'valign': 'vcenter',
                'font_size': DEFAULT_SIZE,
                'bg_color': '#F8BBD0'
            })

        self.optional_format = template.workbook.add_format({
                'font_name': DEFAULT_FONT,
                'bottom': True,
                'right': True,
                'bold': False,
                'text_wrap': True,
                'valign': 'vcenter',
                'font_size': DEFAULT_SIZE,
                'bg_color': '#F5E1E8'
            })

        self.sheet_description_format = self.template.workbook.add_format({
            'bold': True,
            'font_size': DEFAULT_SIZE,
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })


    def add_global_attributes(self):

        global_attributes_filepath = os.path.dirname(self.template.fields_filepath) + '/fields'
        df_global_attributes = global_attributes_to_df(global_attributes_filepath)
        df_global_attributes['Content'] = ''

        last_col = len(df_global_attributes.columns)-1

        for ii, col in enumerate(df_global_attributes.columns):
            self.sheet.write(self.header_row, ii, col, self.header_format)
            self.sheet.write(self.header_row+1, ii, col, self.blank_format)
            self.sheet.set_row(self.header_row+1, None, None, {'hidden': True})

        for idx, row in df_global_attributes.iterrows():

            row_num = self.start_row + idx

            if row['Requirement'] == 'Required':
                cell_format = self.required_format
            elif row['Requirement'] == 'Recommended':
                cell_format = self.recommended_format
            else:
                cell_format = self.optional_format

            for col, val in enumerate(row):

                if col == last_col:
                    cell_format = self.content_format

                if type(val) == float:
                    if math.isnan(val) and col == 3:
                        val = 'Optional'
                    elif math.isnan(val):
                        val = ''
                self.sheet.write(row_num, col, val, cell_format)

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

                    self.sheet.data_validation(
                        first_row=row_num,
                        first_col=col,
                        last_row=row_num,
                        last_col=col,
                        options=valid
                        )

            length = len(row['Description'])

            if row['Attribute'] == 'summary':
                height = 150
            elif length > 0:
                height = int(length/4)
            else:
                height = 15

            self.sheet.set_row(row_num, height)

        # Hide requirements column.
        self.sheet.set_column(3, 3, None, None, {'hidden': True})

        # Key
        sheet_description = 'Template for entering global attributes, metadata that describe the overall dataset'
        self.sheet.merge_range('A2:G2', sheet_description, self.sheet_description_format)
        self.sheet.merge_range('A4:B4', 'Required term', self.required_format)
        self.sheet.merge_range('A5:B5', 'Recommended term', self.recommended_format)
        self.sheet.merge_range('A6:B6', 'Optional term', self.optional_format)
        self.sheet.merge_range('A8:B8', 'More attributes can be selected from')
        self.sheet.merge_range('A9:B9', 'https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3')

        self.sheet.set_column(0, 0, width=20)
        self.sheet.set_column(1, 1, width=60)
        self.sheet.set_column(2, 2, width=30)
        self.sheet.set_column(4, 4, width=60)

        # Freeze the rows at the top
        self.sheet.freeze_panes(self.header_row+1, 1)


class Conversions_Sheet(object):
    """
    Conversions sheet object
    For converting coordinates from minutes and seconds to decimal
    """
    def __init__(self, template):
        self.sheetname = 'Conversions'
        self.sheet = template.workbook.add_worksheet(self.sheetname)

        parameter_format = template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'right': True,
            'bottom': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'left',
            'font_size': DEFAULT_SIZE + 2,
            'bg_color': '#B9F6F5',
        })
        center_format = template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'right': True,
            'bottom': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'center',
            'font_size': DEFAULT_SIZE + 2,
            'bg_color': '#23EEFF',
        })
        output_format = template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'right': True,
            'bottom': True,
            'bold': False,
            'text_wrap': True,
            'valign': 'left',
            'font_size': DEFAULT_SIZE + 2,
            'bg_color': '#FF94E8',
        })

        self.sheet.set_column(0, 2, width=30)

        self.sheet.write(1, 0, "Coordinate conversion ", parameter_format)
        self.sheet.merge_range(2, 0, 2, 1, "Degree Minutes Seconds ", center_format)
        self.sheet.write(3, 0, "Degrees ", parameter_format)
        self.sheet.write(4, 0, "Minutes ", parameter_format)
        self.sheet.write(5, 0, "Seconds ", parameter_format)
        self.sheet.write(6, 0, "Decimal degrees ", output_format)
        self.sheet.write(6, 1, "=B4+B5/60+B6/3600 ", output_format)
        self.sheet.merge_range(7, 0, 7, 1, "Degree decimal minutes", center_format)
        self.sheet.write(8, 0, "Degrees ", parameter_format)
        self.sheet.write(9, 0, "Decimal minutes ", parameter_format)
        self.sheet.write(10, 0, "Decimal degrees ", output_format)
        self.sheet.write(10, 1, "=B9+B10/60 ", output_format)

class Readme_Sheet(object):
    """
    Readme sheet object
    """
    def __init__(self, template):
        self.sheetname = 'README'
        self.sheet = template.workbook.add_worksheet(self.sheetname)
        self.template = template

        self.sheet.set_column(0, 0, width=150)

        readme_format = template.workbook.add_format({
            'font_name': DEFAULT_FONT,
            'font_size': 12,
            'bg_color': '#ffffff',
        })

        readme_filepath = os.path.dirname(self.template.fields_filepath) + '/readmes'

        if template.config == 'CF-NetCDF':
            readme_file = readme_filepath + '/cfnetcdf_readme.txt'
        elif template.config == 'Nansen Legacy logging system':
            readme_file = readme_filepath + '/nl_readme.txt'
        elif template.config == 'Darwin Core':
            readme_file = readme_filepath + '/dwc_readme.txt'

        with open(readme_file, 'r') as file:
            for idx, line in enumerate(file):

                line = line.replace('\n','')

                self.sheet.write(idx, 0, line, readme_format)
                self.sheet.set_row(idx, 25)

        self.sheet.activate()

class Variables_Sheet(object):
    """
    For options that go in drop-down lists
    This will be hidden
    """
    def __init__(self, template):
        self.template = template
        self.sheetname = 'Variables'
        self.sheet = template.workbook.add_worksheet(self.sheetname)
        self.current_column = 0
        self.sheet.hide()

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

def create_template(filepath, template_fields_dict, sheets_info, fields_filepath, config, subconfig=None, conversions=True, metadata=True, global_attributes_df=None,
split_personnel_columns=False):
    """
    Method for calling from other python programs
    Parameters
    ----------
    filepath: string
        The output file
    template_fields_dict : dictionary
        A dictionary of the fields to include in the template. Divided first by sheet. Includes descriptions, formats and validations
    sheets_info: dictionary
        Descriptions, source, name for each sheet
    config: string
        Configuration is either 'Darwin Core', 'CF-NetCDF', or 'Nansen Legacy logging system'
        Dictates what is included in the metadata sheet and readme sheets
        Also used to check if fields are required or recommended
    subconfig: string
        Configuration is either 'Darwin Core', 'CF-NetCDF', or 'Nansen Legacy logging system'
        Dictates what is included in the metadata sheet and readme sheets
        Used to check if fields are required or recommended
    conversions: Boolean
        Should the conversions sheet be written
        Default: True
    global_attributes_df: pandas.core.frame.DataFrame
        Optional parameter. Option to add global attributes from a dataframe to the 'global_attributes' sheet.
        Default: False
    split_personnel_columns: boolean
        Option to split personnel columns into multiple columns.
        Columns included: recordedBy, pi_details
        This is useful if you want to record multiple people in different columns
        Default: False
    """

    args = Namespace()
    args.verbose = 0
    args.dir = os.path.dirname(filepath)
    args.filepath = filepath

    template = Template(args.filepath, fields_filepath, config, subconfig)
    if metadata == True:
        template.add_global_attributes()
    for sheetname, content in template_fields_dict.items():
        template.add_data_sheet(sheetname, sheets_info[sheetname], content, split_personnel_columns)
        if metadata == True and config == 'CF-NetCDF':
            template.add_variable_attributes(sheetname,content)
    if conversions == True:
        template.add_conversions()
    template.add_readme()
    template.close_and_save()

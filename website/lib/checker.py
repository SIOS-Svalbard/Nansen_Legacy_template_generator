#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checks data before they can be imported into the metadata catalogue

@author: lukem
"""

import pandas as pd
import datetime
from datetime import datetime as dt
import numpy as np
import requests
import psycopg2
import getpass
from website.database.get_data import get_data, get_all_ids, get_registered_activities
import website.database.fields as fields
import website.database.metadata_fields as metadata_fields
from website.other_functions.other_functions import split_personnel_list
import uuid

def make_valid_dict(DB, CRUISE_NUMBER):
    """
    Makes a dictionary of the possible fields with their validation.
    Does this by reading the fields list from the fields.py library.
    Parameters
    ---------
    DB: dict
        Details of PSQL database
        Default: False boolean
    CRUISE_NUMBER: str
        Cruise number. Included in some PSQL table names
    Returns
    ---------
    field_dict : dict
        Dictionary of the possible fields
        Contains a Checker object under each name
    """
    # First we go through the fields.py
    field_dict = {}
    for field in fields.fields:
        if field['name'] not in ['recordedBy_details', 'pi_details']:
            new = Checker(DB, name=field['name'], disp_name=field['disp_name'])
            if 'valid' in field:
                new.set_validation(DB, CRUISE_NUMBER, field['valid'])
            if 'inherit' in field:
                new.inherit = field['inherit']
            if 'units' in field:
                new.units = field['units']
            field_dict[field['name']] = new

    return field_dict

def make_valid_dict_metadata(DB):
    """
    Makes a dictionary of the possible metadata fields with their validation.
    Does this by reading the metadata fields list from the metadata_fields.py library.
    Parameters
    ---------
    DB: dict
        Details of PSQL database
        Default: False boolean
    Returns
    ---------
    metadata_field_dict : dict
        Dictionary of the possible metadata fields
        Contains a Checker object under each name
    """
    # First we go through the metadata_fields.py
    metadata_field_dict = {}
    for metadata_field in metadata_fields.metadata_fields:
        if metadata_field['name'] not in ['recordedBy_details', 'pi_details']:
            new = Checker(DB, name=metadata_field['name'], disp_name=metadata_field['disp_name'])
            if 'valid' in metadata_field:
                new.set_validation(DB, metadata_field['valid'])
            if 'inherit' in metadata_field:
                new.inherit = metadata_field['inherit']
            if 'units' in metadata_field:
                new.units = metadata_field['units']
            metadata_field_dict[metadata_field['name']] = new

    return metadata_field_dict

def format_num(num):
    """
    Convert a string with a number to a number by removing common mistakes
    in Excel.
    Converts ',' to '.'
    Removes leading "'"
    If resulting string can be converted to an int, it is returned as an int,
    if not, it is returned as a float. If it can not be converted to a float,
    it throws a ValueError.
    Parameters
    ---------
    num: object
        The number to be converted.
        If it is an int or float, nothing is done with it.
        Needs to be convertible into a string.
    Returns
    ---------
    out: int or float
        The resulting int or float.
    """

    if isinstance(num, int) or isinstance(num, float):
        return num

    num_str = str(num).replace(',', '.').replace("'", '')

    try:
        out = int(num_str)
    except ValueError:
        out = float(num_str)
    return out


def is_nan(value):
    """
    Checks if value is 'nan' or NaT
    Parameters
    ---------
    value: object
        The object to be checked that it is not nan
    Returns
    ---------
    isnan: Boolean
        True: nan
        False: not nan
    """
    isnan = str(value).lower() == 'nan'
    isnat = str(value).lower() == 'nat'
    return isnan or isnat

class Evaluator(object):
    """ An object for holding a function for evaluating a type of data.
    The function should take two arguments, self and a value. By referencing and
    setting values on the object with self, it is possible to evaluate on
    multiple conditions."""

    def __init__(self, validation, func=None):
        """
        Initialise the Evaluator object.
        Parameters
        ---------
        validation: dict
            A dict containing the validation information.
            Can be used in evaluator function by referencing the property
            self.validation
        func: lambda function, optional
            This function should take two inputs, self and a value.
            If this is not set here, it needs to be set using the set_func
            method
            Should return a boolean, where True means the value has passed the
            test
            An example of a functions is:
            lambda self,x : self.valid['value'] < len(x)
        """

        self.validation = validation
        self.eval = func

    def set_func(self, func):
        """
        Method for setting the evaluator function.
        Parameters
        ---------
        func: lambda function, optional
            This function should take two inputs, self and a value.
            If this is not set here, it needs to be set using the set_func
            method
            Should return a boolean, where True means the value has passed the
            test
            An example of a functions is:
            lambda self, x : self.valid['value'] < len(x)
        """

        self.eval = func

    def evaluate(self, value):
        """
        Evaluate value with the evaluator
        Parameters
        ---------
        value: object
            The value to be evaluated
            Needs to be in a format that the function understands
        Returns
        ---------
        res: Boolean
            The result from the evaluator
            True, means that the value passed the evaluation
        """

        if self.eval == None:
            raise NameError(
                "No evaluator, set it during initialisation or with the 'set_func' method")
        try:
            res = self.eval(self, value)
        except TypeError:
            res = False
        if not(isinstance(res, bool)):
            raise ValueError(
                "The evaluator function is not returning a boolean")
        return res

class Field(object):
    """
    Object for holding the specification of a cell
    """

    def __init__(self, name, disp_name, validation={},
                 cell_format={}, width=20, long_list=False):
        """
        Initialising the object
        Parameters
        ----------
        name : str
               Name of object
        disp_name : str
               The title of the column
        validation : dict, optional
            A dictionary using the keywords defined in xlsxwriter
        cell_format : dict, optional
            A dictionary using the keywords defined in xlsxwriter
        width : int, optional
            Number of units for width
        long_list : Boolean, optional
            True for enabling the long list.
        """
        self.name = name  # Name of object
        self.disp_name = disp_name  # Title of column
        self.cell_format = cell_format  # For holding the formatting of the cell
        self.validation = validation  # For holding the validation of the cell
        self.long_list = long_list  # For holding the need for an entry in the
        # variables sheet
        self.width = width

    def set_validation(self, validation):
        """
        Set the validation of the cell
        Parameters
        ----------
        validation : dict
            A dictionary using the keywords defined in xlsxwriter
        """
        self.validation = validation

    def set_cell_format(self, cell_format):
        """
        Set the validation of the cell
        Parameters
        ----------
        cell_format : dict
            A dictionary using the keywords defined in xlsxwriter
        """
        self.cell_format = cell_format

    def set_width(self, width):
        """
        Set the cell width
        Parameters
        ----------
        width : int
            Number of units for width
        """
        self.width = width

    def set_long_list(self, long_list):
        """
        Set the need for moving the source in the list to a cell range in the
        variables sheet
        Parameters
        ----------
        long_list : Boolean
            True for enabling the long list.
        """
        self.long_list = long_list

class Checker(Field):
    """
    Object for holding the specification of a cell, and the validation of it
    Inherits from Field"""

    def __init__(self, DBNAME, inherit=False, units=None, *args, **kwargs):
        """
        Initialising the object
        Parameters
        ---------
        inherit: Boolean, optional
            Should the given field be inherited.
            Default: False
        units: string, optional
            The units of the field
        *args: arguments for Field
        **kwargs: keyword arguments for Field
        """
        Field.__init__(self, *args, **kwargs)
        if self.validation != {}:
            self.validator = self.get_validator(DB, CRUISE_NUMBER, self.validation)
        else:
            self.validator = lambda x: True

        self.inherit = inherit
        self.units = units

    def set_validation(self, DBNAME, CRUISE_NUMBER, validation):
        """
        Method for setting the validation by reading the dictionary
        and converting it using the
        Parameters
        ---------
        validation: dict
            The specifications of the validation as a dict
            See the valid dict in Fields for details
        """

        Field.set_validation(self, validation)
        self.validator = self.get_validator(DB, CRUISE_NUMBER, self.validation)

    def get_validator(self, DBNAME, CRUISE_NUMBER, validation=None):
        """
        Checks a parameter according to the defined validation
        Parameters
        ---------
        validation: dict, optional
            The valid dictionary defined in the fields.py file
            If not set, reads from the object
        Returns
        ---------
        validator: Evaluator
            A validator in the form of an Evaluator object
        """

        if validation == None:
            validation = self.validation

        validate = validation['validate']
        if validate == 'any':
            return Evaluator(validation, func=lambda self, x: isinstance(str(x), str))
        elif validate == 'list' and DB:
            if type(validation['source']) == list:
                lst = validation['source']
            else:
                table = validation['source']
                try:
                    df = get_data(DB, table)
                except:
                    df = get_data(DB, table+'_'+CRUISE_NUMBER)
                lst = df[self.name.lower()].values
            return Evaluator(lst, func=lambda self, x: str(x) in self.validation)

        criteria = validation['criteria']

        def _formula_to_date(formula):
            """
            Internal function for converting validation date functions (Excel
            function) to a datetime date object
            Parameters
            ---------
            formula: str
                The Excel formula to be converted
                Supports simple addition and subtraction and the function TODAY
            Returns
            ---------
            date: datetime date object
                The resulting date from the formula
            """

            form = formula.replace('=', '')
            if 'TODAY()' in form:
                form = form.replace('TODAY()', 'datetime.datetime.today()')
            if '+' in form:
                parts = form.split('+')
                parts[1] = 'datetime.timedelta(days=' + parts[1] + ')'
                form = parts[0] + '+' + parts[1]
            elif '-' in form:
                parts = form.split('-')
                parts[1] = 'datetime.timedelta(days=' + parts[1] + ')'
                form = parts[0] + '-' + parts[1]
            return eval(form)

        if validate == 'length':
            if criteria == 'between':
                return Evaluator(validation, func=lambda self, x: self.validation['minimum'] <= len(x) <= self.validation['maximum'])
            else:
                return Evaluator(validation, func=lambda self, x: eval("len(x) " + self.validation['criteria'] + str(self.validation['value'])))
        elif validate == 'decimal':
            if criteria == 'between':
                return Evaluator(validation, func=lambda self, x: (isinstance(x, int) or isinstance(x, float)) and self.validation['minimum'] <= float(x) <= self.validation['maximum'])
            else:
                return Evaluator(validation, func=lambda self, x: (isinstance(x, int) or isinstance(x, float)) and eval("float(x) " + self.validation['criteria'] + "self.validation['value']"))
        elif validate == 'integer':
            if criteria == 'between':
                return Evaluator(validation, func=lambda self, x: isinstance(x, int) and self.validation['minimum'] <= int(x) <= self.validation['maximum'])
            else:
                return Evaluator(validation, func=lambda self, x: isinstance(x, int) and eval("int(x) " + self.validation['criteria'] + "int(self.validation['value'])"))
        elif validate == 'time':
            if criteria == 'between':
                if isinstance(validation['minimum'], float) or isinstance(validation['minimum'], int):
                    minimum = (datetime.datetime(1, 1, 1, 0, 0) +
                                datetime.timedelta(days=validation['minimum'])).time()
                    maximum = (datetime.datetime(1, 1, 1, 0, 0) +
                                datetime.timedelta(days=validation['maximum'])).time()
                else:
                    minimum = validation['minimum']
                    maximum = validation['maximum']
                ev = Evaluator(validation)
                ev.minimum = minimum
                ev.maximum = maximum
                ev.set_func(lambda self, x: self.minimum <= x <= self.maximum)
                return ev
            else:
                if isinstance(validation['value'], float) or isinstance(validation['value'], int):
                    limit = (datetime.datetime(1, 1, 1, 0, 0) +
                              datetime.timedelta(days=validation['value'])).time()
                else:
                    limit = validation['value']

                ev = Evaluator(validation)
                ev.limit = limit
                ev.set_func(lambda self, x: eval(
                    "x" + self.validation['criteria'] + "self.limit"))
                return ev
        elif validate == 'date':
            if criteria == 'between':
                minimum = validation['minimum']
                maximum = validation['maximum']
                if not(isinstance(minimum, datetime.date)):
                    # We now have a formula
                    minimum = _formula_to_date(minimum)
                if not(isinstance(maximum, datetime.date)):
                    # We now have a formula
                    maximum = _formula_to_date(maximum)
                ev = Evaluator(validation)
                ev.minimum = minimum
                ev.maximum = maximum.date()
                ev.set_func(lambda self, x: self.minimum <= x <= self.maximum)
                # ev.set_func(lambda self,x: print(self.minimum , x , self.maximum))
                return ev

            else:
                limit = validation['value']
                if not(isinstance(limit, datetime.date)):
                    # We now have a formula
                    limit = _formula_to_date(limit)

                ev = Evaluator(validation)
                ev.limit = limit

                ev.set_func(lambda self, x: eval(
                    "x" + self.validation['criteria'] + "self.limit"))

                return ev

        elif validate == 'datetime':
            if criteria == 'between':
                minimum = validation['minimum']
                maximum = validation['maximum']
                if not(isinstance(minimum, datetime.datetime)):
                    # We now have a formula
                    minimum = _formula_to_date(minimum)
                if not(isinstance(maximum, datetime.datetime)):
                    # We now have a formula
                    maximum = _formula_to_date(maximum)

                ev = Evaluator(validation)
                ev.minimum = minimum
                ev.maximum = maximum
                ev.set_func(lambda self, x: self.minimum <= x <= self.maximum)
                # ev.set_func(lambda self,x: print(self.minimum , x , self.maximum))
                return ev

            else:
                limit = validation['value']
                if not(isinstance(limit, datetime.datetime)):
                    # We now have a formula
                    limit = _formula_to_date(limit)

                ev = Evaluator(validation)
                ev.limit = limit

                ev.set_func(lambda self, x: eval(
                    "x" + self.validation['criteria'] + "self.limit"))

                return ev

        else:
            raise NotImplementedError("No validator available for the object")

def clean(data):
    """
    Goes through the array and cleans up the data
    Fixes some numbers that have not been converted correctly
    Converts uuids to lower and makes sure seperator is '-' and not '+' '/'
    Parameters
    ---------
    data: Pandas dataframe of data to be cleaned

    Returns
    ---------
    cleaned_data: Pandas dataframe
        The cleaned data
    """

    try:
        data['id'] = data['id'].replace('/','-', regex=True)
    except:
        pass

    try:
        data['id'] = data['id'].replace('+','-', regex=True)
    except:
        pass

    cleaned_data = data.copy()
    pd.set_option('mode.chained_assignment', None) # PREVENTING COPY WARNING ORIGINATING FROM BELOW

    for col in data.columns:
        if col != 'id':
            for idx, row in data.iterrows():
                try:
                    num = format_num(row[col])
                    cleaned_data[col][idx] = num # COPY WARNING
                except ValueError:
                    continue

    return cleaned_data

def to_ranges_str(lis):
    """
    Conversion of a list for integers to a string containing ranges.
    For instance [1, 2, 3, 4] will be returned as the string [1 - 4]
    Parameters
    ---------
    lis: list of ints
        The list to be converted
    Returns
    ---------
    out: string
        The resulting string with ranges for sequences consisting of more than
        two steps. Enclosed in swuare ([]) brackets
    """

    out = '['+str(lis[0])
    if len(lis) == 2:
        out = out + ', ' + str(lis[1])
    elif len(lis) > 2:
        first = lis[0]
        prev = first
        ii = 1
        for l in lis[1:]:

            if l == prev+1:
                prev = l
                ii = ii+1
            else:
                # longer step
                if ii > 2:
                    out = out + ' - ' + str(prev)
                # else:
                    # out = out +', '+str(prev)
                prev = l
                first = l
                out = out + ', ' + str(first)
                ii = 0
        if ii > 2:
            out = out + ' - ' + str(prev)
        # else:
            # out = out +', '+str(prev)

    out = out + ']'
    return out

def check_value(value, checker):
    """
    Check the value with the checker.
    Does some additional checks in addition to the checks in checker
    Parameters
    ---------
    value: object
        The value to be checked
    checker: Checker
        The Checker to use
    Returns
    ---------
    bool : Boolean
        True, passed
        False, failed
    """

    if value == '' or is_nan(value) or (isinstance(value, float) and np.isnan(value)):
        return True
    if checker.validation['validate'] == 'length':
        for ID in ['id', 'parentID', 'measurementID','eventID', 'occurrenceID']:
            if ID in checker.name.lower():
                try:
                    uuid.UUID(value)
                except ValueError:
                    return False

    if checker.validation['validate'] == 'date':
        try:
            value = value.to_pydatetime().date()
        except:
            pass
        if type(value) == datetime.date(1, 1, 1).__class__:
            return checker.validator.evaluate(value)
    elif checker.validation['validate'] == 'datetime':
        try:
            value = value.to_pydatetime()
        except:
            pass
        if type(value) == datetime.datetime(1, 1, 1).__class__:
            return checker.validator.evaluate(value)
    elif checker.validation['validate'] == 'time':
        if isinstance(value,datetime.time) or value == None:
            value = value
        else:
            value = value.to_pydatetime().time()
        return checker.validator.evaluate(value)
    elif checker.validation['validate'] == 'integer' or checker.validation['validate'] == 'decimal':
        try:
            num = format_num(value)
        except ValueError:
            num = value
        return checker.validator.evaluate(num)
    elif checker.validation['validate'] == 'list':
        return checker.validator.evaluate(value)
    else:
        return checker.validator.evaluate(value)

def check_array(data, checker_list, registered_ids, required, new, firstrow, old_id):
    """
    Checks the data according to the validators in the checker_list
    Returns True if the data is good, as well as an empty string
    Parameters
    ---------
    data : numpy ndarray of objects
        The data to be checked.
        The first row should contain the names of the fields as specified in fields.py
    checker_list : dict of Checker objects
        This is a list of the possible checkers made by make_valid_dict
    required: List of required columns
    registered_ids: List of UUIDS
        This is a list of UUIDS already registered in the metadata catalogue,so we can check for duplicates
    new: Boolean
        Whether the record(s) is being logged for the first time or not
        Influences whether we check whether id already registered
    firstrow: int
        Row number of first row in source data that includes data.
        If data are submitted from the GUI form, this should be 0 or not provided.
        If data are submitted from the Excel templates this should be 4.
    old_id: string
        If UUID has been updated using the GUI form, this is the ID previously used
        for that record. If ID has been changed, checking as if it is a new ID.
        Default = False, for use when submitting multiple records, e.g. from spreadsheet
    Returns
    ---------
    good : Boolean
        A boolean specifying if the data passed the checks (True)
    errors: list of strings
        A string per error, describing where the error was found
        On the form: paramName: disp_name : row
    """
    good = True
    errors = []

    recordedBy_field_count = 0
    pi_field_count = 0

    for req in required:
        if req not in data.columns:
            good = False
            if req in ['pi_name', 'pi_email', 'pi_orcid', 'pi_institution']:
                if pi_field_count == 0 and req != 'pi_orcid':
                    errors.append(f'Required field "pi_details" is missing')
                    pi_field_count = pi_field_count + 1
            elif req in ['recordedBy_name', 'recordedBy_email', 'recordedBy_orcid', 'recordedBy_institution']:
                if recordedBy_field_count == 0 and req != 'recordedBy_orcid':
                    errors.append(f'Required field "recordedBy_details" is missing')
                    recordedBy_field_count = recordedBy_field_count + 1
            else:
                errors.append(f'Required field "{req}" is missing')

    # INHERIT BEFORE CHECKER SO COLUMNS MUST BE THERE REGARDLESS OF WHETHER THERE IS A PARENTID
    unknown_columns = []
    for col in data.columns:
        if col not in checker_list.keys():
            unknown_columns.append(col)
    if unknown_columns != []:
        good = False
        errors.append(f'Field name not recognised: {unknown_columns}')

    if not(good):
        errors.append("Not doing any more tests until all required fields are present and all fields are recognised")
        return good, errors

    already_registered_ids = []
    duplicate_ids = []
    parent_child = []
    missing_parents = []

    for idx, row in data.iterrows():
        if row['id'] != '' and type(row['id']) == str:
            if row['id'] != old_id and old_id != False:
                new = True
            rownum = idx + firstrow
            if row['id'] in registered_ids and new == True:
                good = False
                already_registered_ids.append(rownum)
            elif not data['id'].is_unique:
                duplicate_ids.append(rownum)
                good = False
            elif 'parentID' in data.columns:
                if row['id'] == row['parentID']:
                    parent_child.append(rownum)
                    good = False
        if 'parentID' in data.columns:
            if row['parentID'] != '' and row['parentID'] not in registered_ids and row['parentID'] not in data['id'].values:
                missing_parents.append(rownum)

    if already_registered_ids != []:
        good = False
        if len(data) > 1:
            errors.append(f'ID(s) already registered in the system, Rows: {already_registered_ids}')
        else:
            errors.append('ID already registered in the system')

    if duplicate_ids != []:
        good = False
        if len(data) > 1:
            errors.append(f'ID(s) registered more than once in same upload, Rows: {duplicate_ids}')

    if parent_child != []:
        good = False
        if len(data) > 1:
            errors.append(f'ID is same as Parent ID, Rows: {parent_child}')
        else:
            errors.append('ID and ParentID cannot be the same')

    if missing_parents != []:
        good = False
        if len(data) > 1:
            errors.append(f'ParentID not registered, Rows {missing_parents}')
        else:
            errors.append('ParentID not registered in system')

    minmaxdepths = []
    minmaxelevations = []

    for col in data.columns:
        content_errors = []
        checker = checker_list[col]
        blanks = []

        for idx, row in data.iterrows():
            rownum = idx + firstrow
            val = row[col]
            if val != 'NULL':
                if not check_value(val, checker):
                    content_errors.append(rownum)

            if col in required:

                if val == '' and col not in ['pi_orcid', 'recordedBy_orcid']:
                    blanks.append(rownum)

        if content_errors != []:
            good = False
            if len(data) > 1:
                errors.append(checker.disp_name + ' ('+checker.name + ')'+", Rows: " +
                              to_ranges_str(content_errors) + ' Error: Content in wrong format')
            else:
                errors.append(f'Content in wrong format ({checker.disp_name})')

        if blanks != []:
            good = False
            if len(data) > 1:
                errors.append(checker.disp_name + ' ('+checker.name + ')'+", Rows: " +
                              to_ranges_str(content_errors) + ' Error: Value missing (required)')
            else:
                errors.append(f'Required value missing ({checker.disp_name})')

        if col == 'minimumDepthInMeters' and 'minimumDepthInMeters' in data.columns:
            for idx, row in data.iterrows():
                rownum = idx + firstrow
                mindepth = row[col]
                maxdepth = row['maximumDepthInMeters']
                if maxdepth not in ['', None, 'NULL'] and mindepth not in ['', None, 'NULL']:
                    if mindepth > float(maxdepth):
                        minmaxdepths.append(rownum)

        if col == 'minimumElevationInMeters' and 'minimumElevationInMeters' in data.columns:
            for idx, row in data.iterrows():
                rownum = idx + firstrow
                minelevation = row[col]
                maxelevation = row['maximumElevationInMeters']
                if maxelevation not in ['', None, 'NULL'] and minelevation not in ['', None, 'NULL']:
                    if minelevation > float(maxelevation):
                        minmaxelevations.append(rownum)

    if minmaxdepths != []:
        good = False
        if len(data) > 1:
            errors.append(f'Maximum depth must be greater than or equal to minimum depth, Rows: {minmaxdepths}')
        else:
            errors.append('Maximum depth must be greater than or equal to minimum depth.')

    if minmaxelevations != []:
        good = False
        if len(data) > 1:
            errors.append(f'Maximum elevation must be greater than or equal to minimum depth, Rows: {minmaxdepths}')
        else:
            errors.append('Maximum elevation must be greater than or equal to minimum depth.')

    missingdepths = []

    for idx, row in data.iterrows():
        rownum = idx + firstrow
        n = 0
        for col in ['minimumDepthInMeters', 'maximumDepthInMeters', 'minimumElevationInMeters', 'maximumElevationInMeters']:
            if col in data.columns:
                if row[col] == '':
                    n = n + 1
        if n == 4:
            missingdepths.append(rownum)

    if missingdepths != []:
        good = False
        if len(data) > 1:
            errors.append(f'Please include an elevation or depth (preferably both minimum and maximum, they can be the same), Rows: {missingdepths}')
        else:
            errors.append('Please include an elevation or depth (preferably both minimum and maximum, they can be the same)')

    '''
    Potential additional checks:
        1. Prevent people entering both elevation and depth.
        2. Reject activities logged with same date and time as another activity
    '''

    return good, errors

def check_meta(metadata, metadata_checker_list):
    """
    Checks the data according to the validators in the checker_list
    Returns True if the data is good, as well as an empty string
    Parameters
    ---------
    metadata : pandas dataframe
        The metadata to be checked.
        The first row should contain the names of the fields as specified in metadata_fields.py
    metadata_checker_list : dict of Checker objects
        This is a list of the possible checkers made by make_valid_dict_metadata
    Returns
    ---------
    good : Boolean
        A boolean specifying if the data passed the checks (True)
    errors: list of strings
        A string per error, describing where the error was found
        On the form: paramName: disp_name : row
    """

    good = True
    errors = []

    for col in metadata.columns:
        metadata_checker = metadata_checker_list[col]
        blanks = []

        val = metadata[col].item()
        if val != 'NULL' and not check_value(val, metadata_checker):
            good = False
            errors.append(f'Content in wrong format ({metadata_checker.disp_name})')

    return good, errors

def run(data, metadata=False, required=[], DB=None, CRUISE_NUMBER=None, new=True, firstrow=0, old_id=False):
    """
    Method for running the checker on the given input.
    If importing in another program, this should be called instead of the main
    function
    Can be used to return the data as well
    Parameters
    ---------
    data: Pandas dataframe
        Pandas dataframe of data to be checked.
        'other' hstore should be expanded into separate columns before input
    metadata: Pandas dataframe
        Pandas dataframe of the metadata to be checked
        Default None, if not present (not compulsary)
    required: List
        List of required columns
        Default: Empty list []
    DB: dict
        Details of PSQL database
        Default: False boolean
    CRUISE_NUMBER: str
        Cruise number
        Default: None
    new: Boolean
        Whether the record(s) is being logged for the first time or not
        Influences whether we check whether id already registered
    firstrow: int
        Row number of first row in source data that includes data.
        If data are submitted from the GUI form, this should be 0 or not provided.
        If data are submitted from the Excel templates this should be 4.
    old_id: string
        If UUID has been updated using the GUI form, this is the ID previously used
        for that record. If ID has been changed, checking as if it is a new ID.
        Default = False, for use when submitting multiple records, e.g. from spreadsheet

    Returns
    ---------
    good: Boolean
        The result.
        True: pass
        False: fail
    errors: string
        String specifying where the errors were found
    """

    checker_list = make_valid_dict(DB, CRUISE_NUMBER)

    data = clean(data)

    if DB and CRUISE_NUMBER:
        registered_ids = get_all_ids(DB, CRUISE_NUMBER)
    else:
        registered_ids = []

    # Check the data array
    good, errors = check_array(data, checker_list, registered_ids, required, new, firstrow, old_id)

    g = True
    e = []
    if type(metadata) == pd.core.frame.DataFrame:
        metadata_checker_list = make_valid_dict_metadata(DB)
        g, e = check_meta(metadata, metadata_checker_list)

    good = good and g
    for ii in e:
        errors.append(ii)

    return good, errors

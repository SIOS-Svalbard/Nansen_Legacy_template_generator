#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 08:48:12 2022

@author: lukem
"""

'''
 -- This file is for defining the possible fields.
Each field is defined as a dictionary which should contain:
    name :       short name of field
    disp_name :  The displayed name of the field
    format:      uuid, int, text, time, date, double precision, boolean
    description: Description of the field
    grouping:    Categorising the fields so they can be grouped on the user interface, making it easier for the user to find what they are looking for.
                groups: ['Water',
                        'Species, Classifications and Counts',
                        'Comments',
                        'Sampling Protocol',
                        'Filtering and Volumes',
                        'File Details',
                        'Sediment',
                        'ID',
                        'Numbering',
                        'Coordinates',
                        'Storage',
                        'Timing',
                        'Cruise Details',
                        'Station',
                        'Sample Type/Intended Method',
                        'Instrumentation',
                        'Personnel',
                        'Record Details',
                        'Measurements, Facts, Descriptions',
                        'Ice',
                        'Ship']
    hstore:      Whether the field should be contained in an hstore column or serve as a standalone column.
                 The hstore columns are:
                    metadata (metadata describing the entire dataset, e.g. title, abstract, PI details)
                    other (any other column that is not provided for all or most events, therefore doesn't warrant it's own column)
                 Therefore, the following values are acceptable:
                    metadata
                    other
                    False
Optional fields are:
    width : int
            the width of the cell
    long_list: Boolean
            If the list wil exceed the Excel number of fields set this as true
    dwcid : str
            The Darwin core identifier (an url), if this is used the rest of the names should
            follow the Darwin core
    units : str
            The measurement unit of the variable, using the standard in CF
           Examples: 'm', 'm s-1', '
    inherit : Boolean
             Is this a variable that can be inherited by children?
             If it is not present its default is False
    inherit_weak : Boolean
             Only used if inherit is true. If set to True values already
             entered in the children will be kept.
             This is useful for instance in the case of multinets where the
             individual nets have different max and min depths.
             If it is not present its default is False
    valid : dict
            a dictionary with definitions of the validation for the cell, as
            per keywords used in Xlsxwriter
    cell_format :  dict
                   a dictionary with definitions of the format for the cell, as
                   per keywords in Xlsxwriter
'''

import datetime as dt


fields = [
    # ==============================================================================
    # ID fields
    # ==============================================================================

    {'name': 'id',
           'disp_name': 'ID',
           'description': '''A 36 character long universally unique ID (UUID) including 4 '-'.
Could be read in with a code reader.
If not provided, will be assigned automatically to each record.''',
           'width': 38,
           'format': 'uuid',
           'grouping': 'ID',
           'hstore': False,
           'valid': {
               'validate': 'length',
               'criteria': '==',
               'value': 36,
               'input_title': 'ID',
               'input_message': '''Should be a 36 character long universally unique ID (UUID) including 4 '-'.
Could be read in with a code reader.''',
               'error_title': 'Error',
               'error_message': "Needs to be a 36 characters long universally unique ID (UUID) including 4 '- '"
           }
           },
    {'name': 'parentID',
                 'disp_name': 'Parent ID',
                 'description': '''ID of the sample this subsample was taken from.
Should be a 36 characters long universally unique ID (UUID) including 4 '-'
Could be read in with a code reader.''',
                 'width': 38,
                 'format': 'uuid',
                 'grouping': 'ID',
                 'hstore': False,
                 'valid': {
                     'validate': 'length',
                     'criteria': '==',
                     'value': 36,
                     'input_title': 'Parent ID',
                     'input_message': '''ID of the sample this subsample was taken from.
Should be a 36 characters long universally unique ID (UUID) including 4 '-'
Could be read in with a code reader.''',
                     'error_title': 'Error',
                     'error_message': "Needs to be a 36 characters long universally unique ID (UUID) including 4 '- '"
                 }
                 },
    {'name': 'bottleNumber',
                'disp_name': 'Bottle Number',
                'description': '''The bottle number
Could be for instance the niskin bottle number.
Positive integer''',
                'inherit': True,
                'format': 'int',
                'grouping': 'Numbering',
                'hstore': False,
                'valid': {
                    'validate': 'integer',
                    'criteria': '>',
                    'value': 0,
                    'input_title': 'Bottle Number',
                    'input_message': '''The bottle number
Could be for instance the niskin bottle number.
Positive integer''',
                    'error_title': 'Error',
                    'error_message': 'Integer > 0'
                }
                },
    # ==============================================================================
    # Cruise Details - all in metadata hstore
    # ==============================================================================
    # {'name': 'cruiseNumber',
    #             'disp_name': 'Cruise number',
    #             'description': 'A number that can be used to uniquely identify each cruise',
    #             'inherit': True,
    #             'format': 'int',
    #             'grouping': 'Cruise Details',
    #             'hstore': False,
    #             'valid': {
    #                 'validate': 'any'}
    #             },
    # {'name': 'cruiseName',
    #             'disp_name': 'Cruise name',
    #             'description': 'Full name of the cruise',
    #             'inherit': True,
    #             'format': 'text',
    #             'grouping': 'Cruise Details',
    #             'hstore': False,
    #             'valid': {
    #                 'validate': 'any'}
    #             },
    # {'name': 'projectName',
    #             'disp_name': 'Project name',
    #             'description': 'Full name of the project',
    #             'inherit': True,
    #             'format': 'text',
    #             'grouping': 'Cruise Details',
    #             'hstore': False,
    #             'valid': {
    #                 'validate': 'any'}
    #             },
    # {'name': 'vesselName',
    #             'disp_name': 'Vessel name',
    #             'description': 'Full name of the vessel',
    #             'inherit': True,
    #             'format': 'text',
    #             'grouping': 'Cruise Details',
    #             'hstore': False,
    #             'valid': {
    #                 'validate': 'any'}
    #             },

    # ==============================================================================
    # Timestamps
    # ==============================================================================
    {'name': 'middleDate',
             'disp_name': 'Middle Date (UTC)',
             'description': '''Middle date for event, for instance for noting the deepest point of a trawl or net haul.
Should be in ISO8601 format, in UTC time, e.g. 2022-04-10''',
             'inherit': True,
             'format': 'date',
             'grouping': 'Timing',
             'hstore': 'other',
             'width': 12,
             'valid': {
                 'validate': 'date',
                 'criteria': 'between',
                 'minimum': dt.date(2000, 1, 1),
                 'maximum': '=TODAY()+2',
                 'input_title': 'Start Date',
                 'input_message': '''Middle date for event, for instance for noting the deepest point of a trawl or net haul.
Should be in ISO8601 format, in UTC time, e.g. 2022-04-10T09:46:24Z''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid date [2000-01-01, today + 2]'
             },
             'cell_format': {
                 'num_format': 'yyyy-mm-dd'
             }
             },
    {'name': 'middleTime',
             'disp_name': 'Middle Time (UTC)',
             'description': '''Middle time for event, for instance for noting the deepest point of a trawl or net haul.
Should be in ISO8601 format, in UTC time, e.g. 09:46:24Z''',
             'inherit': True,
             'format': 'time',
             'grouping': 'Timing',
             'hstore': 'other',
             'width': 12,
             'valid': {
                 'validate': 'time',
                 'criteria': 'between',
                 'minimum': 0,  # Time in decimal days
                 'maximum': 0.9999999,  # Time in decimal days
                 'input_title': 'Start Date',
                 'input_message': '''Middle time for event, for instance for noting the deepest point of a trawl or net haul.
Should be in ISO8601 format, in UTC time, e.g. 09:46:24Z''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid date [2000-01-01, today + 2]'
             },
             'cell_format': {
                 'num_format': 'yyyy-mm-dd'
             }
             },
    {'name': 'endDate',
             'disp_name': 'End Date (UTC)',
             'description': '''Date of the end of the collection event period,
Should be in ISO8601 format, in UTC time, e.g. 2022-04-10''',
             'inherit': True,
             'format': 'date',
             'grouping': 'Timing',
             'hstore': False,
             'width': 12,
             'valid': {
                 'validate': 'date',
                 'criteria': 'between',
                 'minimum': dt.date(2000, 1, 1),
                 'maximum': '=TODAY()+2',
                 'input_title': 'End Date',
                 'input_message': '''Date of the end of the collection event period, in UTC time, e.g. 2022-04-10''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid date [2000-01-01, today + 2]'
             },
             'cell_format': {
                 'num_format': 'yyyy-mm-dd'
             }
             },
    {'name': 'endTime',
             'disp_name': 'End Time (UTC)',
             'description': '''Time of the end of the collection event period,
Should be in ISO8601 format, in UTC time, e.g. 09:46:24Z''',
             'inherit': True,
             'format': 'time',
             'grouping': 'Timing',
             'hstore': False,
             'width': 13,
             'dwcid': 'http://rs.tdwg.org/dwc/terms/eventTime',
             'valid': {
                 'validate': 'time',
                 'criteria': 'between',
                 'minimum': 0,  # Time in decimal days
                 'maximum': 0.9999999,  # Time in decimal days
                 'input_title': 'End Time (UTC)',
                 'input_message': '''
The time in UTC
Format is HH:MM
If MM > 59, HH will be HH + 1 ''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid time'
             },
             'cell_format': {
                 'num_format': 'hh:mm'
             }
             },

    # ==============================================================================
    # Coordinates
    # ==============================================================================
    {'name': 'endDecimalLatitude',
                      'disp_name': 'End Decimal Latitude',
                      'description': '''Latitude in decimal degrees at the end of the sampling period.
   Northern hemisphere is positive.
   Example: 78.1500''',
                      'inherit': True,
                      'format': 'double precision',
                      'grouping': 'Coordinates',
                      'hstore': False,
                      'units': 'degrees_north',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': 'between',
                          'minimum': -90,
                          'maximum': 90,
                          'input_title': 'End Decimal Latitude',
                          'input_message': '''Latitude in decimal degrees.
This is for use with for instance trawls and nets.
Northern hemisphere is positive.
Example: 78.1500''',
                          'error_title': 'Error',
                          'error_message': 'Not in range [-90, 90]'
                      },
                      'cell_format': {
                          'num_format': '0.0000'
                      }
                      },
    {'name': 'endDecimalLongitude',
                       'disp_name': 'End Decimal Longitude',
                       'description': '''Longitude in decimal degrees at the end of the sampling period.
   East of Greenwich (0) is positive.
   Example: 15.0012''',
                       'inherit': True,
                       'format': 'double precision',
                       'grouping': 'Coordinates',
                       'hstore': False,
                       'units': 'degree_east',
                       'valid': {
                           'validate': 'decimal',
                           'criteria': 'between',
                           'minimum': -180,
                           'maximum': 180,
                           'input_title': 'End Decimal Longitude',
                           'input_message': '''Longitude in decimal degrees.
This is for use with for instance trawls and nets.
East of Greenwich (0) is positive.
Example: 15.0012''',
                           'error_title': 'Error',
                           'error_message': 'Not in range [-180, 180]'
                       },
                       'cell_format': {
                           'num_format': '0.0000'
                       }
                       },
    {'name': 'middleDecimalLatitude',
                         'disp_name': 'Middle Decimal Latitude',
                         'description': '''Latitude in decimal degrees.
This is for use with for instance trawls and nets and denotes the depest point.
Northern hemisphere is positive.
Example: 78.1500''',
                         'inherit': True,
                         'format': 'double precision',
                         'grouping': 'Coordinates',
                         'hstore': 'other',
                         'units': 'degrees_north',
                         'valid': {
                             'validate': 'decimal',
                             'criteria': 'between',
                             'minimum': -90,
                             'maximum': 90,
                             'input_title': 'Middle Decimal Latitude',
                             'input_message': '''Latitude in decimal degrees.
This is for use with for instance trawls and nets and denotes the depest point.
Northern hemisphere is positive.
Example: 78.1500''',
                             'error_title': 'Error',
                             'error_message': 'Not in range [-90, 90]'
                         },
                         'cell_format': {
                             'num_format': '0.0000'
                         }
                         },
    {'name': 'middleDecimalLongitude',
                          'disp_name': 'Middle Decimal Longitude',
                          'description': '''Longitude in decimal degrees.
This is for use with for instance trawls and nets and denotes the depest point.
East of Greenwich (0) is positive.
Example: 15.0012''',
                          'inherit': True,
                          'format': 'double precision',
                          'grouping': 'Coordinates',
                          'hstore': 'other',
                          'units': 'degree_east',
                          'valid': {
                              'validate': 'decimal',
                              'criteria': 'between',
                              'minimum': -180,
                              'maximum': 180,
                              'input_title': 'Middle Decimal Longitude',
                              'input_message': '''Longitude in decimal degrees.
This is for use with for instance trawls and nets and denotes the depest point.
East of Greenwich (0) is positive.
Example: 15.0012''',
                              'error_title': 'Error',
                              'error_message': 'Not in range [-180, 180]'
                          },
                          'cell_format': {
                              'num_format': '0.0000'
                          }
                          },

    # ==============================================================================
    # Station details
    # ==============================================================================
    {'name': 'statID',
          'disp_name': 'Local Station ID',
          'description': 'This ID is a running series (per gear) for each samling event and is found in the cruise logger.',
          'inherit': True,
          'width': 13,
          'format': 'int',
          'grouping': 'Station',
          'hstore': False,
          'valid': {
              'validate': 'any',
              'input_title': 'Local Station ID',
              'input_message': '''This ID is a running series (per gear) for each samling event and is found in the cruise logger.
'''
          }
          },
    {'name': 'stationName',
               'disp_name': 'Station Name',
               'description': 'The full name of the station. e.g. P1 (NLEG01)',
               'inherit': True,
               'width': 13,
               'format': 'text',
               'grouping': 'Station',
               'hstore': False,
               'long_list': True,
               'valid': {
                   'validate': 'list',
                   'source': 'stations',
                   'input_title': 'Station Name',
                   'input_message': '''The full name of the station. e.g. P1 (NLEG01)''',
                   'error_title': 'Error',
                   'error_message': 'Not a valid value, pick a value from the drop-down list.'
               }
               },

    # ==============================================================================
    # Ship
    # ==============================================================================
    {'name': 'shipSpeedInMetersPerSecond',
                              'disp_name': 'Ship Speed (m/s)',
                              'description': '''The speed of the ship in meters per second.
Decimal number >=0.''',
                              'inherit': True,
                              'format': 'double precision',
                              'grouping': 'Ship',
                              'hstore': 'other',
                              'units': 'm/s',
                              'valid': {
                                  'validate': 'decimal',
                                  'criteria': '>=',
                                  'value': 0,
                                  'input_title': 'Ship Speed (m/s)',
                                  'input_message': '''The speed of the ship in meters per second.
Decimal number >=0.''',
                                  'error_title': 'Error',
                                  'error_message': 'Float >= 0'
                              }
                              },

    # ==============================================================================
    # Paleo
    # ==============================================================================
    {'name': 'sedimentCoreLengthInMeters',
                              'disp_name': 'Sediment Core Length (m)',
                              'description': 'The total sediment core length decimal in meters.',
                              'units': 'm',
                              'format': 'double precision',
                              'grouping': 'Sediment',
                              'hstore': 'other',
                              'valid': {
                                  'validate': 'decimal',
                                  'criteria': '>=',
                                  'value': 0,
                                  'input_title': 'Sediment Core Length (m)',
                                  'input_message': '''The total sediment core length decimal in meters.''',
                                  'error_title': 'Error',
                                  'error_message': 'Float >= 0'
                              }
                              },
    {'name': 'sedimentCoreMaximumDepthInCentiMeters',
                                         'disp_name': 'Sediment Core Maximum Depth (cm)',
                                         'description': '''The sediment core maximum depth in centimeters.
This is measured from the top of the core.
Maximum for multicores is 60 cm
Maximum for gravity and piston cores is 3 000 cm.''',
                                         'units': 'cm',
                                         'format': 'double precision',
                                         'grouping': 'Sediment',
                                         'hstore': 'other',
                                         'valid': {
                                             'validate': 'decimal',
                                             'criteria': 'between',
                                             'minimum': 0,
                                             'maximum': 3000,
                                             'input_title': 'Sediment Core Maximum Depth (m)',
                                             'input_message': '''The sediment core maximum depth in centimeters.
This is measured from the top of the core.
Maximum for multicores is 60 cm
Maximum for gravity and piston cores is 3 000 cm.''',
                                             'error_title': 'Error',
                                             'error_message': 'Float[0, 3 000]'
                                         }
                                         },
    {'name': 'sedimentCoreMinimumDepthInCentiMeters',
                                         'disp_name': 'Sediment Core Minimum Depth (cm)',
                                         'description': '''The sediment core minimum depth in centimeters.
This is measured from the top of the core.''',
                                         'units': 'cm',
                                         'format': 'double precision',
                                         'grouping': 'Sediment',
                                         'hstore': 'other',
                                         'valid': {
                                             'validate': 'decimal',
                                             'criteria': 'between',
                                             'minimum': 0,
                                             'maximum': 3000,
                                             'input_title': 'Sediment Core Minimum Depth (m)',
                                             'input_message': '''The sediment core minimum depth in centimeters.
This is measured from the top of the core.''',
                                             'error_title': 'Error',
                                             'error_message': 'Float[0, 3 000]'
                                         }
                                         },

    # ==============================================================================
    # Strings
    # ==============================================================================
    {'name': 'colour',
            'disp_name': 'Colour',
            'description': 'Colour of the sample or specimen',
            'format': 'text',
            'grouping': 'Measurements, Facts, Descriptions',
            'hstore': 'other',
            'valid': {
                'validate': 'any',
                'input_title': 'Colour',
                'input_message': 'Colour'
            }
            },
    {'name': 'smell',
            'disp_name': 'Smell',
            'description': 'A descriptive word or term for the smell of the sample or specimen',
            'format': 'text',
            'grouping': 'Measurements, Facts, Descriptions',
            'hstore': 'other',
            'valid': {
                'validate': 'any',
                'input_title': 'Smell',
                'input_message': 'Smell'
            }
            },

    # ==============================================================================
    # Personnel
    # ==============================================================================
    {'name': 'recordedBy_name',
              'disp_name': 'Recorded By (Name)',
              'description': '''Full name of who has recorded/analysed the data.
Can be a concatenated list, separated by: '|'
Example: John Doe | Ola Nordmann''',
              'dwcid': 'http://rs.tdwg.org/dwc/terms/recordedBy',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'valid': {
                  'validate': 'any',
                  'input_title': 'Recorded By',
                  'input_message': '''Full name of who has recorded/analysed the data.
Can be a concatenated list, separated by: '|'
Example: John Doe | Ola Nordmann'''
              }
              },
    {'name': 'recordedBy_email',
              'disp_name': 'Recorded By (Email)',
              'description': '''Email of who has recorded/analysed the data.
Can be a concatenated list, separated by: '|'
Example: johnd@unis.no | olan@unis.no''',
              'dwcid': 'http://rs.tdwg.org/dwc/terms/recordedBy',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'valid': {
                  'validate': 'any',
                  'input_title': 'Recorded By (Email)',
                  'input_message': '''Email of who has recorded/analysed the data.
Can be a concatenated list, separated by: '|'
Example: johnd@unis.no | olan@unis.no'''
              }
              },
    {'name': 'recordedBy_orcid',
              'disp_name': 'Recorded By (OrcID)',
              'description': '''OrcID(s) of who has recorded/analysed the data.
Can be a concatenated list, separated by: '|'
Example: https://orcid.org/0000-0002-9746-544X''',
              'dwcid': 'http://rs.tdwg.org/dwc/terms/recordedBy',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'valid': {
                  'validate': 'any',
                  'input_title': 'Recorded By (OrcID)',
                  'input_message': '''OrcID(s) of who has recorded/analysed the data.
    Can be a concatenated list, separated by: '|'
    Example: https://orcid.org/0000-0002-9746-544X'''
              }
              },
    {'name': 'recordedBy_institution',
              'disp_name': 'Recorded By (Institution)',
              'description': '''Institution of who has recorded/analysed the data.
Can be a concatenated list, separated by: '|'. Please include for everyone listed, even if some are from the same institution.
Example: University Centre in Svalbard | University Centre in Svalbard''',
              'dwcid': 'http://rs.tdwg.org/dwc/terms/recordedBy',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'valid': {
                  'validate': 'any',
                  'input_title': 'Recorded By',
                  'input_message': '''Institution of who has recorded/analysed the data.
Can be a concatenated list, separated by: '|'. Please include for everyone listed, even if some are from the same institution.
Example: University Centre in Svalbard | University Centre in Svalbard'''
              }
              },
    {'name': 'recordedBy_details',
              'disp_name': 'Recorded By',
              'description': '''Details of who has recorded/analysed the data.
Should ideally include full name and email, e.g. Luke Marsden (lukem@unis.no).
Can be a concatenated list, separated by: '|'.''',
              'dwcid': 'http://rs.tdwg.org/dwc/terms/recordedBy',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'long_list': True,
              'valid': {
                  'validate': 'list',
                  'source': 'personnel',
                  'error_title': 'Error',
                  'error_message': 'Not a valid value, pick a value from the drop-down list.',
                  'input_title': 'Recorded By',
                  'input_message': '''Details of who has recorded/analysed the data.
    Should ideally include full name and email, e.g. Luke Marsden (lukem@unis.no).
    Can be a concatenated list, separated by: '|'.''',

              }
              },
    # FROM TABLE, LINK TO EMAIL AND INSTITUTION AUTOMATICALLY. WHAT ABOUT WHEN PI CHANGES INSTITUTION?
    {'name': 'pi_name',
              'disp_name': 'PI name',
              'description': '''Full name of the principal investigator of the data.
Can be a concatenated list, separated by: '|'
Example: John Doe | Ola Nordmann''',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'valid': {
                  'validate': 'any',
                  'input_title': 'PI name',
                  'input_message': '''Full name of the principal investigator of the data.
Can be a concatenated list, separated by: '|'
Example: John Doe | Ola Nordmann'''
              }
              },
    {'name': 'pi_email',
              'disp_name': 'PI email',
              'description': '''Email of the principal investigator of the data.
Can be a concatenated list, separated by: '|'
Please include for every PI listed.
Example: john.doe@unis.no | ola.nordmann@unis.no''',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'valid': {
                  'validate': 'any',
                  'input_title': 'PI email',
                  'input_message': '''Email of the principal investigator of the data.
Can be a concatenated list, separated by: '|'
Please include for every PI listed.
Example: john.doe@unis.no | ola.nordmann@unis.no'''
              }
              },
    {'name': 'pi_institution',
              'disp_name': 'PI institution',
              'description': '''Main institution of the principal investigator of the data.
Please include for every PI listed, even if the same.
Example: University Centre in Svalbard | University Centre in Svalbard''',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'valid': {
                  'validate': 'any',
                  'input_title': 'PI institution',
                  'input_message': '''Main institution of the principal investigator of the data.
Please include for every PI listed, even if the same.
Example: University Centre in Svalbard | University Centre in Svalbard'''
              }
              },
    {'name': 'pi_orcid',
              'disp_name': 'PI OrcID',
              'description': '''OrcID of the principal investigator(s) of the data.
Please include for every PI listed. Example: https://orcid.org/0000-0002-9746-544X''',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'valid': {
                  'validate': 'any',
                  'input_title': 'PI OrcID',
                  'input_message': '''OrcID of the principal investigator(s) of the data.
    Please include for every PI listed.  Example: https://orcid.org/0000-0002-9746-544X'''
              }
              },
    {'name': 'pi_details',
              'disp_name': 'PI Details',
              'description': '''Details of the principal investigator of the data.
Should ideally include full name and email, e.g. Luke Marsden (lukem@unis.no).
Can be a concatenated list, separated by: '|'
''',
              'format': 'text',
              'grouping': 'Personnel',
              'hstore': False,
              'long_list': True,
              'valid': {
                  'validate': 'list',
                  'source': 'personnel',
                  'input_title': 'PI Details',
                  'input_message': '''Details of the principal investigator of the data.
    Should ideally include full name and email, e.g. Luke Marsden (lukem@unis.no).
    Can be a concatenated list, separated by: '|'
    ''',
                  'error_title': 'Error',
                  'error_message': 'Not a valid value, pick a value from the drop-down list.'
              }
              },

    # ==============================================================================
    # Storage
    # ==============================================================================
    # Dropdown
    {'name': 'storageTemp',
               'disp_name': 'Storage temp',
               'description': 'Choose the storage temperature used',
               'format': 'text',
               'grouping': 'Storage',
               'hstore': 'other',
               'width': 15,
               'long_list': True,
               'valid': {
                   'validate': 'list',
                   'source': 'storage_temperatures',
                   'input_title': 'Storage temperature',
                   'input_message': '''Choose the storage temperature used''',
                   'error_title': 'Error',
                   'error_message': 'Not a valid value, pick a value from the drop-down list.'
               }
               },
    {'name': 'fixative',
            'disp_name': 'Fixative',
            'description': 'Fixative used for sample',
            'format': 'text',
            'grouping': 'Storage',
            'hstore': 'other',
            'valid': {
                'validate': 'any',
                'input_title': 'Fixative',
                'input_message': '''Fixative used for sample '''
            }
            },
    # RETHINK. DEFAULT VALUE FOR NO PHYSICAL SAMPLE PRESERVED?
    {'name': 'sampleLocation',
                  'disp_name': 'Sample Location',
                  'description': '''The long-term storage location onshore, immediately after the cruise.
This could for instance be an institution or something more specific.''',
                  'format': 'text',
                  'grouping': 'Storage',
                  'hstore': False,
                  'valid': {
                      'validate': 'any',
                      'input_title': 'Sample Location',
                      'input_message': '''The long-term storage location onshore, immediately after the cruise.
This could for instance be an institution or something more specific.'''
                  }
                  },
    {'name': 'dilution_factor',
                   'disp_name': 'Dilution factor',
                   'description': 'Factor by which the sample has been diluted by',
                   'format': 'double precision',
                   'grouping': 'Filtering and Volumes',
                   'hstore': 'other',
                   'width': 20,
                   'valid': {
                       'validate': 'decimal',
                       'criteria': '>',
                       'value': 0,
                       'input_title': 'Dilution factor',
                       'input_message': '''Positive integer''',
                       'error_title': 'Error',
                       'error_message': 'Integer > 0'
                   }
                   },
    {'name': 'sample_owner',
              'disp_name': 'Sample Owner',
              'description': 'Person or institution who owns the sample',
              'format': 'text',
              'grouping': 'Storage',
              'hstore': 'other',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Sample Owner',
                  'input_message': '''Person who owns the sample'''
              }
              },

    # ==============================================================================
    # Filtering
    # ==============================================================================
    {'name': 'filter',
          'disp_name': 'Filter',
          'description': '''Choose the filter used.
If no filtering is being done choose None''',
          'format': 'text',
          'grouping': 'Filtering and Volumes',
          'hstore': 'other',
          'width': 15,
          'long_list': True,
          'valid': {
              'validate': 'list',
              'source': 'filters',
              'input_title': 'Filter',
              'input_message': '''Choose the filter used. If no filtering is being done choose None''',
              'error_title': 'Error',
              'error_message': 'Not a valid value, pick a value from the drop-down list.'
          }
          },
    {'name': 'filteredVolumeInMilliliters',
                               'disp_name': 'Filtered volume (mL)',
                               'description': 'Filtered volume in decimal millilitres',
                               'format': 'double precision',
                               'grouping': 'Filtering and Volumes',
                               'hstore': 'other',
                               'valid': {
                                   'validate': 'decimal',
                                   'criteria': '>',
                                   'value': 0,
                                   'input_title': 'Filtered volume (mL)',
                                   'input_message': '''Filtered volume in decimal millilitres''',
                                   'error_title': 'Error',
                                   'error_message': 'Decimal > 0'
                               }
                               },
    {'name': 'methanol_vol',
                'disp_name': 'Methanol volume (mL)',
                'description': 'Volume of methanol used in millilitres',
                'format': 'double precision',
                'grouping': 'Filtering and Volumes',
                'hstore': 'other',
                'units': 'mL',
                'valid': {
                    'validate': 'decimal',
                    'criteria': '>',
                    'value': 0,
                    'input_title': 'Methanol volume (mL)',
                    'input_message': '''Volume of methanol used in millilitres''',
                    'error_title': 'Error',
                    'error_message': 'Decimal > 0'
                }
                },
    {'name': 'sampleVolumeInMilliliters',
                             'disp_name': 'Sample volume (mL)',
                             'description': 'Sample volume in millilitres',
                             'format': 'double precision',
                             'grouping': 'Filtering and Volumes',
                             'hstore': 'other',
                             'units': 'mL',
                             'valid': {
                                 'validate': 'decimal',
                                 'criteria': '>',
                                 'value': 0,
                                 'input_title': 'Sample volume (mL)',
                                 'input_message': '''Sample volume in millilitres''',
                                 'error_title': 'Error',
                                 'error_message': 'Decimal > 0'
                             }
                             },
    {'name': 'subsample_vol',
                 'disp_name': 'Subsample volume (mL)',
                 'description': 'Subsample volume in millilitres',
                 'units': 'mL',
                 'format': 'double precision',
                 'grouping': 'Filtering and Volumes',
                 'hstore': 'other',
                 'valid': {
                     'validate': 'decimal',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Subsample volume (mL)',
                     'input_message': '''Subsample volume in millilitres''',
                     'error_title': 'Error',
                     'error_message': 'Decimal > 0'
                 }
                 },
    # ==============================================================================
    # Probable MeasurementOrFact types from Darwin Core
    # ==============================================================================
    {'name': 'weightInGrams',
                 'disp_name': 'Weight (g)',
                 'description': 'Weight of the sample or specimen in grams',
                 'format': 'double precision',
                 'grouping': 'Measurements, Facts, Descriptions',
                 'hstore': 'other',
                 'units': 'g',
                 'valid': {
                     'validate': 'decimal',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Weight in grams (g)',
                     'input_message': '''Weight in grams''',
                     'error_title': 'Error',
                     'error_message': 'Float > 0'
                 }
                 },
    {'name': 'gonadWeightInGrams',
                      'disp_name': 'Gonad Weight (g)',
                      'description': 'Wet weight of the gonad in in grams',
                      'format': 'double precision',
                      'grouping': 'Measurements, Facts, Descriptions',
                      'hstore': 'other',
                      'units': 'g',
                      #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Gonad Weight in grams (g)',
                          'input_message': '''Wet weight of the gonad in in grams''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      },
    {'name': 'liverWeightInGrams',
                      'disp_name': 'Liver Weight (g)',
                      'description': 'Wet weight of the liver in in grams',
                      'format': 'double precision',
                      'grouping': 'Measurements, Facts, Descriptions',
                      'hstore': 'other',
                      'units': 'g',
                      #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Liver Weight in grams (g)',
                          'input_message': '''Wet weight of the liver in in grams''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      },
    {'name': 'somaticWeightInGrams',
                        'disp_name': 'Somatic Weight (g)',
                        'description': 'Wet weight of the fish when all inner organs are removed from the fish gonad in in grams',
                        'format': 'double precision',
                        'grouping': 'Measurements, Facts, Descriptions',
                        'hstore': 'other',
                        'units': 'g',
                        #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>',
                            'value': 0,
                            'input_title': 'Somatic Weight in grams (g)',
                            'input_message': '''Wet weight of the fish when all inner organs are removed from the fish gonad in in grams''',
                            'error_title': 'Error',
                            'error_message': 'Float > 0'
                        }
                        },
    {'name': 'forkLengthInMeters',
                      'disp_name': 'Fork lenght (cm)',
                      'description': '''The length of a fish measured from the most anterior part of the head to the deepest point of the notch in the tail fin in cm.
Positive decimal number''',
                      'format': 'double precision',
                      'grouping': 'Measurements, Facts, Descriptions',
                      'hstore': 'other',
                      'units': 'cm',
                      #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Fork lenght (cm)',
                          'input_message': '''The length of a fish measured from the most anterior part of the head to the deepest point of the notch in the tail fin in cm.
Positive decimal number''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      },
    {'name': 'maturationStage',
                   'disp_name': 'Maturation Stage',
                   'description': '''On the basis of shape, size, color of the gonads and other morphological featuers, at least six maturity stages can be recongnized
Value in range [0, 7]''',
                   'format': 'int',
                   'grouping': 'Measurements, Facts, Descriptions',
                   'hstore': 'other',
                   'units': '1',
                   'valid': {
                       'validate': 'integer',
                       'criteria': 'between',
                       'minimum': 0,
                       'maximum': 7,
                       'input_title': 'Maturation Stage',
                       'input_message': '''On the basis of shape, size, color of the gonads and other morphological featuers, at least six maturity stages can be recongnized
Value in range [0, 7]''',
                       'error_title': 'Error',
                       'error_message': 'Int range [0, 7]'
                   }
                   },
    {'name': 'ectoparasites',
                 'disp_name': 'Ectoparasites',
                 'description': '''Number of ectoparasites visible on the fins and gills of the fish
Integer >= 0''',
                 'format': 'int',
                 'grouping': 'Measurements, Facts, Descriptions',
                 'hstore': 'other',
                 'units': '1',
                 'valid': {
                     'validate': 'integer',
                     'criteria': '>=',
                     'value': 0,
                     'input_title': 'Ectoparasites',
                     'input_message': '''Number of ectoparasites visible on the fins and gills of the fish
Integer >= 0''',
                     'error_title': 'Error',
                     'error_message': 'Int range [0, 7]' # is this right?
                 }
                 },
    {'name': 'endoparasites',
                 'disp_name': 'Endoparasites',
                 'description': '''Number of endoparasites visible in the body cavity of the fish
Integer >= 0''',
                 'format': 'int',
                 'grouping': 'Measurements, Facts, Descriptions',
                 'hstore': 'other',
                 'units': '1',
                 'valid': {
                     'validate': 'integer',
                     'criteria': '>=',
                     'value': 0,
                     'input_title': 'Endoparasites',
                     'input_message': '''Number of endoparasites visible in the body cavity of the fish
Integer >= 0''',
                     'error_title': 'Error',
                     'error_message': 'Int range [0, 7]'
                 }
                 },

    # ==============================================================================
    # Physical properties and physical oceanography things
    # ==============================================================================
    {'name': 'seaIceCoreType',
                  'disp_name': 'Sea Ice Core Type',
                  'description': 'The analysis the sea ice core is intended for',
                  'format': 'text',
                  'grouping': 'Ice',
                  'hstore': 'other',
                  'valid': {
                      'validate': 'any',
                      'input_title': 'Sea Ice Core Type',
                      'input_message': 'The analysis the sea ice core is intended for'
                  }
                  },
    {'name': 'seaIceCoreLengthInCentimeters',
                            'disp_name': 'Sea Ice Core Length (cm)',
                            'description': '''Sea ice core length in decimal centimeters.
Float number larger than 0 ''',
                            'units': 'cm',
                            'format': 'double precision',
                            'grouping': 'Ice',
                            'hstore': 'other',
                            'valid': {
                                'validate': 'decimal',
                                'criteria': '>',
                                'value': 0,
                                'input_title': 'Sea Ice Core length (cm)',
                                'input_message': '''Sea ice core length in decimal centimeters.
 Float number larger than 0 ''',
                                'error_title': 'Error',
                                'error_message': 'Float > 0'
                            }
                            },
    {'name': 'seaIceMeltpondTemperatureInCelsius',
                                       'disp_name': 'Sea Ice Meltpond Temperature (C)',
                                       'description': '''Sea ice meltpond temperature in Celsius.
Float number larger than -10 ''',
                                       'units': 'Celsius',
                                       'format': 'double precision',
                                       'grouping': 'Ice',
                                       'hstore': 'other',
                                       'valid': {
                                           'validate': 'decimal',
                                           'criteria': '>',
                                           'value': -10,
                                           'input_title': 'Sea Ice Meltpond Temperature (C)',
                                           'input_message': '''Sea ice meltpond temperature in Celsius.
 Float number larger than -10 ''',
                                           'error_title': 'Error',
                                           'error:message': 'Float > -10'
                                       }
                                       },
    {'name': 'seaIceMeltpondSalinity',
                          'disp_name': 'Sea Ice Meltpond Salinity (1e-3)',
                          'description': '''Sea ice meltpond salinity in parts per thousand
Often using the Practical Salinity Scale of 1978
Float number larger than or equal to 0
Example: 0.029''',
                          'units': '1e-3',
                          'format': 'double precision',
                          'grouping': 'Ice',
                          'hstore': 'other',
                          'valid': {
                              'validate': 'decimal',
                              'criteria': '>=',
                              'value': 0,
                              'input_title': 'Sea Ice Meltpond Salinity',
                              'input_message': '''Sea ice meltpond salinity in parts per thousand
Often using the Practical Salinity Scale of 1978
Float number larger than or equal to 0
Example: 0.029''',
                              'error_title': 'Error',
                              'error_message': 'Float >= 0'
                          }
                          },
    {'name': 'sedimentPH',
              'disp_name': 'Sediment pH  (total scale)',
              'description': '''
Is the measure of acidity of seawater, defined as the negative logarithm of
the concentration of dissolved hydrogen ions plus bisulfate ions in a sea water
medium; it can be measured or calculated; when measured the scale is defined
according to a series of buffers prepared in artificial seawater containing
bisulfate.
Float in range [-2, 16]''',
              'format': 'double precision',
              'hstore': 'other',
              'grouping': 'Sediment',
              'units': '1',
              'valid': {
                  'validate': 'decimal',
                  'criteria': 'between',
                  'minimum': -2,
                  'maximum': 16,
                  'input_title': 'Sediment  pH  (total scale)',
                  'input_message': '''
Is the measure of acidity of seawater, defined as the negative logarithm of
the concentration of dissolved hydrogen ions plus bisulfate ions in a sea water
medium; it can be measured or calculated; when measured the scale is defined
according to a series of buffers prepared in artificial seawater containing
bisulfate.
Float in range [-2, 16]''',
                  'error_title': 'Error',
                  'error_message': 'Not in range [-2, 16]'
              }
              },
    {'name': 'benthicRespiration',
                      'disp_name': 'Benthic Respiration (mmol/m^2)',
                      'description': '''
Benthic respiration of Oxygen in millimole per square meter
Positive float number''',
                      'format': 'double precision',
                      'grouping': 'Sediment',
                      'hstore': 'other',
                      'units': 'mmol m-2',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>=',
                          'value': 0,
                          'input_title': 'Benthic Respiration (mmol/m^2)',
                          'input_message': '''
Benthic respiration of Oxygen in millimole per square meter
Positive float number''',
                          'error_title': 'Error',
                          'error_message': 'Float >= 0'
                      }
                      },
    {'name': 'seaIceTotalDIC',
                  'disp_name': 'Ice DIC (umol/kg)',
                  'description': '''
Sea Ice Total dissolved inorganic carbon in umol per kg
Positive float number''',
                  'format': 'double precision',
                  'grouping': 'Ice',
                  'hstore': 'other',
                  'units': 'umol kg-1',
                  'valid': {
                      'validate': 'decimal',
                      'criteria': '>=',
                      'value': 0,
                      'input_title': 'Sea Ice DIC (umol/kg)',
                      'input_message': '''
Sea Ice Total dissolved inorganic carbon in umol per kg
Positive float number''',
                      'error_title': 'Error',
                      'error_message': 'Float >= 0'
                  }
                  },
    {'name': 'seaWaterDeltaO18',
                    'disp_name': 'Sea delta-O-18 (1e-3)',
                    'description': '''
Sea Water delta-O-18 in parts per thousand
Positive float number''',
                    'format': 'double precision',
                    'grouping': 'Water',
                    'hstore': 'other',
                    'units': '1e-3',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': '>=',
                        'value': 0,
                        'input_title': 'Sea Water delta-O-18 (1e-3)',
                        'input_message': '''
Sea Water delta-O-18 in parts per thousand
Positive float number''',
                        'error_title': 'Error',
                        'error_message': 'Float >= 0'
                    }
                    },
    {'name': 'seaIceDeltaO18',
                  'disp_name': 'Ice delta-O-18 (1e-3)',
                  'description': '''
Sea Ice delta-O-18 in parts per thousand
Positive float number''',
                  'format': 'double precision',
                  'grouping': 'Ice',
                  'hstore': 'other',
                  'units': '1e-3',
                  'valid': {
                      'validate': 'decimal',
                      'criteria': '>=',
                      'value': 0,
                      'input_title': 'Sea Ice delta-O-18 (1e-3)',
                      'input_message': '''
Sea Ice delta-O-18 in parts per thousand
Positive float number''',
                      'error_title': 'Error',
                      'error_message': 'Float >= 0'
                  }
                  },
    {'name': 'seaWaterAlkalinity',
                      'disp_name': 'Total Alkalinity (umol/kg)',
                      'description': '''
Sea Water Total Alkalinity in micromols per kilogram
Positive float number''',
                      'format': 'double precision',
                      'grouping': 'Water',
                      'hstore': 'other',
                      'units': 'umol kg-1',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>=',
                          'value': 0,
                          'input_title': 'Sea Water Total Alkalinity (umol/kg)',
                          'input_message': '''
Sea Water Total Alkalinity in micromols per kilogram
Positive float number''',
                          'error_title': 'Error',
                          'error_message': 'Float >= 0'
                      }
                      },

    # ==============================================================================
    # Sample details
    # ==============================================================================
    {'name': 'sampleType',
              'disp_name': 'Sample Type',
              'description': '''Choose the sample type.
Listed at: https://github.com/SIOS-Svalbard/AeN_doc/blob/master/list_sample_types.csv''',
              'long_list': True,
              'format': 'text',
              'grouping': 'Sample Type/Intended Method',
              'hstore': False,
              'valid': {
                  'validate': 'list',
                  'source': 'sample_types',
                  'input_title': 'Sample type',
                  'input_message': '''Choose the sample type.
Listed at: https://github.com/SIOS-Svalbard/AeN_doc/blob/master/list_sample_types.csv''',
                  'error_title': 'Error',
                  'error_message': 'Not a valid value, pick a value from the drop-down list.'
              }
              },
    # THIS SHOULD BECOME A MORE IMPORTANT TERM IN V2, AND MOST OF THE TERMS IN SAMPLE TYPE SHOULD BE MOVED TO INTENDED METHOD. MAKE REQUIRED TERM FOR SAMPLES.
    {'name': 'intendedMethod',
                  'disp_name': 'Intended Method',
                  'description': '''The intended measurement or analysis method for the sample.
If multiple methods, separate with ';'.
Examples: 'FCM', 'XCM', 'SEM' ''',
                  'format': 'text',
                  'grouping': 'Sample Type/Intended Method',
                  'hstore': False,
                  'long_list': True,
                  'valid': {
                      'validate': 'list',
                      'source': 'intended_methods',
                      'input_title': 'Intended Method',
                      'input_message': '''The intended measurement or analysis method for the sample.
If multiple methods, separate with ';'.
Examples: 'FCM', 'XCM', 'SEM' ''',
                      'error_title': 'Error',
                      'error_message': 'Not a valid value, pick a value from the drop-down list.'
                  }
                  },
    {'name': 'tissueType',
              'disp_name': 'Tissue Type',
              'description': '''The type of tissue in the sample.
If multiple tissue types, organs etc. separate with ';'.
Examples: 'heart', 'liver; brain', 'liver section' ''',
              'format': 'text',
              'grouping': 'Sample Type/Intended Method',
              'hstore': 'other',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Tissue Type',
                  'input_message': '''The type of tissue in the sample.
If multiple tissue types, organs etc. separate with ';'.
Examples: 'heart', 'liver; brain', 'liver section' '''
              }
              },

    # ==============================================================================
    # Instrumentation
    # ==============================================================================
    {'name': 'gearType',
                    'disp_name': 'Gear Type',
                    'description': '''Choose the gear used to retrieve the sample.
Listed at: https://github.com/SIOS-Svalbard/AeN_doc/blob/master/list_gear_types.csv''',
                    'inherit': True,
                    'inherit_weak': True,
                    'format': 'text',
                    'grouping': 'Instrumentation',
                    'hstore': False,
                    'long_list': True,
                    'valid': {
                        'validate': 'list',
                        'source': 'gear_types',
                        'input_title': 'Gear Type',
                        'input_message': '''Choose the gear used to retrieve the sample.
Listed at: https://github.com/SIOS-Svalbard/AeN_doc/blob/master/list_gear_types.csv''',
                        'error_title': 'Error',
                        'error_message': 'Not a valid value, pick a value from the drop-down list.'
                    }
            },
    {'name': 'serialNumber',
                'disp_name': 'Serial Number',
                'description': 'The serial number of the instrument used',
                'format': 'text',
                'grouping': 'Numbering',
                'hstore': 'other',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Instrument Serial Number',
                    'input_message': 'The serial number of the instrument used'
                }
                },

    # ==============================================================================
    # Other
    # ==============================================================================
    {'name': 'dataFilename',
                'disp_name': 'Data filename',
                'description': 'The name of the file that contains the data',
                'format': 'text',
                'grouping': 'File Details',
                'hstore': 'other',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Data filename',
                    'input_message': 'The name of the file that contains the data'
                }
                },

    # ==============================================================================
    # Sampling protocols
    # ==============================================================================
    {'name': 'samplingProtocolDoc',
                    'disp_name': 'Sampling protocol document',
                    'description': '''This should be a reference to the document that contains the sampling protocol used.
Where possible, include the DOI of the document.''',
                    'format': 'text',
                    'grouping': 'Sampling Protocol',
                    'hstore': False,
                    'dwcid': 'https://dwc.tdwg.org/terms/#dwc:samplingProtocol',
                    'valid': {
                        'validate': 'any',
                        'input_title': 'Sampling Protocol Document',
                        'input_message': '''This should be a reference to the document that contains the sampling protocol used.
Where possible, include the DOI of the document.'''
                    }
                    },
    {'name': 'samplingProtocolSection',
                    'disp_name': 'Sampling protocol section',
                    'description': '''This should be a reference to the section within sampling protocol document.''',
                    'format': 'text',
                    'grouping': 'Sampling Protocol',
                    'hstore': False,
                    'dwcid': 'https://dwc.tdwg.org/terms/#dwc:samplingProtocol',
                    'valid': {
                        'validate': 'any',
                        'input_title': 'Sampling Protocol Section',
                        'input_message': '''This should be a reference to the section within sampling protocol document.'''
                    }
                    },
    {'name': 'samplingProtocolVersion',
                    'disp_name': 'Sampling protocol version',
                    'description': '''This should be a reference to the version of the sampling protocol document.
This is not neccessary if you have included the DOI in the sampling protocol document.''',
                    'format': 'text',
                    'grouping': 'Sampling Protocol',
                    'hstore': False,
                    'dwcid': 'https://dwc.tdwg.org/terms/#dwc:samplingProtocol',
                    'valid': {
                        'validate': 'any',
                        'input_title': 'Sampling Protocol Version',
                        'input_message': '''This should be a reference to the version of the sampling protocol document.
                        This is not neccessary if you have included the DOI in the sampling protocol document.'''
                    }
                    },

    # ==============================================================================
    # Comments
    # ==============================================================================
    {'name': 'comments1',
                'disp_name': 'Comments',
                'description': 'Main comments about the sample or event.',
                'width': 40,
                'format': 'text',
                'grouping': 'Comments',
                'hstore': False,
                'valid': {
                         'validate': 'any',
                         'input_title': 'Comments',
                         'input_message': 'Main comments about the sample or event.'
                }
                },
    {'name': 'comments2',
                'disp_name': 'Comments #2',
                'description': 'Additional comments about the sample or event.',
                'width': 40,
                'format': 'text',
                'grouping': 'Comments',
                'hstore': 'other',
                'valid': {
                         'validate': 'any',
                         'input_title': 'Comments #2',
                         'input_message': 'Additional comments about the sample or event.'
                }
                },
    {'name': 'comments3',
                'disp_name': 'Comments #3',
                'description': 'Additional comments about the sample or event.',
                'width': 40,
                'format': 'text',
                'grouping': 'Comments',
                'hstore': 'other',
                'valid': {
                         'validate': 'any',
                         'input_title': 'Comments #3',
                         'input_message': 'Additional comments about the sample or event.'
                }
                },
    {'name': 'comments4',
                'disp_name': 'Comments #4',
                'description': 'Additional comments about the sample or event.',
                'width': 40,
                'format': 'text',
                'grouping': 'Comments',
                'hstore': 'other',
                'valid': {
                         'validate': 'any',
                         'input_title': 'Comments #4',
                         'input_message': 'Additional comments about the sample or event.'
                }
                },
    {'name': 'comments5',
                'disp_name': 'Comments #5',
                'description': 'Additional comments about the sample or event.',
                'width': 40,
                'format': 'text',
                'grouping': 'Comments',
                'hstore': 'other',
                'valid': {
                         'validate': 'any',
                         'input_title': 'Comments #5',
                         'input_message': 'Additional comments about the sample or event.'
                }
                },

    # ==============================================================================
    # History and modifications
    # ==============================================================================
    {'name': 'history',
                'disp_name': 'history',
                'description': 'Additional comments about the sample or event.',
                'width': 40,
                'format': 'text',
                'grouping': 'Record Details',
                'hstore': False,
                'valid': {
                         'validate': 'any',
                         'input_title': 'History',
                         'input_message': 'History of when the sample was first logged and the record updated.'
                }
                },
    {'name': 'created',
                'disp_name': 'created',
                'description': 'Timestamp when the sample was first logged.',
                'width': 40,
                'format': 'timestamp with time zone',
                'grouping': 'Record Details',
                'hstore': False,
                'valid': {
                         'validate': 'any',
                         'input_title': 'Created',
                         'input_message': 'Timestamp when the sample was first logged.'
                }
                },
    {'name': 'modified',
                'disp_name': 'modified',
                'description': 'Timestamp when the log of the sample was last modified.',
                'width': 40,
                'format': 'timestamp with time zone',
                'grouping': 'Record Details',
                'hstore': False,
                'valid': {
                         'validate': 'any',
                         'input_title': 'Modified',
                         'input_message': 'Timestamp when the log of the sample was last modified.'
                }
                },
    {'name': 'source',
                'disp_name': 'source',
                'description': 'Where the source was logged (file or page).',
                'width': 40,
                'format': 'text',
                'grouping': 'Record Details',
                'hstore': False,
                'valid': {
                         'validate': 'any',
                         'input_title': 'Source',
                         'input_message': 'Where the source was logged (file or page).'
                }
                },
    ]

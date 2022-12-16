#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 15:27:00 2022

@author: lukem
"""

'''
 -- This file is for defining the possible metadata fields.
Each field is defined as a dictionary which should contain:
    name :       short name of field
    disp_name :  The displayed name of the field
    format:      uuid, int, text, time, date, double precision, boolean
    description: Description of the field
    grouping:    Categorising the fields so they can be grouped on the user interface, making it easier for the user to find what they are looking for.
                 groups: [
                 'Dataset Details',
                 'Cruise Details',
                 ]
    valid :      dict
                 a dictionary with definitions of the validation for the cell, as
                 per keywords used in Xlsxwriter

Optional fields are:
    width : int
            the width of the cell
    long_list: Boolean
            If the list wil exceed the Excel number of fields set this as true
    required : Boolean
             Is this metadata field required in this logging system?
             If not present then it is False by default
    derive_from: str
            Field in fields.py that this metadata term can be derived from.
            For example, minimum and maximum latitude can be derived from decimalLatitude
    derive_by: str
            Method used to derive metadata value from field
    units : str
            The measurement unit of the variable, using the standard in CF
           Examples: 'm', 'm s-1', '
    eml (subfields)
        name : str
                The field name in the Ecological Metadata Language conventions,
                recommended for use in Darwin Core Archives
                Documented here: https://rs.gbif.org/schema/eml-gbif-profile/1.1/eml-gbif-profile.xsd
        description: str
                The description associated with the name
        recommendations: str
                Is the field
                as defined here:
    acdd (subfields)
        name : str
                 The field name in the ACDD conventions, recommended for use in NetCDF files
                 https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3
        description: str
                 The description associated with the name
        recommendations: str
                Is the global attribute 'Highly Recommended', 'Recommended', or 'Suggested'
                as defined here: https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3
    cell_format :  dict
                   a dictionary with definitions of the format for the cell, as
                   per keywords in Xlsxwriter
'''

import datetime as dt
import uuid

metadata_fields = [

    # ==============================================================================
    # Terms required by arctic data centre for NetCDF/CF files
    # https://adc.met.no/node/4
    # ==============================================================================
    {'name': 'dataset_id',
                'disp_name': "Dataset ID",
                'acdd': {
                    'name': "id",
                    'description': "An identifier for the data set, provided by and unique within its naming authority. The combination of the 'naming authority' and the 'id' should be globally unique, but the id can be globally unique by itself also. IDs can be URLs, URNs, DOIs, meaningful text strings, a local key, or any other unique string of characters. The id should not include white space characters.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "alternateIdentifier",
                    'description': "It is a Universally Unique Identifier (UUID) for the EML document and not for the dataset. This term is optional. A list of different identifiers can be supplied. E.g., 619a4b95-1a82-4006-be6a-7dbe3c9b33c5.",
                    'recommendations': 'Optional'
                },
                'default': str(uuid.uuid1()),
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Dataset ID',
                    'input_message': "An identifier for the data set, provided by and unique within its naming authority. The combination of the 'naming authority' and the 'id' should be globally unique, but the id can be globally unique by itself also. IDs can be URLs, URNs, DOIs, meaningful text strings, a local key, or any other unique string of characters. The id should not include white space characters."
                    }
                },
    {'name': 'naming_authority',
                'disp_name': "Naming Authority",
                'acdd': {
                    'name': "naming_authority",
                    'description': "The organization that provides the initial id (see above) for the dataset. The naming authority should be uniquely specified by this attribute. We recommend using reverse-DNS naming for the naming authority; URIs are also acceptable. Example: 'edu.ucar.unidata'.",
                    'recommendations': 'Recommended',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Naming Authority',
                    'input_message': "The organization that provides the initial id (see above) for the dataset. The naming authority should be uniquely specified by this attribute. We recommend using reverse-DNS naming for the naming authority; URIs are also acceptable. Example: 'edu.ucar.unidata'."
                    }
                },
    {'name': 'language',
                'disp_name': "Language",
                'eml': {
                    'name': 'language',
                    'description': "The language in which the resource (not the metadata document) is written",
                    'recommendations': 'Required',
                },
                'default': 'English',
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Language',
                    'input_message': "The language in which the resource (not the metadata document) is written"
                    }
                },
    {'name': 'title',
                'disp_name': 'Title',
                'acdd': {
                    'name': 'title',
                    'description': 'A short phrase or sentence describing the dataset. In many discovery systems, the title will be displayed in the results list from a search, and therefore should be human readable and reasonable to display in a list of such names. This attribute is also recommended by the NetCDF Users Guide and the CF conventions.',
                    'recommendations': 'Highly Recommended',
                },
                'eml': {
                    'name': 'title',
                    'description': "The 'title' field provides a description of the resource that is being documented that is long enough to differentiate it from other similar resources. Multiple titles may be provided, particularly when trying to express the title in more than one language",
                    'recommendations': 'Required',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Title',
                    'input_message': 'A short phrase or sentence describing the dataset. In many discovery systems, the title will be displayed in the results list from a search, and therefore should be human readable and reasonable to display in a list of such names.'
                    }
                },
    {'name': 'summary',
                'disp_name': 'Summary',
                'acdd': {
                    'name': 'summary',
                    'description': 'A paragraph describing the dataset, analogous to an abstract for a paper.',
                    'recommendations': 'Highly Recommended',
                },
                'eml': {
                    'name': 'abstract',
                    'description': "A brief overview of the resource that is being documented. The abstract should include basic information that summarizes the resource.",
                    'recommendations': 'Required',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Summary',
                    'input_message': 'A paragraph describing the dataset, analogous to an abstract for a paper.'
                    }
                },
    {'name': 'metadataProvider',
                'disp_name': 'Metadata Provider',
                'eml': {
                    'name': 'metadataProvider',
                    'description': "The metadataProvider is the person or organization responsible for providing documentation for the resource.",
                    'recommendations': 'Required'
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Metadata Provider',
                    'input_message': 'The metadataProvider is the person or organization responsible for providing documentation for the resource.'
                    }
                },
    # Keywords in EML are separate 'keyword' fields, how do I manage this?!
    # Separate into EML on output by splitting them? Or have multiple fields to begin with?
    # Link to GCMD keywords in metadata sheet
    {'name': 'keywords',
                'disp_name': "Keywords",
                'acdd': {
                    'name': "keywords",
                    'description': "A comma-separated list of key words and/or phrases. Keywords may be common words or phrases, terms from a controlled vocabulary (GCMD is required), or URIs for terms from a controlled vocabulary (see also 'keywords_vocabulary' attribute). If keywords are extracted from e.g. GCMD Science Keywords, add keywords_vocabulary='GCMDSK' and prefix in any case each keyword with the appropriate prefix.",
                    'recommendations': 'Highly Recommended',
                },
                'eml': {
                    'name': "keyword",
                    'description': "This field names a keyword or key phrase that concisely describes the resource or is related to the resource. Each keyword field should contain one and only one keyword",
                    'recommendations': 'Required'
                },
                'link': 'https://gcmd.earthdata.nasa.gov/KeywordViewer/scheme/all?gtm_scheme=all',
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Keyword(s)',
                    'input_message': "A comma-separated list of key words and/or phrases. Keywords may be common words or phrases, terms from a controlled vocabulary (GCMD is required), or URIs for terms from a controlled vocabulary (see also 'keywords_vocabulary' attribute). If keywords are extracted from e.g. GCMD Science Keywords, add keywords_vocabulary='GCMDSK' and prefix in any case each keyword with the appropriate prefix."
                    }
                },
    {'name': 'keywords_vocabulary',
                'disp_name': "Keywords Vocabulary",
                'acdd': {
                    'name': "keywords_vocabulary",
                    'description': "If you are using a controlled vocabulary for the words/phrases in your 'keywords' attribute, this is the unique name or identifier of the vocabulary from which keywords are taken. If more than one keyword vocabulary is used, each may be presented with a prefix and a following comma, so that keywords may optionally be prefixed with the controlled vocabulary key. Example: 'GCMD:GCMD Keywords, CF:NetCDF COARDS Climate and Forecast Standard Names'.",
                    'recommendations': 'Suggested',
                },
                'eml': {
                    'name': "keywordThesaurus",
                    'description': "The name of the official keyword thesaurus from which keyword was derived",
                    'recommendations': 'Required',
                },
                'default': 'GCMD:GCMD Keywords',
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Keywords Vocabulary',
                    'input_message': "If you are using a controlled vocabulary for the words/phrases in your 'keywords' attribute, this is the unique name or identifier of the vocabulary from which keywords are taken. If more than one keyword vocabulary is used, each may be presented with a prefix and a following comma, so that keywords may optionally be prefixed with the controlled vocabulary key. Example: 'GCMD:GCMD Keywords, CF:NetCDF COARDS Climate and Forecast Standard Names'."
                    }
                },
    {'name': 'geospatial_lat_min',
                'disp_name': "Minimum Latitude",
                'acdd': {
                    'name': "geospatial_lat_min",
                    'description': "Describes a simple lower latitude limit; may be part of a 2- or 3-dimensional bounding region. Geospatial_lat_min specifies the southernmost latitude covered by the dataset. Must be decimal degrees north.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "southBoundingCoordinate",
                    'description': "The southBoundingCoordinate field defines the latitude of the southern-most point of the bounding box that is being described.",
                    'recommendations': 'Required'
                },
                'derive_from': 'decimalLatitude',
                'derive_by': 'min',
                'units': 'degree_north',
                'format': 'double precision',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'decimal',
                    'criteria': 'between',
                    'minimum': -90,
                    'maximum': 90,
                    'input_title': 'Minimum Latitude',
                    'input_message': '''Maximum latitude in decimal degrees.
Northern hemisphere is positive.
Example: 78.1500''',
                    'error_title': 'Error',
                    'error_message': 'Not in range [-90, 90]'
                },
                'cell_format': {
                    'num_format': '0.0000'
                }
                },
    {'name': 'geospatial_lat_max',
                'disp_name': "Maximum Latitude",
                'acdd': {
                    'name': "geospatial_lat_max",
                    'description': "Describes a simple upper latitude limit; may be part of a 2- or 3-dimensional bounding region. Geospatial_lat_max specifies the northernmost latitude covered by the dataset. Must be decimal degrees north.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "northBoundingCoordinate",
                    'description': "The northBoundingCoordinate field defines the latitude of the northern-most point of the bounding box that is being described.",
                    'recommendations': 'Required'
                },
                'derive_from': 'decimalLatitude',
                'derive_by': 'max',
                'units': 'degree_north',
                'format': 'double precision',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'decimal',
                    'criteria': 'between',
                    'minimum': -90,
                    'maximum': 90,
                    'input_title': 'Maximum Latitude',
                    'input_message': '''Maximum latitude in decimal degrees.
Northern hemisphere is positive.
Example: 78.1500''',
                    'error_title': 'Error',
                    'error_message': 'Not in range [-90, 90]'
                },
                'cell_format': {
                    'num_format': '0.0000'
                }
                },
    {'name': 'geospatial_lon_min',
                'disp_name': "Minimum Longitude",
                'acdd': {
                    'name': "geospatial_lon_min",
                    'description': "Describes a simple lower longitude limit; may be part of a 2- or 3-dimensional bounding region. Geospatial_lon_min specifies the westernmost longitude covered by the dataset. Must be decimal degrees east.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "westBoundingCoordinate",
                    'description': "The westBoundingCoordinate field defines the longitude of the western-most point of the bounding box that is being described.",
                    'recommendations': 'Required'
                },
                'derive_from': 'decimalLongitude',
                'derive_by': 'min',
                'units': 'degree_east',
                'format': 'double precision',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'decimal',
                    'criteria': 'between',
                    'minimum': -180,
                    'maximum': 180,
                    'input_title': 'Minimum Longitude',
                    'input_message': '''Minimum longitude in decimal degrees.
East of Greenwich (0) is positive.
Example: 15.0012''',
                    'error_title': 'Error',
                    'error_message': 'Not in range [-180, 180]'
                },
                'cell_format': {
                    'num_format': '0.0000'
                }
                },
    {'name': 'geospatial_lon_max',
                'disp_name': "Maximum Longitude",
                'acdd': {
                    'name': "geospatial_lon_max",
                    'description': "Describes a simple upper longitude limit; may be part of a 2- or 3-dimensional bounding region. Geospatial_lon_max specifies the easternmost longitude covered by the dataset. Must be decimal degrees east.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "eastBoundingCoordinate",
                    'description': "The eastBoundingCoordinate field defines the longitude of the eastern-most point of the bounding box that is being described.",
                    'recommendations': 'Required'
                },
                'derive_from': 'decimalLongitude',
                'derive_by': 'max',
                'units': 'degree_east',
                'format': 'double precision',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'decimal',
                    'criteria': 'between',
                    'minimum': -180,
                    'maximum': 180,
                    'input_title': 'Maximum Longitude',
                    'input_message': '''Maximum longitude in decimal degrees.
East of Greenwich (0) is positive.
Example: 15.0012''',
                    'error_title': 'Error',
                    'error_message': 'Not in range [-180, 180]'
                },
                'cell_format': {
                    'num_format': '0.0000'
                }
                },

    {'name': 'geospatial_vertical_min',
                'disp_name': "Minimum Vertical (m)",
                'acdd': {
                    'name': "geospatial_vertical_min",
                    'description': "Describes the numerically smaller vertical limit; may be part of a 2- or 3-dimensional bounding region. See geospatial_vertical_positive and geospatial_vertical_units.",
                    'recommendations': 'Recommended',
                },
                'derive_from': ['minimumDepthInMeters','minimumElevationInMeters'],
                'derive_by': 'min',
                'format': 'double precision',
                'grouping': 'Dataset Details',
                'units': 'm',
                'valid': {
                    'validate': 'decimal',
                    'criteria': 'between',
                    'minimum': 0,
                    'maximum': 9999,
                    'input_title': 'Minimum Vertical (m)',
                    'input_message': '''Describes the numerically smaller vertical limit; may be part of a 2- or 3-dimensional bounding region. See geospatial_vertical_positive and geospatial_vertical_units.''',
                    'error_title': 'Error',
                    'error_message': 'Decimal [0, 9999]'
                }
                },
    {'name': 'geospatial_vertical_max',
                'disp_name': "Maximum Vertical (m)",
                'acdd': {
                    'name': "geospatial_vertical_min",
                    'description': "Describes the numerically larger vertical limit; may be part of a 2- or 3-dimensional bounding region. See geospatial_vertical_positive and geospatial_vertical_units.",
                    'recommendations': 'Recommended',
                },
                'derive_from': ['maximumDepthInMeters','maximumElevationInMeters'],
                'derive_by': 'max',
                'format': 'double precision',
                'grouping': 'Dataset Details',
                'units': 'm',
                'valid': {
                    'validate': 'decimal',
                    'criteria': 'between',
                    'minimum': 0,
                    'maximum': 9999,
                    'input_title': 'Maximum Vertical (m)',
                    'input_message': '''Describes the numerically larger vertical limit; may be part of a 2- or 3-dimensional bounding region. See geospatial_vertical_positive and geospatial_vertical_units.''',
                    'error_title': 'Error',
                    'error_message': 'Decimal [0, 9999]'
                }
                },
    {'name': 'geospatial_vertical_positive',
                'disp_name': "Vertical Positive Direction",
                'acdd': {
                    'name': "geospatial_vertical_positive",
                    'description': "One of 'up' or 'down'. If up, vertical values are interpreted as 'altitude', with negative values corresponding to below the reference datum (e.g., under water). If down, vertical values are interpreted as 'depth', positive values correspond to below the reference datum. Note that if geospatial_vertical_positive is down ('depth' orientation), the geospatial_vertical_min attribute specifies the data's vertical location furthest from the earth's center, and the geospatial_vertical_max attribute specifies the location closest to the earth's center.",
                    'recommendations': 'Recommended',
                },
                'derive_from': ['maximumDepthInMeters','maximumElevationInMeters'],
                'derive_by': 'up/down',
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'list',
                    'source': ['up', 'down'],
                    'input_title': 'Vertical Positive Direction',
                    'input_message': '''One of 'up' or 'down'. If up, vertical values are interpreted as 'altitude', with negative values corresponding to below the reference datum (e.g., under water). If down, vertical values are interpreted as 'depth', positive values correspond to below the reference datum. Note that if geospatial_vertical_positive is down ('depth' orientation), the geospatial_vertical_min attribute specifies the data's vertical location furthest from the earth's center, and the geospatial_vertical_max attribute specifies the location closest to the earth's center.''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid value, pick a value from the drop-down list.'
                    }
                },
    {'name': 'geospatial_vertical_units',
                'disp_name': "Vertical Units",
                'acdd': {
                    'name': "geospatial_vertical_units",
                    'description': "Units for the vertical axis described in 'geospatial_vertical_min' and 'geospatial_vertical_max' attributes. The default is EPSG:4979 (height above the ellipsoid, in meters); other vertical coordinate reference systems may be specified. Note that the common oceanographic practice of using pressure for a vertical coordinate, while not strictly a depth, can be specified using the unit bar. Examples: 'EPSG:5829' (instantaneous height above sea level), 'EPSG:5831' (instantaneous depth below sea level).",
                    'recommendations': 'Suggested',
                },
                'default': 'm',
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Vertical Units',
                    'input_message': "Units for the vertical axis described in 'geospatial_vertical_min' and 'geospatial_vertical_max' attributes."

                    }
                },
    {'name': 'studyAreaDescription',
                'disp_name': "Study Area Description",
                'eml': {
                    'name': "studyAreaDescription",
                    'description': "The studyAreaDescription field documents the physical area associated with the research project. It can include descriptions of the geographic, temporal, and taxonomic coverage of the research location and descriptions of domains (themes) of interest such as climate, geology, soils or disturbances.",
                    'recommendations': 'Required',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Study Area Description',
                    'input_message': "The studyAreaDescription field documents the physical area associated with the research project. It can include descriptions of the geographic, temporal, and taxonomic coverage of the research location and descriptions of domains (themes) of interest such as climate, geology, soils or disturbances."
                    }
                },

    {'name': 'time_coverage_start',
                'disp_name': "Time Coverage Start",
                'acdd': {
                    'name': "time_coverage_start",
                    'description': "Describes the time of the first data point in the data set. Use the ISO 8601:2004 date format, preferably the extended format as recommended in the Attribute Content Guidance section. I.e. YYYY-MM-DDTHH:MM:SSZ (always use UTC).",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "beginDate",
                    'description': "A single time stamp signifying the beginning of some time period",
                    'recommendations': 'Optional',
                },
                'derive_from': ['eventDate', 'eventTime'],
                'derive_by': 'min',
                'format': 'datetime',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'datetime',
                    'criteria': 'between',
                    'minimum': dt.datetime(2000, 1, 1, 00, 00),
                    'maximum': '=TODAY()+2',
                    'input_title': 'Time Coverage Start',
                    'input_message': '''Timestamp that data collection began. Should be in ISO8601 format, in UTC time, e.g. 2022-04-10T15:42:38Z''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid date [2000-01-01, today + 2]'
                },
                'cell_format': {
                    'num_format': 'yyyy-mm-dd hh:mm'
                }
                },
    {'name': 'time_coverage_end',
                'disp_name': "Time Coverage End",
                'acdd': {
                    'name': "time_coverage_end",
                    'description': "Describes the time of the last data point in the data set. Use the ISO 8601:2004 date format, preferably the extended format as recommended in the Attribute Content Guidance section. I.e. YYYY-MM-DDTHH:MM:SSZ (always use UTC).",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "endDate",
                    'description': "A single time stamp signifying the end of some time period",
                    'recommendations': 'Optional'
                },
                'derive_from': ['eventDate', 'eventTime'],
                'derive_by': 'max',
                'format': 'datetime',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'datetime',
                    'criteria': 'between',
                    'minimum': dt.datetime(2000, 1, 1, 00, 00),
                    'maximum': '=TODAY()+2',
                    'input_title': 'Time Coverage End',
                    'input_message': '''Timestamp that data collection ended. Should be in ISO8601 format, in UTC time, e.g. 2022-04-10T15:42:38Z''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid date [2000-01-01, today + 2]'
                },
                'cell_format': {
                    'num_format': 'yyyy-mm-dd hh:mm'
                }
                },
    # Populate ACDD or EML automatically? Then the user needs to choose the version of CF or DwC later?
    {'name': 'Conventions',
                'disp_name': "Conventions",
                'acdd': {
                    'name': "Conventions",
                    'description': "A comma-separated string of the conventions that are followed by the dataset. For files that follow this version of ACDD, include the string 'ACDD-1.3'. (This attribute is described in the NetCDF Users Guide.)",
                    'recommendations': 'Highly Recommended',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Conventions',
                    'input_message': "A comma-separated string of the conventions that are followed by the dataset. For files that follow this version of ACDD, include the string 'ACDD-1.3'. (This attribute is described in the NetCDF Users Guide.)"
                    }
                },
    {'name': 'history',
                'disp_name': "Data History",
                'acdd': {
                    'name': "history",
                    'description': "Provides an audit trail for modifications to the original data. This attribute is also in the NetCDF Users Guide: 'This is a character array with a line for each invocation of a program that has modified the dataset. Well-behaved generic netCDF applications should append a line containing: date, time of day, user name, program name and command arguments.' To include a more complete description you can append a reference to an ISO Lineage entity; see NOAA EDM ISO Lineage guidance.",
                    'recommendations': 'Recommended',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'History',
                    'input_message': "Provides an audit trail for modifications to the original data. This attribute is also in the NetCDF Users Guide: 'This is a character array with a line for each invocation of a program that has modified the dataset. Well-behaved generic netCDF applications should append a line containing: date, time of day, user name, program name and command arguments.' To include a more complete description you can append a reference to an ISO Lineage entity; see NOAA EDM ISO Lineage guidance."
                    }
                },
    {'name': 'source',
                'disp_name': "Date Source",
                'acdd': {
                    'name': "source",
                    'description': "The method of production of the original data. If it was model-generated, source should name the model and its version. If it is observational, source should characterize it. This attribute is defined in the CF Conventions. Examples: 'temperature from CTD #1234'; 'world model v.0.1'.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "methods",
                    'description': "The methods field documents scientific methods used in the collection of this dataset. It includes information on items such as tools, instrument calibration and software.",
                    'recommendations': 'Required',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Data Source',
                    'input_message': "The methods field documents scientific methods used in the collection of this dataset. It includes information on items such as tools, instrument calibration and software."
                    }
                },
    {'name': 'processing_level',
                'disp_name': "Processing Level",
                'acdd': {
                    'name': "processing_level",
                    'description': "A textual description of the processing (or quality control) level of the data.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "methodStep",
                    'description': "The methodStep field allows for repeated sets of elements that document a series of procedures followed to produce a data object. These include text descriptions of the procedures, relevant literature, software, instrumentation, source data and any quality control measures taken.",
                    'recommendations': 'Optional',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Processing Level',
                    'input_message': "A textual description of the processing (or quality control) level of the data."
                    }
                },
    {'name': 'date_created',
                'disp_name': "Date Created",
                'acdd': {
                    'name': "date_created",
                    'description': "The date on which this version of the data was created. (Modification of values implies a new version, hence this would be assigned the date of the most recent values modification.) Metadata changes are not considered when assigning the date_created. The ISO 8601:2004 extended date format is recommended, as described in the Attribute Content Guidance section. E.g. 2020-10-20T12:35:00Z.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "dateStamp",
                    'description': "The date the metadata document was created or modified.",
                    'recommendations': 'Optional',
                },
                'default': dt.datetime.utcnow(),
                'format': 'datetime',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'datetime',
                    'criteria': 'between',
                    'minimum': dt.datetime(2000, 1, 1, 00, 00),
                    'maximum': '=TODAY()+2',
                    'input_title': 'Date Created',
                    'input_message': '''The datetime on which this version of the data was created. (Modification of values implies a new version, hence this would be assigned the date of the most recent values modification.) Metadata changes are not considered when assigning the date_created. The ISO 8601:2004 extended date format is recommended, as described in the Attribute Content Guidance section. E.g. 2020-10-20T12:35:00Z.''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid datetime [2000-01-01, today + 2]'
                },
                'cell_format': {
                    'num_format': 'yyyy-mm-dd hh:mm:ss'
                }
                },
    {'name': 'creator_name',
                'disp_name': "Creator Name",
                'acdd': {
                    'name': "creator_name",
                    'description': "The name of the person (or other creator type specified by the creator_type attribute) principally responsible for creating this data. See last paragraph under creator_type.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "creator",
                    'description': "The 'creator' element provides the full name of the person, organization, or position who created the resource. The list of creators for a resource represent the people and organizations who should be cited for the resource.",
                    'recommendations': 'Required',
                },
                'format': 'text',
                'derive_from': ['recordedBy_name', 'pi_name'],
                'derive_by': 'concat',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Creator Name',
                    'input_message': "The name of the person (or other creator type specified by the creator_type attribute) principally responsible for creating this data. See last paragraph under creator_type."
                    }
                },
    {'name': 'creator_type',
                'disp_name': "Creator Type",
                'acdd': {
                    'name': "creator_type",
                    'description': '''Specifies type of creator with one of the following: 'person', 'group', 'institution', or 'position'. If this attribute is not specified, the creator is assumed to be a person.

    If multiple persons are involved, please list these as a comma separated string. In such situation please remember to add a comma separated string for creator_institution and creator_email as well. Consistency between these fields are done from left to right.''',
                    'recommendations': 'Suggested',
                },
                'format': 'text',
                'default': 'person',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Creator Type',
                    'input_message': '''Specifies type of creator with one of the following: 'person', 'group', 'institution', or 'position'. If this attribute is not specified, the creator is assumed to be a person.

    If multiple persons are involved, please list these as a comma separated string. In such situation please remember to add a comma separated string for creator_institution and creator_email as well. Consistency between these fields are done from left to right.'''
                    }
                },
    {'name': 'creator_institution',
                'disp_name': "Creator Institution",
                'acdd': {
                    'name': "creator_institution",
                    'description': "The institution of the creator; should uniquely identify the creator's institution. This attribute's value should be specified even if it matches the value of publisher_institution, or if creator_type is institution. See last paragraph under creator_type.",
                    'recommendations': 'Suggested',
                },
                'eml': {
                    'name': "organizationName",
                    'description': "The full name of the organization that is associated with the resource. This field is intended to describe which institution or overall organization is associated with the resource being described.",
                    'recommendations': 'Required',
                },
                'format': 'text',
                'derive_from': ['recordedBy_institution', 'pi_institution'],
                'derive_by': 'concat',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Creator Institution',
                    'input_message': "The institution of the creator; should uniquely identify the creator's institution. This attribute's value should be specified even if it matches the value of publisher_institution, or if creator_type is institution. See last paragraph under creator_type."
                    }
                },
    {'name': 'creator_email',
                'disp_name': "Creator Email",
                'acdd': {
                    'name': "creator_email",
                    'description': "The email address of the person (or other creator type specified by the creator_type attribute) principally responsible for creating this data. See last paragraph under creator_type.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': 'electronicMailAddress',
                    'description': 'The electronic mail address is the email address for the party. It is intended to be an Internet SMTP email address, which should consist of a username followed by the @ symbol, followed by the email server domain name address.',
                    'recommendations': 'Required',
                },
                'format': 'text',
                'derive_from': ['recordedBy_email', 'pi_email'],
                'derive_by': 'concat',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Creator Email',
                    'input_message': "The email address of the person (or other creator type specified by the creator_type attribute) principally responsible for creating this data. See last paragraph under creator_type."
                    }
                },
    {'name': 'creator_url',
                'disp_name': "Creator URL",
                'acdd': {
                    'name': "creator_url",
                    'description': "The URL of the person (or other creator type specified by the creator_type attribute) principally responsible for creating this data. See last paragraph under creator_type.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "onlineUrl",
                    'description': "A link to associated online information, usually a web site. When the party represents an organization, this is the URL to a website or other online information about the organization. If the party is an individual, it might be their personal web site or other related online information about the party.",
                    'recommendations': 'Recommended',
                },
                'format': 'text',
                'derive_from': ['recordedBy_orcid', 'pi_orcid'],
                'derive_by': 'concat',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Creator URL',
                    'input_message': "The URL of the person (or other creator type specified by the creator_type attribute) principally responsible for creating this data. See last paragraph under creator_type."
                    }
                },
    {'name': 'institution',
                'disp_name': "Institution",
                'acdd': {
                    'name': "institution",
                    'description': "The name of the institution principally responsible for originating this data. This attribute is recommended by the CF convention. If provided as a string ending with a keyword in parantheses (), the main text will be interpreted as the long name and the keyword in the parantheses as the short name. E.g. 'Norwegian Meteorological Institute (MET)'",
                    'recommendations': 'Recommended',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Institution',
                    'input_message': "The name of the institution principally responsible for originating this data. This attribute is recommended by the CF convention. If provided as a string ending with a keyword in parantheses (), the main text will be interpreted as the long name and the keyword in the parantheses as the short name. E.g. 'Norwegian Meteorological Institute (MET)'"
                    }
                },
    {'name': 'project',
                'disp_name': "Project",
                'acdd': {
                    'name': "project",
                    'description': "The name of the project(s) principally responsible for originating this data. Multiple projects can be separated by commas, as described under Attribute Content Guidelines. Examples: 'PATMOS-X', 'Extended Continental Shelf Project'. If each substring includes a keyword in parantheses, this is interpreted as the short name for the project while the rest is the long name. E.g. 'Nansen Legacy (NLEG)'.",
                    'recommendations': 'Recommended',
                },
                'eml': {
                    'name': "project",
                    'description': "The project field contains information on the project in which this dataset was collected. It includes information such as project personnel, funding, study area, project design and related projects.",
                    'recommendations': 'Required',
                },
                'format': 'text',
                'derive_from_table': 'cruise_details',
                'derive_from': 'project',
                'derive_by': 'copy',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Project',
                    'input_message': "The name of the project(s) principally responsible for originating this data. Multiple projects can be separated by commas, as described under Attribute Content Guidelines. Examples: 'PATMOS-X', 'Extended Continental Shelf Project'. If each substring includes a keyword in parantheses, this is interpreted as the short name for the project while the rest is the long name. E.g. 'Nansen Legacy (NLEG)'."
                    }
                },
    {'name': 'publisher_name',
                'disp_name': "Publisher Name",
                'acdd': {
                    'name': "publisher_name",
                    'description': "The name of the person (or other entity specified by the publisher_type attribute) responsible for publishing the data file or product to users, with its current metadata and format.",
                    'recommendations': 'Recommended',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Publisher Name',
                    'input_message': "The name of the person (or other entity specified by the publisher_type attribute) responsible for publishing the data file or product to users, with its current metadata and format."
                    }
                },
    {'name': 'publisher_email',
                'disp_name': "Publisher Email",
                'acdd': {
                    'name': "publisher_email",
                    'description': "The email address of the person (or other entity specified by the publisher_type attribute) responsible for publishing the data file or product to users, with its current metadata and format.",
                    'recommendations': 'Recommended',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Publisher Email',
                    'input_message': "The email address of the person (or other entity specified by the publisher_type attribute) responsible for publishing the data file or product to users, with its current metadata and format."
                    }
                },
    {'name': 'publisher_url',
                'disp_name': "Publisher URL",
                'acdd': {
                    'name': "publisher_url",
                    'description': "The URL of the person (or other entity specified by the publisher_type attribute) responsible for publishing the data file or product to users, with its current metadata and format.",
                    'recommendations': 'Recommended',
                },
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Publisher URL',
                    'input_message': "The URL of the person (or other entity specified by the publisher_type attribute) responsible for publishing the data file or product to users, with its current metadata and format."
                    }
                },
    {'name': 'license',
                'disp_name': "License",
                'acdd': {
                    'name': "license",
                    'description': "Provide the URL to a standard or specific license, enter 'Freely Distributed' or 'None', or describe any restrictions to data access and distribution in free text. It is strongly recommended to use identifiers and URL's from https://spdx.org/licenses/ and to use a form similar to <URL>(<Identifier>) using elements from the SPDX source listed above.",
                    'recommendations': 'Recommended',
                },
                'default': 'https://creativecommons.org/licenses/by/4.0/',
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'License',
                    'input_message': "Provide the URL to a standard or specific license, enter 'Freely Distributed' or 'None', or describe any restrictions to data access and distribution in free text. It is strongly recommended to use identifiers and URL's from https://spdx.org/licenses/ and to use a form similar to <URL>(<Identifier>) using elements from the SPDX source listed above."
                    }
                },
    {'name': 'instrument',
                'disp_name': "Instrument",
                'acdd': {
                    'name': "instrument",
                    'description': "Name of the contributing instrument(s) or sensor(s) used to create this data set or product. Indicate controlled vocabulary used in instrument_vocabulary. Comma separated list.",
                    'recommendations': 'Suggested',
                },
                'derive_from': 'gearType',
                'derive_by': 'concat',
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Instrument',
                    'input_message': "Name of the contributing instrument(s) or sensor(s) used to create this data set or product. Indicate controlled vocabulary used in instrument_vocabulary. Comma separated list."
                    }
                },
    {'name': 'instrument_vocabulary',
                'disp_name': "Instrument Vocabulary",
                'acdd': {
                    'name': "instrument_vocabulary",
                    'description': "Controlled vocabulary for the names used in the 'instrument' attribute. Comma separated list. Remember to use prefixes like for keywords.",
                    'recommendations': 'Suggested',
                },
                'derive_from': 'gearType',
                'derive_by': 'concat',
                'format': 'text',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Instrument Vocabulary',
                    'input_message': "Controlled vocabulary for the names used in the 'instrument' attribute. Comma separated list. Remember to use prefixes like for keywords."
                    }
                },
    {'name': 'cruise_number',
                'disp_name': "Cruise Number",
                'format': 'text',
                'derive_from_table': 'cruise_details',
                'derive_from': 'cruise_number',
                'derive_by': 'copy',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Cruise Number',
                    'input_message': "cruise number"
                    }
                },
    {'name': 'cruise_name',
                'disp_name': "Cruise Name",
                'format': 'text',
                'derive_from_table': 'cruise_details',
                'derive_from': 'cruise_name',
                'derive_by': 'copy',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Cruise Name',
                    'input_message': "cruise name"
                    }
                },
    {'name': 'vessel_name',
                'disp_name': "Vessel Name",
                'format': 'text',
                'derive_from_table': 'cruise_details',
                'derive_from': 'vessel_name',
                'derive_by': 'copy',
                'grouping': 'Dataset Details',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Vessel Name',
                    'input_message': "vessel name"
                    }
                }
    ]

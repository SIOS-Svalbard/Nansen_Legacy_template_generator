import yaml
import Learnings_from_AeN_template_generator.config.fields as fields
import os
import pandas as pd
import json

def get_fields(configuration):
    '''
    Function to get the fields for a certain configuration in the 'template_configurations.yaml' file.

    Parameters
    ----------
    configuration: string
        The name of the configuration
    '''

    required_fields = ['id','parentID','sampleType','stationName','eventDate','eventTime','decimalLatitude','decimalLongitude','minimumDepthInMeters','maximumDepthInMeters','pi_name','pi_email','recordedBy_name','recordedBy_email']
    recommended_fields = ['gearType','pi_institution','pi_orcid','recordedBy_institution','recordedBy_orcid','sampleLocation','samplingProtocolDoc','samplingProtocolVersion','samplingProtocolSection','comments1']

    required_fields_dic = {}
    recommended_fields_dic = {}
    extra_fields_dic = {}

    groups = []
    extrafields=[]

    for field in fields.fields:
        if field['name'] in required_fields:
            if field['grouping'] not in ['Record Details'] and field['name'] not in ['pi_details', 'recordedBy_details']:
                required_fields_dic[field['name']] = {}
                required_fields_dic[field['name']]['disp_name'] = field['disp_name']
                required_fields_dic[field['name']]['description'] = field['description']
                required_fields_dic[field['name']]['format'] = field['format']
                if field['valid']['validate'] == 'list' and field['name'] not in ['stationName']:
                    table = field['valid']['source']
                    df = pd.read_csv(f'Learnings_from_AeN_template_generator/config/{table}.csv')
                    required_fields_dic[field['name']]['source'] = list(df[field['name'].lower()])
        elif field['name'] in recommended_fields:
            if field['grouping'] not in ['Record Details'] and field['name'] not in ['pi_details', 'recordedBy_details']:
                recommended_fields_dic[field['name']] = {}
                recommended_fields_dic[field['name']]['disp_name'] = field['disp_name']
                recommended_fields_dic[field['name']]['description'] = field['description']
                recommended_fields_dic[field['name']]['format'] = field['format']
                if field['valid']['validate'] == 'list' and field['name'] not in ['stationName']:
                    table = field['valid']['source']
                    df = pd.read_csv(f'Learnings_from_AeN_template_generator/config/{table}.csv')
                    recommended_fields_dic[field['name']]['source'] = list(df[field['name'].lower()])
        else:
            # Setting up extra fields for the 'modal' where the user can add more fields
            # Removing fields already included on the form and creating a list of groups so they can be grouped on the UI.
            if field['grouping'] not in ['Record Details'] and field['name'] not in ['pi_details', 'recordedBy_details']:
                extra_fields_dic[field['name']] = {}
                extra_fields_dic[field['name']]['disp_name'] = field['disp_name']
                extra_fields_dic[field['name']]['description'] = field['description']
                extra_fields_dic[field['name']]['format'] = field['format']
                extra_fields_dic[field['name']]['grouping'] = field['grouping']
                if field['valid']['validate'] == 'list' and field['name'] not in ['stationName']:
                    table = field['valid']['source']
                    df = pd.read_csv(f'Learnings_from_AeN_template_generator/config/{table}.csv')
                    extra_fields_dic[field['name']]['source'] = list(df[field['name'].lower()])

                groups.append(field['grouping'])

    groups = sorted(list(set(groups)))

    return required_fields_dic, recommended_fields_dic, extra_fields_dic, groups

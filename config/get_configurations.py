import yaml
import sys
from os.path import os
config_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'config'))

sys.path.append(config_dir)
import fields as fields
from pull_cf_standard_names import cf_standard_names_to_dic
#import pandas as pd

def get_list_of_configs():

    configs = yaml.safe_load(open("Learnings_from_AeN_template_generator/config/template_configurations.yaml", encoding='utf-8'))['setups']
    configs_list = []

    for config in configs:
        configs_list.append(config)

    return configs_list

def get_list_of_subconfigs(config):

    configs = yaml.safe_load(open("Learnings_from_AeN_template_generator/config/template_configurations.yaml", encoding='utf-8'))['setups']
    subconfigs = []

    if config == 'Learnings from Nansen Legacy logging system':
        for subconfig in configs[config]:
            subconfigs.append(subconfig)

    return subconfigs

def get_config_fields_dic(config, subconfig=None):

    configs = yaml.safe_load(open("Learnings_from_AeN_template_generator/config/template_configurations.yaml", encoding='utf-8'))['setups']
    #configs = yaml.safe_load(open("template_configurations.yaml", encoding='utf-8'))['setups']

    if subconfig:
        config_dict = configs[config][subconfig]['fields'][0]
    else:
        config_dict = configs[config]['fields'][0]

    return config_dict

def get_config_fields(config, subconfig=None):

    configs = yaml.safe_load(open("Learnings_from_AeN_template_generator/config/template_configurations.yaml", encoding='utf-8'))['setups']
    #configs = yaml.safe_load(open("template_configurations.yaml", encoding='utf-8'))['setups']

    if subconfig:
        config_dict = configs[config][subconfig]['fields'][0]
    else:
        config_dict = configs[config]['fields'][0]

    list_of_lists = list(config_dict.values())

    fields_in_config_list = []

    for sublist in list_of_lists:
        fields_in_config_list.extend(sublist)

    fields_in_config_dict = {}
    extra_fields_dict = {}
    groups = []

    # Loading in Nansen Legacy fields
    for field in fields.fields:
        if field['name'] in fields_in_config_list:
            fields_in_config_dict[field['name']] = {}
            fields_in_config_dict[field['name']]['disp_name'] = field['disp_name']
            fields_in_config_dict[field['name']]['description'] = field['description']
            fields_in_config_dict[field['name']]['format'] = field['format']
            #if field['valid']['validate'] == 'list' and field['name'] not in ['stationName']:
            #    table = field['valid']['source']
            #    df = pd.read_csv(f'Learnings_from_AeN_template_generator/config/{table}.csv')
            #    fields_in_config_dict[field['name']]['source'] = list(df[field['name'].lower()])

        else:
            extra_fields_dict[field['name']] = {}
            extra_fields_dict[field['name']]['disp_name'] = field['disp_name']
            extra_fields_dict[field['name']]['description'] = field['description']
            extra_fields_dict[field['name']]['format'] = field['format']
            extra_fields_dict[field['name']]['grouping'] = field['grouping']
            #if field['valid']['validate'] == 'list' and field['name'] not in ['stationName']:
            #    table = field['valid']['source']
            #    df = pd.read_csv(f'Learnings_from_AeN_template_generator/config/{table}.csv')
            #    extra_fields_dict[field['name']]['source'] = list(df[field['name'].lower()])

            groups.append(field['grouping'])

    groups = sorted(list(set(groups)))

    # Loading in CF standard names
    cf_standard_names = cf_standard_names_to_dic()

    for cf_standard_name in cf_standard_names:
        if cf_standard_name['id'] in fields_in_config_list:
            fields_in_config_dict[cf_standard_name['id']] = {}
            fields_in_config_dict[cf_standard_name['id']]['disp_name'] = cf_standard_name['id']
            if cf_standard_name['description'] == None:
                cf_standard_name['description'] = ''
            if cf_standard_name['id'] == 'time':
                cf_standard_name['description'] = 'Reference date/time.\nUnits should be specified in the format\ntime units since reference time\nwhere the time units can be\nseconds, hours, days, weeks, months, or years'
            fields_in_config_dict[cf_standard_name['id']]['description'] = f"{cf_standard_name['description']} \ncanonical units: {cf_standard_name['canonical_units']}"
            fields_in_config_dict[cf_standard_name['id']]['format'] = 'double_precision'

    # Creating a dictionary for the configuration that I can use
    output_config_dict = {}

    for key, value_list in config_dict.items():
        output_config_dict[key] = {}
        for value in value_list:
            if 'bounds' in value:
                output_config_dict[key][value] = {
                    'disp_name': value,
                    'description': 'For use when a data point does not represent a single point in space or time, but a cell of finite size. Use this variable to encode the extent of the cell (e.g. the minimum and maximum depth that a data point is representative of).',
                    'format': 'double_precision'
                    }
            else:
                output_config_dict[key][value] = fields_in_config_dict[value]

    return output_config_dict, fields_in_config_list, extra_fields_dict, cf_standard_names, groups

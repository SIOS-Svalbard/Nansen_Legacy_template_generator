import yaml
import sys
from os.path import os
config_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'config'))

sys.path.append(config_dir)
import fields as fields
from .pull_cf_standard_names import cf_standard_names_to_dic
from .pull_darwin_core_terms import dwc_terms_to_df
import pandas as pd

def get_list_of_configs():

    configs = yaml.safe_load(open("website/config/template_configurations.yaml", encoding='utf-8'))['setups']
    configs_list = []

    for config in configs:
        configs_list.append(config)

    return configs_list

def get_list_of_subconfigs(config):

    configs = yaml.safe_load(open("website/config/template_configurations.yaml", encoding='utf-8'))['setups']
    subconfigs = []

    if config in ['Learnings from Nansen Legacy logging system', 'Darwin Core']:
        for subconfig in configs[config]:
            subconfigs.append(subconfig)

    return subconfigs

def get_config_fields_dic(config, subconfig=None):

    configs = yaml.safe_load(open("website/config/template_configurations.yaml", encoding='utf-8'))['setups']

    # if subconfig:
    #     config_dict = configs[config][subconfig]['fields'][0]
    # else:
    #     config_dict = configs[config]['fields'][0]
    if subconfig:
        config_dict = configs[config][subconfig]
    else:
        config_dict = configs[config]

    return config_dict

def get_config_fields(config, subconfig=None):

    initial_config_dict = get_config_fields_dic(config,subconfig)

    fields_in_config_list = []

    if config == 'Darwin Core':
        config_dict = {} # Not used in this configuration
    else:
        config_dict = initial_config_dict['fields'][0]
        list_of_lists = list(config_dict.values())
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

    # Loading in Darwin Core terms

    dwc_terms_df = dwc_terms_to_df()

    dwc_terms_df['description'] = dwc_terms_df['rdfs_comment'] + '\n\n' + dwc_terms_df['dcterms_description']+ '\n\n' + dwc_terms_df['examples']
    dwc_terms_df['disp_name'] = dwc_terms_df['id'] = dwc_terms_df['term_localName']
    dwc_terms_df['format'] = 'text'

    dwc_terms_json = dwc_terms_df[['id', 'disp_name','description','format']].to_dict('records')

    if config == 'Darwin Core':
        dwc_subconfig = subconfig
    else:
        dwc_subconfig = 'Sampling Event'

    if config != 'CF-NetCDF': # Don't need Darwin Core terms for CF-NetCDF configuration
        dwc_conf_dict = get_dwc_config_dict(subconfig = dwc_subconfig, dwc_terms_df = dwc_terms_df)
    else:
        dwc_conf_dict = {}

    # Creating a dictionary for the configuration that I can use
    if config == 'Darwin Core':
        output_config_dict = dwc_conf_dict
        fields_in_config_list = []
        for core, criteria in dwc_conf_dict.items():
            for requirement, ii in criteria.items():
                if requirement not in ['Source', 'Required CSV']:
                    fields_in_config_list.extend(list(ii.keys()))
        # THE DWC CONF DICT NEEDS TO BE ALL THE TERMS MINUS WHAT IS IN FIELDS_IN_CONFIG_LIST

    else:
        output_config_dict = {'Data': {'Required CSV': True}}


        for key, value_list in config_dict.items():
            output_config_dict['Data'][key] = {}
            for value in value_list:
                if 'bounds' in value:
                    output_config_dict['Data'][key][value] = {
                        'disp_name': value,
                        'description': 'For use when a data point does not represent a single point in space or time, but a cell of finite size. Use this variable to encode the extent of the cell (e.g. the minimum and maximum depth that a data point is representative of).',
                        'format': 'double_precision'
                        }
                else:
                    output_config_dict['Data'][key][value] = fields_in_config_dict[value]

    return output_config_dict, fields_in_config_list, extra_fields_dict, cf_standard_names, groups, dwc_conf_dict, dwc_terms_json

def get_dwc_extension(source):
    df_extension = pd.read_xml(source)
    return df_extension

def get_dwc_terms_from_extension(df_extension):

    terms_dict = {}
    columns = df_extension.columns

    for idx, row in df_extension.iterrows():
        term = row['name']
        terms_dict[term] = {}

        terms_dict[term]['disp_name'] = term

        if 'group' in columns:
            terms_dict[term]['grouping'] = row['group']
        if 'type' in columns:
            if row['type'] == 'uri':
                terms_dict[term]['format'] = 'text'
            else: # row['type'] in ['date', 'integer', 'decimal']:
                terms_dict[term]['format'] = row['type']

        terms_dict[term]['description'] = row['description']

        if 'comments' in columns:
            terms_dict[term]['description'] = terms_dict[term]['description'] + '\n\n' + str(row['comments'])
        if 'examples' in columns:
            terms_dict[term]['description'] = terms_dict[term]['description'] + '\n\n' + 'Examples: ' + str(row['examples'])

    return terms_dict

def get_dwc_term_description_from_extension(term,df_extension):

    description = ''
    columns = df_extension.columns

    if 'comments' in columns:
        description = str(df_extension.loc[df_extension['name'] == term, 'comments'].values[0])
    try:
        description = description + '\n\nExamples: ' + str(df_extension.loc[df_extension['name'] == term, 'examples'].values[0])
    except:
        pass

def get_dwc_term_dict_from_df(term,df):
    terms_dict = {}

    # Rewrite so doesn't fail if no value for certain term
    try:
        terms_dict['description'] = str(df.loc[df['term_localName'] == term, 'rdfs_comment'].values[0])
    except:
        terms_dict['description'] = ''

    try:
        terms_dict['description'] = terms_dict['description'] + '\n\n' + str(df.loc[df['term_localName'] == term, 'dcterms_description'].values[0])
    except:
        pass

    try:
        terms_dict['description'] = terms_dict['description'] + '\n\nExamples: ' + str(df.loc[df['term_localName'] == term, 'examples'].values[0])
    except:
        pass

    terms_dict['disp_name'] = term
    terms_dict['format'] = 'text'

    return terms_dict


def get_dwc_config_dict(subconfig, dwc_terms_df):

    config_dict = yaml.safe_load(open("website/config/template_configurations.yaml", encoding='utf-8'))['setups']['Darwin Core'][subconfig]

    output_config_dict = {}
    for extension in config_dict.keys():
        criteria = config_dict[extension]['fields'][0]
        output_config_dict[extension] = {}
        source = config_dict[extension]['Source']

        output_config_dict[extension]['Required CSV'] = config_dict[extension]['Required CSV']
        output_config_dict[extension]['Source'] = source

        df_extension = get_dwc_extension(source)

        for key, value in criteria.items():
            output_config_dict[extension][key] = {}
            if value != 'from source':
                for term in value:
                    output_config_dict[extension][key][term] = get_dwc_term_dict_from_df(term,dwc_terms_df)
                    if output_config_dict[extension][key][term]['description'] == '':
                        output_config_dict[extension][key][term]['description'] = get_dwc_term_description_from_extension(term,df_extension)
            else:
                output_config_dict[extension][key] = get_dwc_terms_from_extension(df_extension)

        # Removing fields from recommended that are already in required
        for field in output_config_dict[extension]['Required'].keys():
            output_config_dict[extension]['Recommended'].pop(field, None)

        # Removing fields from other that are already in required or recommended
        if 'Other' in output_config_dict[extension].keys():
            for field in output_config_dict[extension]['Required'].keys():
                output_config_dict[extension]['Other'].pop(field, None)
            for field in output_config_dict[extension]['Recommended'].keys():
                output_config_dict[extension]['Other'].pop(field, None)

    return output_config_dict, dwc_terms_json

# #%%

# for sheet in output_config_dict.keys():
#     print('\n', sheet)
#     if 'Required CSV' in output_config_dict[sheet].keys():
#         for col, fields in output_config_dict[sheet].items():
#             if col not in ['Required CSV', 'Source']:
#                 print('\n',col)
#                 for key, field in fields.items():
#                     print('Key: ',key)
#                     print('disp_name: ', field['disp_name'])
#                     print('Description: ', field['description'])

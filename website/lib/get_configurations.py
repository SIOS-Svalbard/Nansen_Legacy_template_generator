import yaml
#import sys
#from os.path import os
# config_dir = os.path.abspath(os.path.join(
#     os.path.dirname(__file__), '..', 'config'))

# sys.path.append(config_dir)
from .pull_cf_standard_names import cf_standard_names_to_dic
from .pull_other_fields import other_fields_to_dic
from .pull_darwin_core_terms import dwc_terms_to_dic, dwc_extension_to_dic

CONFIG_PATH = 'website/config/template_configurations.yaml'

def get_list_of_configs():

    configs = yaml.safe_load(open(CONFIG_PATH, encoding='utf-8'))['setups']
    configs_list = []

    for config in configs:
        configs_list.append(config)

    return configs_list

def get_list_of_subconfigs(config):

    configs = yaml.safe_load(open(CONFIG_PATH, encoding='utf-8'))['setups']
    subconfigs = []

    if config in ['Learnings from Nansen Legacy logging system', 'Darwin Core']:
        for subconfig in configs[config]:
            subconfigs.append(subconfig)

    return subconfigs

def get_config_fields_dic(config, subconfig=None):

    configs = yaml.safe_load(open(CONFIG_PATH, encoding='utf-8'))['setups']

    if subconfig:
        config_dict = configs[config][subconfig]
    else:
        config_dict = configs[config]

    return config_dict

def get_config_fields(fields_filepath, config, subconfig=None):

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

    other_fields = other_fields_to_dic(fields_filepath)
    cf_standard_names = cf_standard_names_to_dic(fields_filepath)
    dwc_terms = dwc_terms_to_dic(fields_filepath)

    all_fields = other_fields + cf_standard_names + dwc_terms

    cf_standard_names = [cf_standard_name for cf_standard_name in cf_standard_names if cf_standard_name['id'] not in fields_in_config_list]

    for field in all_fields:
        if field['id'] in fields_in_config_list:
            fields_in_config_dict[field['id']] = field

    for field in other_fields:
        if field['id'] not in fields_in_config_list:
            extra_fields_dict[field['id']] = field
            groups.append(field['grouping'])
    groups = sorted(list(set(groups)))

    if config == 'Darwin Core':
        dwc_subconfig = subconfig
    else:
        dwc_subconfig = 'Sampling Event'
    dwc_conf_dict = get_dwc_config_dict(fields_filepath = fields_filepath, subconfig = dwc_subconfig, dwc_terms = dwc_terms)

    # Creating a dictionary for the configuration that I can use
    if config == 'Darwin Core':
        output_config_dict = dwc_conf_dict
        fields_in_config_list = []
        for core, criteria in dwc_conf_dict.items():
            for requirement, ii in criteria.items():
                if requirement not in ['Source', 'Required CSV']:
                    fields_in_config_list.extend(list(ii.keys()))
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

    return output_config_dict, fields_in_config_list, extra_fields_dict, cf_standard_names, groups, dwc_terms

def get_dwc_config_dict(fields_filepath, subconfig, dwc_terms):

    config_dict = yaml.safe_load(open(CONFIG_PATH, encoding='utf-8'))['setups']['Darwin Core'][subconfig]

    output_config_dict = {}
    for extension in config_dict.keys():
        criteria = config_dict[extension]['fields'][0]
        output_config_dict[extension] = {}
        source = config_dict[extension]['Source']

        output_config_dict[extension]['Required CSV'] = config_dict[extension]['Required CSV']
        output_config_dict[extension]['Source'] = source

        dwc_extension = dwc_extension_to_dic(fields_filepath, extension)

        for key, value in criteria.items():
            output_config_dict[extension][key] = {}
            if value != 'from source':
                for term in value:
                    # validation from extension, as extension has information about the type (integer, decimal..)
                    # description from main as it contains more information more reliably.
                    # Sometimes the term is not in the extension or vice versa. This is possible when 'eventID' needs to be in an extension, for example.
                    try:
                        output_config_dict[extension][key][term] = get_dwc_term_dict_from_main(term,dwc_terms)
                    except:
                        output_config_dict[extension][key][term] = get_dwc_term_dict_from_extension(term,dwc_extension)

                    if output_config_dict[extension][key][term]['description'] == '':
                        output_config_dict[extension][key][term]['description'] = get_dwc_term_description_from_extension(term,dwc_extension)
                    try:
                        output_config_dict[extension][key][term]['valid'] = get_validation_from_extension(term, dwc_extension)
                    except:
                        pass
            else:
                try:
                    output_config_dict[extension][key] = get_dwc_terms_from_extension(dwc_extension)
                except:
                    pass

        # Removing fields from recommended that are already in required
        for field in output_config_dict[extension]['Required'].keys():
            output_config_dict[extension]['Recommended'].pop(field, None)

        # Removing fields from other that are already in required or recommended
        if 'Other' in output_config_dict[extension].keys():
            for field in output_config_dict[extension]['Required'].keys():
                output_config_dict[extension]['Other'].pop(field, None)
            for field in output_config_dict[extension]['Recommended'].keys():
                output_config_dict[extension]['Other'].pop(field, None)

    return output_config_dict

def get_dwc_term_dict_from_main(term,dwc_terms):

    terms_dict = [dic for dic in dwc_terms if dic['id'] == term][0]

    return terms_dict

def get_dwc_term_dict_from_extension(term,dwc_extension):

    terms_dict = [dic for dic in dwc_extension if dic['id'] == term][0]

    return terms_dict

def get_dwc_term_description_from_extension(term,dwc_extension):

    terms_dict = [dic for dic in dwc_extension if dic['id'] == term][0]
    description = terms_dict['description']

    return description

def get_validation_from_extension(term,dwc_extension):

    terms_dict = [dic for dic in dwc_extension if dic['id'] == term]
    validation = terms_dict[0]['valid']

    return validation

def get_dwc_terms_from_extension(dwc_extension):

    terms_dict = {}

    for term in dwc_extension:
        terms_dict[term['id']] = term

    return terms_dict

def get_field_requirements(fields_filepath, config, subconfig, sheetname):
    '''
    Get field requirements for template generator
    Dictates how column headers are formatted (colour coded)
    '''
    config_dict = get_config_fields_dic(config=config, subconfig=subconfig)

    cf_standard_names = cf_standard_names_to_dic(fields_filepath)
    cf_standard_names = [cf_standard_name['id'] for cf_standard_name in cf_standard_names]

    dwc_terms_dic = dwc_terms_to_dic(fields_filepath)
    dwc_terms = [term['term_localName'] for term in dwc_terms_dic]

    if config == 'Learnings from Nansen Legacy logging system':
        required_fields = config_dict['fields'][0]['Required']
        recommended_fields = config_dict['fields'][0]['Recommended']
        dwc_terms = [term for term in dwc_terms if term not in required_fields and term not in recommended_fields]
        cf_standard_names = [term for term in cf_standard_names if term not in required_fields and term not in recommended_fields]
    elif config == 'Darwin Core':
        required_fields = config_dict[sheetname]['fields'][0]['Required']
        recommended_fields = config_dict[sheetname]['fields'][0]['Recommended']
        dwc_terms = [term for term in dwc_terms if term not in required_fields and term not in recommended_fields]
    elif config == 'CF-NetCDF':
        required_fields = []
        recommended_fields = []

    return (
    required_fields,
    recommended_fields,
    dwc_terms,
    cf_standard_names,
    )

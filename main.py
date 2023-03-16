#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from website import create_app
from website.lib.template import print_html_template
from website.lib.get_configurations import *

app = create_app()

@app.route('/', methods=['GET'])
def home():

    # if 'select-config' in form:
    #     config = form.getvalue('select-config')
    # else:
    #     config = 'CF-NetCDF'

    # if config == 'Learnings from Nansen Legacy logging system':
    #     if 'select-subconfig' in form:
    #         subconfig = form.getvalue('select-subconfig')
    #     else:
    #         subconfig = 'default'
    # else:
    #     subconfig = None

    config = 'CF-NetCDF'
    subconfig = None

    list_of_configs = get_list_of_configs()
    list_of_subconfigs = get_list_of_subconfigs(config = config)

    # Getting setup specific to this configuration
    output_config_dict, output_config_fields, extra_fields_dict, cf_standard_names, groups = get_config_fields(config = config, subconfig = subconfig)

    # Creating a dictionary of all the fields.
    all_fields_dict = extra_fields_dict.copy()

    for key in output_config_dict.keys():
        for field, values in output_config_dict[key].items():
            all_fields_dict[field] = values

    cf_groups = ['sea_water','sea_ice']
    added_fields_dic = {}
    added_cf_names_dic = {}
    fields_list = [] # List of fields selected - dictates columns in template

    return print_html_template(
        output_config_dict = output_config_dict,
        extra_fields_dict = extra_fields_dict,
        groups = groups,
        added_fields_dic = added_fields_dic,
        cf_standard_names = cf_standard_names,
        cf_groups = cf_groups,
        added_cf_names_dic = added_cf_names_dic,
        list_of_configs = list_of_configs,
        list_of_subconfigs=list_of_subconfigs,
        config=config,
        subconfig=subconfig
    )



if __name__ == '__main__':
    app.run(debug=True)

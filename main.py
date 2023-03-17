#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from website import create_app
from website.lib.template import print_html_template
from website.lib.get_configurations import *
from flask import request, send_file
from website.lib.make_xlsx import write_file

app = create_app()

@app.route('/', methods=['GET', 'POST'])
def home():

    config = request.form.get("select-config", "CF-NetCDF")

    if config == 'Learnings from Nansen Legacy logging system':
        subconfig = request.form.get("select-subconfig", "default")
    else:
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

    if request.method == 'GET':

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

    if request.form['submitbutton'] not in ['selectConfig', 'selectSubConfig']:
        for field in cf_standard_names:
            if field['id'] in request.form and field['id'] not in output_config_fields:
                fields_list.append(field['id'])
                added_cf_names_dic[field['id']] = {}
                added_cf_names_dic[field['id']]['disp_name'] = field['id']
                if field['description'] == None:
                      field['description'] = ''
                added_cf_names_dic[field['id']]['description'] = f"{field['description']} \ncanonical units: {field['canonical_units']}"
                added_cf_names_dic[field['id']]['format'] = 'double precision'

        for field in all_fields_dict.keys():
            if field in request.form:
                if field not in added_cf_names_dic.keys():
                    fields_list.append(field)
                    if field in extra_fields_dict.keys():
                        added_fields_dic[field] = extra_fields_dict[field]

        for key in output_config_dict.keys():
            for field, values in output_config_dict[key].items():
                if field in request.form:
                    output_config_dict[key][field]['checked'] = 'yes'

        if request.form['submitbutton'] == 'generateTemplate':
            filepath = '/tmp/LFNL_template.xlsx'
            write_file(filepath, fields_list, metadata=True, conversions=True, configuration=config, subconfiguration=subconfig)
            return send_file(filepath, as_attachment=True)

        else:
            return print_html_template(output_config_dict = output_config_dict, extra_fields_dict = extra_fields_dict, groups = groups, added_fields_dic = added_fields_dic, cf_standard_names = cf_standard_names, cf_groups = cf_groups, added_cf_names_dic = added_cf_names_dic, list_of_configs = list_of_configs, list_of_subconfigs=list_of_subconfigs, config=config, subconfig=subconfig)
    else:
        return print_html_template(output_config_dict = output_config_dict, extra_fields_dict = extra_fields_dict, groups = groups, added_fields_dic = added_fields_dic, cf_standard_names = cf_standard_names, cf_groups = cf_groups, added_cf_names_dic = added_cf_names_dic, list_of_configs = list_of_configs, list_of_subconfigs=list_of_subconfigs, config=config, subconfig=subconfig)


if __name__ == '__main__':
    app.run(debug=True)

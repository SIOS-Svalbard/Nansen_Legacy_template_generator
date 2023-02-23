#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 14:36:16 2022

@author: lukem
"""

#import config.fields as fields
#import config.metadata_fields as metadata_fields
#import spreadsheet.make_xlsx as mx
import Learnings_from_AeN_template_generator.spreadsheet.make_xlsx as mx
from Learnings_from_AeN_template_generator.config.get_configurations import *
from Learnings_from_AeN_template_generator.config.pull_cf_standard_names import cf_standard_names_to_dic
import cgi
import cgitb
import http.cookies as Cookie
import tempfile
from mako.lookup import TemplateLookup
import shutil
import os
import sys
from mako.template import Template

def print_html_template(output_config_dict, extra_fields_dict, groups, added_fields_dic, cf_standard_names, cf_groups, added_cf_names_dic, list_of_configs, config, list_of_subconfigs=None, subconfig=None):
    '''
    Prints the html template. Excluding closing the <main> element which must be closed at the bottom of this script
    '''
    if len(added_fields_dic) > 0:
        added_fields_bool = True
    else:
        added_fields_bool = False

    if len(added_cf_names_dic) > 0:
        added_cf_names_bool = True
    else:
        added_cf_names_bool = False

    if config == 'CF-NetCDF':
        description = 'Create spreadsheet templates that are easy to convert to CF-NetCDF files.'
    elif config == 'Learnings from Nansen Legacy logging system':
        description = 'Create spreadsheet templates that can be used in combination with the Learnings from Nansen Legacy logging system.'

    template = templates.get_template("generateTemplateIsolated.html")
    sys.stdout.flush()
    sys.stdout.buffer.write(b"Content-Type: text/html\n\n")

    sys.stdout.buffer.write(template.render(output_config_dict = output_config_dict, extra_fields_dict = extra_fields_dict, groups = groups, added_fields_dic = added_fields_dic, added_fields_bool = added_fields_bool, cf_standard_names=cf_standard_names, cf_groups=cf_groups, added_cf_names_dic=added_cf_names_dic, added_cf_names_bool=added_cf_names_bool, list_of_configs=list_of_configs, list_of_subconfigs=list_of_subconfigs, config=config, subconfig=subconfig, description=description))

cgitb.enable() # comment out when not developing tool

cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

method = os.environ.get("REQUEST_METHOD", "GET")

templates = TemplateLookup(directories = ['templates'], output_encoding='utf-8')

form = cgi.FieldStorage()

if 'select-config' in form:
    config = form.getvalue('select-config')
else:
    config = 'CF-NetCDF'

if config == 'Learnings from Nansen Legacy logging system':
    if 'select-subconfig' in form:
        subconfig = form.getvalue('select-subconfig')
    else:
        subconfig = 'default'
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

if method == "POST":

    if form['submitbutton'].value not in ['selectConfig', 'selectSubConfig']:

        # for field in extra_fields_dict.keys():
        #     if field in form:
        #         fields_list.append(field)

        for field in cf_standard_names:
            if field['id'] in form and field['id'] not in output_config_fields:
                fields_list.append(field['id'])
                added_cf_names_dic[field['id']] = {}
                added_cf_names_dic[field['id']]['disp_name'] = field['id']
                if field['description'] == None:
                      field['description'] = ''
                added_cf_names_dic[field['id']]['description'] = f"{field['description']} \ncanonical units: {field['canonical_units']}"
                added_cf_names_dic[field['id']]['format'] = 'double precision'

        for field in all_fields_dict.keys():
            if field in form:
                if field not in added_cf_names_dic.keys():
                    fields_list.append(field)
                    if field in extra_fields_dict.keys():
                        added_fields_dic[field] = extra_fields_dict[field]

        for key in output_config_dict.keys():
            for field, values in output_config_dict[key].items():
                if field in form:
                    output_config_dict[key][field]['checked'] = 'yes'

        if form['submitbutton'].value == 'generateTemplate':

            outputFileName = 'LFNL_template.xlsx'

            print("Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            print("Content-Disposition: attachment; filename="+outputFileName+"\n")
            path = "/tmp/" + next(tempfile._get_candidate_names()) + '.xlsx'

            mx.write_file(path, fields_list, metadata=True, conversions=True, configuration=config, subconfiguration=subconfig)

            with open(path, "rb") as f:
                sys.stdout.flush()
                shutil.copyfileobj(f, sys.stdout.buffer)

        else:
            print_html_template(output_config_dict = output_config_dict, extra_fields_dict = extra_fields_dict, groups = groups, added_fields_dic = added_fields_dic, cf_standard_names = cf_standard_names, cf_groups = cf_groups, added_cf_names_dic = added_cf_names_dic, list_of_configs = list_of_configs, list_of_subconfigs=list_of_subconfigs, config=config, subconfig=subconfig)

    else:
        print_html_template(output_config_dict = output_config_dict, extra_fields_dict = extra_fields_dict, groups = groups, added_fields_dic = added_fields_dic, cf_standard_names = cf_standard_names, cf_groups = cf_groups, added_cf_names_dic = added_cf_names_dic, list_of_configs = list_of_configs, list_of_subconfigs=list_of_subconfigs, config=config, subconfig=subconfig)

elif method == "GET":
    print_html_template(output_config_dict = output_config_dict, extra_fields_dict = extra_fields_dict, groups = groups, added_fields_dic = added_fields_dic, cf_standard_names = cf_standard_names, cf_groups = cf_groups, added_cf_names_dic = added_cf_names_dic, list_of_configs = list_of_configs, list_of_subconfigs=list_of_subconfigs, config=config, subconfig=subconfig)

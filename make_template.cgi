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
from Learnings_from_AeN_template_generator.config.get_configurations import get_fields
from Learnings_from_AeN_template_generator.config.pull_cf_standard_names import create_cf_standard_names_json
import cgi
import cgitb
import http.cookies as Cookie
import tempfile
from mako.lookup import TemplateLookup
import shutil
import os
import sys
from mako.template import Template

def print_html_template(required_fields_dic, recommended_fields_dic, extra_fields_dic, groups, added_fields_dic, cf_standard_names, cf_groups, added_cf_names_dic):
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
        
    template = templates.get_template("generateTemplateIsolated.html")
    sys.stdout.flush()
    sys.stdout.buffer.write(b"Content-Type: text/html\n\n")
    
    sys.stdout.buffer.write(template.render(required_fields_dic = required_fields_dic, recommended_fields_dic = recommended_fields_dic, extra_fields_dic = extra_fields_dic, groups = groups, added_fields_dic = added_fields_dic, added_fields_bool = added_fields_bool, cf_standard_names=cf_standard_names, cf_groups=cf_groups, added_cf_names_dic=added_cf_names_dic, added_cf_names_bool=added_cf_names_bool))


cgitb.enable() # comment out when not developing tool

cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

method = os.environ.get("REQUEST_METHOD", "GET")

templates = TemplateLookup(directories = ['Learnings_from_AeN_template_generator/templates'], output_encoding='utf-8')

config = 'other'

required_fields_dic, recommended_fields_dic, extra_fields_dic, groups = get_fields(configuration=config)
all_fields_dic = {**required_fields_dic, **recommended_fields_dic, **extra_fields_dic}

cf_standard_names, cf_groups = create_cf_standard_names_json()

added_fields_dic = {}
added_cf_names_dic = {}

fields_list = []
form = cgi.FieldStorage()

for field in all_fields_dic.keys():
    if field in form:
        fields_list.append(field)
        if field not in required_fields_dic.keys() and field not in recommended_fields_dic.keys():
            added_fields_dic[field] = extra_fields_dic[field]

for field in cf_standard_names:
    if field['id'] in form:
        fields_list.append(field['id'])
        added_cf_names_dic[field['id']] = {}
        added_cf_names_dic[field['id']]['disp_name'] = field['id']
        added_cf_names_dic[field['id']]['description'] = field['description']
        
        
if method == "POST":


    if form['submitbutton'].value == 'generateTemplate':
        
        outputFileName = 'LFNL_template.xlsx'
   
        print("Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        print("Content-Disposition: attachment; filename="+outputFileName+"\n")
        path = "/tmp/" + next(tempfile._get_candidate_names()) + '.xlsx'
        
        mx.write_file(path, fields_list, metadata=True, conversions=True, configuration=config)
        
        with open(path, "rb") as f:
            sys.stdout.flush()
            shutil.copyfileobj(f, sys.stdout.buffer)
            
    else:
        
        print_html_template(required_fields_dic = required_fields_dic, recommended_fields_dic = recommended_fields_dic, extra_fields_dic = extra_fields_dic, groups = groups, added_fields_dic = added_fields_dic, cf_standard_names=cf_standard_names, cf_groups=cf_groups, added_cf_names_dic=added_cf_names_dic)

elif method == "GET":
    print_html_template(required_fields_dic = required_fields_dic, recommended_fields_dic = recommended_fields_dic, extra_fields_dic = extra_fields_dic, groups = groups, added_fields_dic = added_fields_dic, cf_standard_names = cf_standard_names, cf_groups = cf_groups, added_cf_names_dic = added_cf_names_dic)


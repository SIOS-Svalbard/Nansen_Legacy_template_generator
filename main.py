#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import request, send_file, render_template, flash, redirect, url_for, session, request
import os
from website import create_app
from website.lib.template import print_html_template
from website.lib.get_configurations import *
from website.lib.create_template import create_template
from website.lib.pull_cf_standard_names import cf_standard_names_update
from website.lib.pull_global_attributes import global_attributes_update
from website.lib.dropdown_lists_from_static_config_files import populate_dropdown_lists
from website.lib.pull_darwin_core_terms import dwc_terms_update, get_dwc_extension_description
from website.lib.usage_stats import log_template, log_visit

app = create_app()

# Get the directory of the currently running script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'visits.db')

@app.route("/", methods=["GET", "POST"])
def home_redirect():
    return redirect(url_for("home", config='CF-NetCDF'))

@app.route("/config=<config>", methods=["GET", "POST"])
def home(config):

    ip_address = request.remote_addr  # Get visitor's IP address

    # Select or change configuration
    config = request.form.get("select-config", config)
    subconfig = session.get('subconfig')

    list_of_configs = get_list_of_configs()
    list_of_subconfigs = get_list_of_subconfigs(config=config)

    if subconfig is None or subconfig not in list_of_subconfigs:
        if config == "Nansen Legacy logging system":
            subconfig = request.form.get("select-subconfig", "default")
            if subconfig not in list_of_subconfigs:
                subconfig = 'Activities'
        elif config == 'Darwin Core':
            subconfig = request.form.get("select-subconfig", "Sampling Event")
            if subconfig not in list_of_subconfigs:
                subconfig = 'Sampling Event'

    if config == 'CF-NetCDF':
        subconfig = None

    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    FIELDS_FILEPATH = os.path.join(BASE_PATH, 'website', 'config', 'fields')

    # Getting setup specific to this configuration
    (
        output_config_dict,
        output_config_fields,
        extra_fields_dict,
        cf_standard_names,
        groups,
        dwc_terms
    ) = get_config_fields(fields_filepath=FIELDS_FILEPATH, config=config, subconfig=subconfig)

    sheets_descriptions = {}
    for sheet in output_config_dict.keys():
        for key in output_config_dict[sheet].keys():
            if key not in ['Required CSV', 'Source']:
                fields_dict = output_config_dict[sheet][key]
                output_config_dict[sheet][key] = populate_dropdown_lists(fields_dict, config)

        if config == 'Darwin Core':
            sheets_descriptions[sheet] = get_dwc_extension_description(FIELDS_FILEPATH, sheet)
        elif config == 'CF-NetCDF':
            sheets_descriptions[sheet] = 'Template for data and metadata to be encoded in a CF-NetCDF file'
        else:
            sheets_descriptions[sheet] = None

    extra_fields_dict = populate_dropdown_lists(extra_fields_dict, config)
    dwc_terms = populate_dropdown_lists(dwc_terms, config)
    cf_standard_names = populate_dropdown_lists(cf_standard_names, config)

    # Creating a dictionary of all the fields.
    all_fields_dict = extra_fields_dict.copy()

    compulsary_sheets = []

    for sheet in output_config_dict.keys():
        if output_config_dict[sheet]['Required CSV'] == True:
            compulsary_sheets.append(sheet)
        added_sheet = request.form.get("submitbutton", None)
        if 'add_'+sheet == added_sheet:
            output_config_dict[sheet]['Required CSV'] = True
        for key, val in request.form.items():
            if key.startswith(sheet):
                output_config_dict[sheet]['Required CSV'] = True
        if 'remove_'+sheet == added_sheet:
            output_config_dict[sheet]['Required CSV'] = False
        for key in output_config_dict[sheet].keys():
            if key not in ['Required CSV', 'Source']:
                for field, values in output_config_dict[sheet][key].items():
                    all_fields_dict[field] = values

    cf_groups = ["sea_water", "sea_ice"]
    added_fields_dic = {}
    added_cf_names_dic = {}
    added_dwc_terms_dic = {}
    fields_list = []  # List of fields selected - dictates columns in template
    template_fields_dict = {} # Dictionary of fields. All info needed for spreadsheet template.
    dwc_terms_by_sheet = {} # Separate dictionary of dwc terms for each sheet. Not including required or recommended terms in each sheet.

    for sheet in output_config_dict.keys():
        if output_config_dict[sheet]['Required CSV'] == True:
            template_fields_dict[sheet] = {}
            added_cf_names_dic[sheet] = {}
            added_dwc_terms_dic[sheet] = {}
            added_fields_dic[sheet] = {}
            dwc_terms_tmp = dwc_terms
            for key in output_config_dict[sheet].keys():
                if key not in ['Required CSV', 'Source']:
                    fields_accounted_for = output_config_dict[sheet][key].keys()
                    idxs_to_remove = []
                    for idx, dwc_term in enumerate(dwc_terms_tmp):
                        if dwc_term['id'] in fields_accounted_for:
                            idxs_to_remove.append(idx)
                    dwc_terms_to_keep = [dwc_terms_tmp[i] for i in range(len(dwc_terms_tmp)) if i not in idxs_to_remove]
                    dwc_terms_tmp = dwc_terms_to_keep
            dwc_terms_by_sheet[sheet] = dwc_terms_tmp

    if request.method == "GET":

        log_visit(ip_address, DB_PATH)

        return print_html_template(
            output_config_dict=output_config_dict,
            extra_fields_dict=extra_fields_dict,
            groups=groups,
            added_fields_dic=added_fields_dic,
            cf_standard_names=cf_standard_names,
            cf_groups=cf_groups,
            added_cf_names_dic=added_cf_names_dic,
            dwc_terms_by_sheet=dwc_terms_by_sheet,
            added_dwc_terms_dic=added_dwc_terms_dic,
            list_of_configs=list_of_configs,
            list_of_subconfigs=list_of_subconfigs,
            config=config,
            subconfig=subconfig,
            compulsary_sheets=compulsary_sheets,
            sheets_descriptions = sheets_descriptions
        )

    if 'submitbutton' in request.form:

        all_form_keys = list(request.form.keys())

        # Removing bounds key if coordinate not selected
        keys_to_remove = []
        key_set = set(all_form_keys)

        for key in all_form_keys:
            if key.endswith('_bounds'):
                # Check if a corresponding key without '_bounds' exists
                base_key = key[:-len('_bounds')]
                if base_key not in key_set:
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            all_form_keys.remove(key)

        # CF standard names
        for field in cf_standard_names:
            for sheet in template_fields_dict.keys():
                for form_key in all_form_keys:
                    if form_key.startswith(sheet):
                        form_field = form_key.split('__')[1]
                        if field['id'] == form_field and field['id'] not in output_config_dict[sheet]:
                            template_fields_dict[sheet][field['id']] = {}
                            template_fields_dict[sheet][field['id']]['disp_name'] = field['id']
                            template_fields_dict[sheet][field['id']]['valid'] = field['valid']
                            if field["description"] == None:
                                field["description"] = ""
                            template_fields_dict[sheet][field['id']]['description'] = f"{field['description']} \ncanonical units: {field['canonical_units']}"
                            template_fields_dict[sheet][field['id']]['format'] = "double precision"
                            added_cf_names_dic[sheet][field['id']] = template_fields_dict[sheet][field['id']]

        # DWC terms
        for sheet in dwc_terms_by_sheet.keys():
            for term in dwc_terms_by_sheet[sheet]:
                for form_key in all_form_keys:
                    if form_key.startswith(sheet):
                        form_field = form_key.split('__')[1]
                        if term['id'] == form_field and term['id'] not in output_config_dict[sheet]:
                            template_fields_dict[sheet][term['id']] = {}
                            template_fields_dict[sheet][term['id']]['disp_name'] = term['id']
                            if term["description"] == None:
                                term["description"] = ""
                            template_fields_dict[sheet][term['id']]['description'] = term['description']
                            template_fields_dict[sheet][term['id']]['format'] = "double precision"
                            template_fields_dict[sheet][term['id']]['valid'] = term['valid']
                            added_dwc_terms_dic[sheet][term['id']] = template_fields_dict[sheet][term['id']]

        # Other fields (not CF standard names or DwC terms - terms designed for the template generator and logging system)
        for sheet in template_fields_dict.keys():
            for form_key in all_form_keys:
                if form_key.startswith(sheet):
                    form_field = form_key.split('__')[1]
                    if form_field not in added_cf_names_dic[sheet].keys() and form_field not in added_dwc_terms_dic[sheet].keys():
                        template_fields_dict[sheet][form_field] = all_fields_dict[form_field] # fields to write to template
                        if form_field in extra_fields_dict.keys():
                            added_fields_dic[sheet][form_field] = extra_fields_dict[form_field] # Extra fields added to template generator interface by user

        for sheet in output_config_dict.keys():
            for key in output_config_dict[sheet].keys():
                if key not in ['Required CSV', 'Source']:
                    for field, values in output_config_dict[sheet][key].items():
                        if sheet + '__' + field in request.form:
                            output_config_dict[sheet][key][field]["checked"] = "yes"

        if request.form["submitbutton"] == "generateTemplate":

            sheets = template_fields_dict.keys()

            sheets_info = {}
            for sheet in sheets:
                sheets_info[sheet] = {
                    'description': sheets_descriptions[sheet]
                }
                if 'Source' in output_config_dict[sheet].keys():
                    sheets_info[sheet]['source'] = output_config_dict[sheet]['Source']
                else:
                    sheets_info[sheet]['source'] = None

            log_template(ip_address, config, subconfig, sheets, DB_PATH)

            filepath = "/tmp/Nansen_Legacy_template.xlsx"

            if config == 'Darwin Core':
                metadata = False
            else:
                metadata = True

            create_template(
                filepath,
                template_fields_dict,
                sheets_info,
                FIELDS_FILEPATH,
                config,
                subconfig,
                conversions=True,
                metadata = metadata
            )
            return send_file(filepath, as_attachment=True)

        else:
            return print_html_template(
                output_config_dict=output_config_dict,
                extra_fields_dict=extra_fields_dict,
                groups=groups,
                added_fields_dic=added_fields_dic,
                cf_standard_names=cf_standard_names,
                cf_groups=cf_groups,
                added_cf_names_dic=added_cf_names_dic,
                dwc_terms_by_sheet=dwc_terms_by_sheet,
                added_dwc_terms_dic=added_dwc_terms_dic,
                list_of_configs=list_of_configs,
                list_of_subconfigs=list_of_subconfigs,
                config=config,
                subconfig=subconfig,
                compulsary_sheets=compulsary_sheets,
                sheets_descriptions = sheets_descriptions
            )
    elif 'select-config' in request.form:

        config = request.form.get('select-config')
        subconfig = request.form.get('select-subconfig')
        # Store subconfig in the session
        session['subconfig'] = subconfig

        return redirect(url_for("home", config=config))

    else:

        return print_html_template(
            output_config_dict=output_config_dict,
            extra_fields_dict=extra_fields_dict,
            groups=groups,
            added_fields_dic=added_fields_dic,
            cf_standard_names=cf_standard_names,
            cf_groups=cf_groups,
            added_cf_names_dic=added_cf_names_dic,
            dwc_terms_by_sheet=dwc_terms_by_sheet,
            added_dwc_terms_dic=added_dwc_terms_dic,
            list_of_configs=list_of_configs,
            list_of_subconfigs=list_of_subconfigs,
            config=config,
            subconfig=subconfig,
            compulsary_sheets=compulsary_sheets,
            sheets_descriptions = sheets_descriptions
        )

@app.route("/update", methods=["GET", "POST"])
def update_config():
    """
    updates the DwC terms, global attributes and the CF standard names
    in the config directory.
    """
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    FIELDS_FILEPATH = os.path.join(BASE_PATH, 'website', 'config', 'fields')

    if request.method == "POST":

        if request.form["submitbutton"] == "pullCF":
            errors = cf_standard_names_update(FIELDS_FILEPATH)
            if len(errors) == 0:
                flash('Pulled latest version of CF standard names', category='success')
            else:
                for error in errors:
                    flash(error, category='error')

        elif request.form["submitbutton"] == "pullDwC":
            errors = dwc_terms_update(FIELDS_FILEPATH)
            if len(errors) == 0:
                flash('Pulled latest version of Darwin Core terms', category='success')
            else:
                for error in errors:
                    flash(error, category='error')

        elif request.form["submitbutton"] == "pullGlobal":
            errors = global_attributes_update(FIELDS_FILEPATH)
            if len(errors) == 0:
                flash('Pulled latest version of global attributes', category='success')
            else:
                for error in errors:
                    flash(error, category='error')

    return render_template(
        "update_terms.html"
    )

if __name__ == "__main__":
    app.run(debug=True)

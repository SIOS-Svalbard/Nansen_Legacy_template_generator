#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import request, send_file
import json

from website import create_app
from website.lib.template import print_html_template
from website.lib.get_configurations import *
from website.lib.make_xlsx import write_file
from website.lib.pull_cf_standard_names import cf_standard_names_update
from website.lib.pull_acdd_conventions import acdd_conventions_update

app = create_app()


@app.route("/", methods=["GET", "POST"])
def home():

    # Select or change configuration
    config = request.form.get("select-config", "CF-NetCDF")

    list_of_configs = get_list_of_configs()
    list_of_subconfigs = get_list_of_subconfigs(config=config)

    if config == "Learnings from Nansen Legacy logging system":
        subconfig = request.form.get("select-subconfig", "default")
        if subconfig not in list_of_subconfigs:
            subconfig = 'default'
    elif config == 'Darwin Core':
        subconfig = request.form.get("select-subconfig", "Sampling Event")
        if subconfig not in list_of_subconfigs:
            subconfig = 'Sampling Event'
    else:
        subconfig = None

    # Getting setup specific to this configuration
    (
        output_config_dict,
        output_config_fields,
        extra_fields_dict,
        cf_standard_names,
        groups,
        dwc_conf_dict
    ) = get_config_fields(config=config, subconfig=subconfig)

    # Creating a dictionary of all the fields.
    all_fields_dict = extra_fields_dict.copy()
    sheets = []

    for sheet in output_config_dict.keys():
        added_sheet = request.form.get("submitbutton", None)
        if 'add_'+sheet == added_sheet:
            output_config_dict[sheet]['Required CSV'] = True
        for key, val in request.form.items():
            if key.startswith(sheet):
                output_config_dict[sheet]['Required CSV'] = True
        for key in output_config_dict[sheet].keys():
            if key not in ['Required CSV', 'Source']:
                for field, values in output_config_dict[sheet][key].items():
                    all_fields_dict[field] = values
        if output_config_dict[sheet]['Required CSV'] == True:
            sheets.append(sheet)



    print('------------')
    print(sheets)
    print('------------')
    cf_groups = ["sea_water", "sea_ice"]
    added_fields_dic = {}
    added_cf_names_dic = {}
    fields_list = []  # List of fields selected - dictates columns in template

    if request.method == "GET":

        return print_html_template(
            output_config_dict=output_config_dict,
            extra_fields_dict=extra_fields_dict,
            groups=groups,
            added_fields_dic=added_fields_dic,
            cf_standard_names=cf_standard_names,
            cf_groups=cf_groups,
            added_cf_names_dic=added_cf_names_dic,
            list_of_configs=list_of_configs,
            list_of_subconfigs=list_of_subconfigs,
            config=config,
            subconfig=subconfig,
        )

    if request.form["submitbutton"] not in ["selectConfig", "selectSubConfig"]:
        for field in cf_standard_names:
            if field["id"] in request.form and field["id"] not in output_config_fields:
                fields_list.append(field["id"])
                added_cf_names_dic[field["id"]] = {}
                added_cf_names_dic[field["id"]]["disp_name"] = field["id"]
                if field["description"] == None:
                    field["description"] = ""
                added_cf_names_dic[field["id"]][
                    "description"
                ] = f"{field['description']} \ncanonical units: {field['canonical_units']}"
                added_cf_names_dic[field["id"]]["format"] = "double precision"

        for field in all_fields_dict.keys():
            if field in request.form:
                if field not in added_cf_names_dic.keys():
                    fields_list.append(field)
                    if field in extra_fields_dict.keys():
                        added_fields_dic[field] = extra_fields_dict[field]

        for key in output_config_dict.keys():
            for field, values in output_config_dict[key].items():
                if field in request.form:
                    output_config_dict[key][field]["checked"] = "yes"

        if request.form["submitbutton"] == "generateTemplate":
            filepath = "/tmp/LFNL_template.xlsx"
            write_file(
                filepath,
                fields_list,
                metadata=True,
                conversions=True,
                configuration=config,
                subconfiguration=subconfig,
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
                list_of_configs=list_of_configs,
                list_of_subconfigs=list_of_subconfigs,
                config=config,
                subconfig=subconfig,
            )
    else:
        return print_html_template(
            output_config_dict=output_config_dict,
            extra_fields_dict=extra_fields_dict,
            groups=groups,
            added_fields_dic=added_fields_dic,
            cf_standard_names=cf_standard_names,
            cf_groups=cf_groups,
            added_cf_names_dic=added_cf_names_dic,
            list_of_configs=list_of_configs,
            list_of_subconfigs=list_of_subconfigs,
            config=config,
            subconfig=subconfig,
        )

@app.route("/update", methods=["POST"])
def update_config():
    """
    updates the ACDD Conventions and the CF standard names
    in the config directory.
    """
    try:
        acdd_conventions_update()
        cf_standard_names_update()
        return '"OK"'
    except Exception as e:
        return json.dumps(str(e)), 500



if __name__ == "__main__":
    app.run(debug=True)

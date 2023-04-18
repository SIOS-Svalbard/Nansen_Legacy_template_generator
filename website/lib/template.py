from flask import render_template

def print_html_template(output_config_dict, extra_fields_dict, groups, added_fields_dic, cf_standard_names, cf_groups, added_cf_names_dic, dwc_terms, added_dwc_terms_dic, list_of_configs, config, list_of_subconfigs=None, subconfig=None, compulsary_sheets=None):
    '''
    Prints the html template. Excluding closing the <main> element which must be closed at the bottom of this script
    '''
    added_fields_bool = {}
    for sheet in added_fields_dic.keys():
        if len(added_fields_dic[sheet]) > 0:
            added_fields_bool[sheet] = True
        else:
            added_fields_bool[sheet] = False

    added_cf_names_bool = {}
    for sheet in added_cf_names_dic.keys():
        if len(added_cf_names_dic) > 0:
            added_cf_names_bool[sheet] = True
        else:
            added_cf_names_bool[sheet] = False

    added_dwc_terms_bool = {}
    for sheet in added_dwc_terms_dic.keys():
        if len(added_dwc_terms_dic) > 0:
            added_dwc_terms_bool[sheet] = True
        else:
            added_dwc_terms_bool[sheet] = False

    if config == 'CF-NetCDF':
        description = 'Create spreadsheet templates that are easy to convert to CF-NetCDF files.'
    elif config == 'Learnings from Nansen Legacy logging system':
        description = 'Create spreadsheet templates that can be used in combination with the Learnings from Nansen Legacy logging system.'
    elif config == 'Darwin Core':
        description = 'Create spreadsheet templates that can be used to create Darwin Core cores and extension CSVs. Each sheet below represents one core or extension.'

    return render_template(
        "home.html",
        output_config_dict = output_config_dict,
        extra_fields_dict = extra_fields_dict,
        groups = groups,
        added_fields_dic = added_fields_dic,
        added_fields_bool = added_fields_bool,
        cf_standard_names=cf_standard_names,
        cf_groups=cf_groups,
        added_cf_names_dic=added_cf_names_dic,
        added_cf_names_bool=added_cf_names_bool,
        dwc_terms=dwc_terms,
        added_dwc_terms_dic=added_dwc_terms_dic,
        added_dwc_terms_bool=added_dwc_terms_bool,
        list_of_configs=list_of_configs,
        list_of_subconfigs=list_of_subconfigs,
        config=config,
        subconfig=subconfig,
        description=description,
        compulsary_sheets=compulsary_sheets
    )

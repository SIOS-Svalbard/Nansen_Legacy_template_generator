from flask import render_template

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

    return render_template(
        "generateTemplateIsolated.html",
        output_config_dict = output_config_dict,
        extra_fields_dict = extra_fields_dict,
        groups = groups,
        added_fields_dic = added_fields_dic,
        added_fields_bool = added_fields_bool,
        cf_standard_names=cf_standard_names,
        cf_groups=cf_groups,
        added_cf_names_dic=added_cf_names_dic,
        added_cf_names_bool=added_cf_names_bool,
        list_of_configs=list_of_configs,
        list_of_subconfigs=list_of_subconfigs,
        config=config,
        subconfig=subconfig,
        description=description
    )
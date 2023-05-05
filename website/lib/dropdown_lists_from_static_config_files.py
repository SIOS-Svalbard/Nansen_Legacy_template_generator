import pandas as pd

def get_dropdown_list_from_csv(field):
    df = pd.read_csv(f'website/config/dropdown_lists/{field}.csv')
    dropdown_list = list(df[field])
    return dropdown_list

def populate_dropdown_lists(fields_dict, config):

    fields_with_dropdown_list = [
        'kingdom',
        'sex',
        'sampleType',
        'gearType',
        'intendedMethod'
    ]

    if config == 'Learnings from Nansen Legacy logging system':
        fields_with_dropdown_list + [
            'storageTemp',
            'filter'
        ]

    if isinstance(fields_dict, list):
        fields_with_dropdowns = []
        for field in fields_dict:
            if field['id'] in fields_with_dropdown_list:
                field['valid']['validate'] = 'list'
                field['valid']['source'] = get_dropdown_list_from_csv(field['id'])
                field['valid']['error_message'] = 'Not a valid value, pick a value from the drop-down list.'
            fields_with_dropdowns.append(field)
        return fields_with_dropdowns

    else:
        for field in fields_dict.keys():
            if field in fields_with_dropdown_list:
                fields_dict[field]['valid']['validate'] = 'list'
                fields_dict[field]['valid']['source'] = get_dropdown_list_from_csv(field)
                fields_dict[field]['valid']['error_message'] = 'Not a valid value, pick a value from the drop-down list.'
        return fields_dict

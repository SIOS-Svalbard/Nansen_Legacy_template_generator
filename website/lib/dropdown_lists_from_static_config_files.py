import pandas as pd
from website import DROPDOWNS_PATH
import os

def get_dropdown_list_from_csv(field):
    filepath = os.path.join(DROPDOWNS_PATH, f'{field}.csv')
    df = pd.read_csv(filepath)
    dropdown_list = list(df[field])
    return dropdown_list

def populate_dropdown_lists(fields_dict, config):

    fields_with_dropdown_list = [
        'kingdom',
        'sex',
        'sampleType',
        'gearType',
        'intendedMethod',
        'filter',
        'storageTemperature'
    ]

<<<<<<< HEAD
    if config == ' Nansen Legacy logging system':
=======
    if config == 'Nansen Legacy logging system':
>>>>>>> ae0ef6d7bb9eebd7f03fd6cef1f05ca185652b79
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

#!/usr/bin/env python3

import sys
import os
from website.lib.pull_cf_standard_names import cf_standard_names_update
from website.lib.pull_acdd_conventions import acdd_conventions_update
from website.lib.pull_darwin_core_terms import dwc_terms_update, dwc_extensions_update

# available scopes
ACDD = 'acdd'
CF = 'cf'
DWC = 'dwc'

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
FIELDS_FILEPATH = os.path.join(BASE_PATH, 'website', 'config', 'fields')

scopes = sys.argv[1:]

for scope in scopes:
    print("Updating", scope)

    if scope == ACDD:
        acdd_conventions_update(FIELDS_FILEPATH)
    elif scope == CF:
        cf_standard_names_update(FIELDS_FILEPATH)
    elif scope == DWC:
        #dwc_terms_update(FIELDS_FILEPATH)
        dwc_extensions_update(FIELDS_FILEPATH)
    else:
        print("Ignore unknown scope", scope)

    print("Updated", scope)

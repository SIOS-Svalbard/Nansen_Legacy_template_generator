#!/usr/bin/env python3

import sys

from website.lib.pull_cf_standard_names import cf_standard_names_update
from website.lib.pull_acdd_conventions import acdd_conventions_update

# available scopes
ACDD = 'acdd'
CF = 'cf'

scopes = sys.argv[1:]

for scope in scopes:
    print("Updating", scope)

    if scope == ACDD:
        acdd_conventions_update()
    elif scope == CF:
        cf_standard_names_update()
    else:
        print("Ignore unknown scope", scope)

    print("Updated", scope)

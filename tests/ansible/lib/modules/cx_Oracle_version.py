#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
module: cx_Oracle_version
short_description: Test import of cx_Oracle
options: {}
'''

RETURN = r'''
version:
    type: str
'''

from ansible.module_utils.basic import AnsibleModule


import cx_Oracle

def main():
    module = AnsibleModule(
        argument_spec={},
        supports_check_mode=True,
    )

    try:
        module.exit_json(changed=False, version=cx_Oracle.version)
    except Exception:
        e = sys.exc_info()[1]
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()

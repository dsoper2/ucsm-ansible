#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_ucs_callhome
short_description: configures callhome on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures callhome on a cisco ucs server
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: "present"
    alert_throttling_admin_state:
        version_added: "1.0(1e)"
        description: alert throttling admin state
        required: false
        choices: ['on', 'off']
        default: "on"
    policy_owner:
        version_added: "2.1(1a)"
        description: policy owner
        required: false
        choices: ['local', 'pending-policy', 'policy']
        default: "local"
    name:
        version_added: "2.1(1a)"
        description: name
        required: false
    descr:
        version_added: "2.1(1a)"
        description: description
        required: false

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_callhome:
    alert_throttling_admin_state: "on"
    policy_owner: "local"
    name: "testname"
    descr: "description"
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                alert_throttling_admin_state=dict(type='str',
                                        choices=['on', 'off'], default="on"),
                policy_owner=dict(type='str',
                                choices=['local', 'pending-policy', 'policy'],
                                default="local"),
                name=dict(type='str'),
                descr=dict(type='str'),
    )


def _argument_custom():
    return dict(
        state=dict(default="present",
                   choices=['present', 'absent'],
                   type='str'),
    )


def _argument_connection():
    return  dict(
        # UcsHandle
        ucs_server=dict(type='dict'),

        # Ucs server credentials
        ucs_ip=dict(type='str'),
        ucs_username=dict(default="admin", type='str'),
        ucs_password=dict(type='str', no_log=True),
        ucs_port=dict(default=None),
        ucs_secure=dict(default=None),
        ucs_proxy=dict(default=None)
    )


def _ansible_module_create():
    argument_spec = dict()
    argument_spec.update(_argument_mo())
    argument_spec.update(_argument_custom())
    argument_spec.update(_argument_connection())

    return AnsibleModule(argument_spec,
                         supports_check_mode=True)


def _get_mo_params(params):
    from ansible.module_utils.cisco_ucs import UcsConnection
    args = {}
    for key in _argument_mo():
        if params.get(key) is None:
            continue
        args[key] = params.get(key)
    return args


def setup_callhome(server, module):
    from ucsm_apis.admin.callhome import callhome_enable
    from ucsm_apis.admin.callhome import callhome_disable
    from ucsm_apis.admin.callhome import callhome_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = callhome_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        callhome_enable(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        callhome_disable(server)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_callhome(server, module)
    except Exception as e:
        err = True
        result["msg"] = "setup error: %s " % str(e)
        result["changed"] = False

    return result, err


def main():
    from ansible.module_utils.cisco_ucs import UcsConnection

    module = _ansible_module_create()
    conn = UcsConnection(module)
    server = conn.login()
    result, err = setup(server, module)
    conn.logout()
    if err:
        module.fail_json(**result)
    module.exit_json(**result)


if __name__ == '__main__':
    main()


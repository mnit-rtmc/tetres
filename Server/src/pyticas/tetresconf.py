"""
This file contains functions related to parsing tetres.conf
"""

import common


def get_property(prop):
    """
    read property from specified file
    :rtype: str
    """

    try:
        with open(common.CONFIG_FILE_PATH, 'r') as f:
            for line in f.readlines():
                if not line or line.startswith('#'):
                    continue
                tmp = line.split('=')
                name = tmp[0]
                value = tmp[1]
                if name == prop:
                    return str(value).strip()
    except Exception as ex:
        pass

    return None

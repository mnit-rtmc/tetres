"""
This file contains functions related to parsing tetres.conf
"""

import sys, os, socket, getopt
import common
import dbinfo

def get_property(prop, pref_filename='/etc/tetres/tetres.conf'):
    """
    read property from specified file

    :rtype: str
    """

    # gets server/tetres.conf
    pref_filepath = os.path.join(os.path.dirname(common.CUR_PATH), pref_filename)

    try:
        with open(pref_filepath, 'r') as f:
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

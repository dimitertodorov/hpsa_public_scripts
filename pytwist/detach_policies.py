# Detach Patch Policies

import os
import re
import subprocess
import os
import sys
import getopt
import csv

from optparse import OptionParser


if (sys.platform == 'win32'):
    pytwist_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\smopylibs2')
    pylibs_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\agent\\pylibs')
    if os.path.isdir(pylibs_dir):
        pylibs_dir = (os.environ['SystemDrive'] + '\\Program Files\\Loudcloud\\Blackshadow')
        if os.path.isdir(pylibs_dir):
            raise 'The Opsware pylibs modules cannot be located'
else:
    pytwist_dir = '/opt/opsware/pylibs2'
    pylibs_dir = '/opt/opsware/agent/pylibs'
    if os.path.isdir(pylibs_dir):
        pylibs_dir = '/lc/blackshadow/coglib'
        if os.path.isdir(pylibs_dir):
            raise 'The Opsware pylibs modules cannot be located'
sys.path.append(pylibs_dir)
sys.path.append(pytwist_dir)
from pytwist import *
from pytwist.com.opsware.search import Filter
from pytwist.com.opsware.server import *
from pytwist.com.opsware.device import *
from pytwist.com.opsware.swmgmt import *

ts = twistserver.TwistServer()

if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='%prog [--user username --password password]')
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                      help="Password")
    parser.add_option("-i", "--id", action="store", dest="policy_id", metavar="policy_id", default=0,
                      help="Policy ID")

    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
    except getopt.GetoptError:
        parser.print_help()
        sys.exit(2)

    if opts.username and opts.password:
        ts.authenticate(opts.username, opts.password)
    elif os.environ.has_key('SA_USER') and os.environ.has_key('SA_PWD'):
        ts.authenticate(os.environ['SA_USER'], os.environ['SA_PWD'])
    else:
        print "Username and Password not provided. Script may fail unless running in OGSH. \n Specify with -u username -p password"

    try:
        server_service = ts.server.ServerService
        server_script_service = ts.script.ServerScriptService
        device_group_service = ts.device.DeviceGroupService
        auth_service = ts.fido.AuthorizationService
        swps = ts.swmgmt.SoftwarePolicyService
        wpps=ts.swmgmt.WindowsPatchPolicyService
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)

    if long(opts.policy_id)!=0:
        print long(opts.policy_id)
        wppref=WindowsPatchPolicyRef(long(opts.policy_id))
        wppvo=wpps.getWindowsPatchPolicyVO(wppref)
        if (len(wppvo.associatedServers)!=0):
            servers=wppvo.associatedServers
            wpps.detachFromPolicies([wppref],servers)
        if (len(wppvo.associatedDeviceGroups)!=0):
            device_groups=wppvo.associatedDeviceGroups
            wpps.detachFromPolicies([wppref],device_groups)





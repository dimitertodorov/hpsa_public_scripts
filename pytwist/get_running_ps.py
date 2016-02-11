# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
"""
Get NW Info
"""

#Import some basic python modules
import os
import sys
import getopt
from itertools import islice, chain
import time

#Import the OptionParser to allow for CLI options
from optparse import OptionParser
import simplejson as json
# HPSA - Depending on Windows/Unix select the directories containing the pytwist libraries.
if (sys.platform == 'win32'):
    pytwist_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\smopylibs2')
    pylibs_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\agent\\pylibs')
else:
    pytwist_dir = '/opt/opsware/pylibs2'
    pylibs_dir = '/opt/opsware/agent/pylibs2'

# Add the pytwist/pylibs directories to the path and import necessary modules.
sys.path.append(pylibs_dir)
sys.path.append(pytwist_dir)
from pytwist import *
from pytwist.com.opsware.search import Filter


from pytwist.com.opsware.fido import OperationConstants
from pytwist.com.opsware.device import DeviceGroupRef
from pytwist.com.opsware.job import JobRef,JobNotification,JobSchedule,JobInfoVO
from pytwist.com.opsware.script import ServerScriptRef, ServerScriptJobArgs

#Initialize the twist
ts = twistserver.TwistServer()


# Main Script
if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='python %prog [--file "CSV filename" -s script_id -e email] Optional: [-u username -p password]')
    parser.add_option("-f", "--filter", action="store", dest="filter", metavar="filter", default="(ServerVO.hostName CONTAINS ASOJIASOJIDSAOIAJSDA)",
                      help="Filter")
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                      help="Password")
    parser.add_option("-c", "--custattr", action="store", dest="custattr", metavar="custattr", default="ITS_TEST",
                      help="CustomAttribute")



    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
        if not opts.custattr:
            parser.error("custattr required")
        if not opts.filter:
            parser.error("Filter required")
    except getopt.GetoptError:
        parser.print_help()
        sys.exit(2)
    if opts.username and opts.password:
        ts.authenticate(opts.username,opts.password)
    elif os.environ.has_key('SA_USER') and os.environ.has_key('SA_PWD'):
        ts.authenticate(os.environ['SA_USER'],os.environ['SA_PWD'])
    else:
        print "Username and Password not provided. Script may fail unless running in OGSH. \nSpecify with -u username -p password"

    try:
        server_service=ts.server.ServerService
        server_script_service=ts.script.ServerScriptService
        device_group_service=ts.device.DeviceGroupService
        auth_service=ts.fido.AuthorizationService
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)

    sh_info=[]
    server_filter = Filter()
    server_filter.expression="(%s)" % (opts.filter)
    server_refs=server_service.findServerRefs(server_filter)
    shvos=server_service.getServerHardwareVOs(server_refs)
    for sh in shvos:
        server={}
        server['name']=sh.ref.name
        server['id']=sh.ref.id
        server['interfaces']=[]
        for intf in sh.interfaces:
            interface={}
            interface['ipAddress']=intf.ipAddress

            interface['hardwareAddress']=intf.hardwareAddress
            interface['netmask']=intf.netmask
            interface['slot']=intf.slot
            interface['enabled']=intf.enabled
            server['interfaces'].append(interface)
        sh_info.append(server)
    print json.dumps(sh_info)






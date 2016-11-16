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
import re
from itertools import islice, chain
import time
from datetime import datetime
import csv

#Import the OptionParser to allow for CLI options
from optparse import OptionParser
import json
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
        print("Username and Password not provided. Script may fail unless running in OGSH. \nSpecify with -u username -p password")

    try:
        server_service=ts.server.ServerService
        server_script_service=ts.script.ServerScriptService
        device_group_service=ts.device.DeviceGroupService
        auth_service=ts.fido.AuthorizationService
    except:
        print("Error initializing services to HPSA")
        sys.exit(2)

    sh_info=[]
    server_filter = Filter()
    server_filter.expression="(%s)" % (opts.filter)
    server_refs=server_service.findServerRefs(server_filter)
    server_vos=server_service.getServerVOs(server_refs)
    for server_vo in server_vos:
        server={}
        server['name']=server_vo.ref.name
        server['id']=server_vo.ref.id
        server['tools_version']="0"
        server['tools_date']="0"
        server['tools_count']=0
        pkgs = server_service.getInstalledSoftware(server_vo.ref)
        for p in pkgs:
            vmware_re = re.compile(r"vmware tools", flags=re.IGNORECASE)
            if p.name:
                match = re.search(vmware_re,p.name)
            if match:
                server['tools_count'] = server['tools_count']+1
                server['tools_version']=p.version
                server_service.setCustAttr(server_vo.ref,'ITS_VMWARE_TOOLS',p.version)
                server['tools_date']=datetime.fromtimestamp(p.beginDate).strftime("%A, %d. %B %Y %I:%M%p")
                print("%s %s" % (p.version, server_vo.ref.name))
        server_service.setCustAttr(server_vo.ref,'ITS_VMWARE_TOOLS_COUNT',"%s" % server['tools_count'])
        sh_info.append(server)
    #print(sh_info)
    print json.dumps(sh_info, sort_keys=True, indent=4, separators=(',', ': '))
    keys=['name','id','tools_version','tools_date','tools_count']
    f=open("N:\\vmtools.csv",'wb')
    dict_writer=csv.DictWriter(f,keys,quoting=csv.QUOTE_ALL)
    dict_writer.writer.writerow(keys)
    dict_writer.writerows(sh_info)






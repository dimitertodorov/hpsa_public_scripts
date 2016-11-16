# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
"""
Get Hypervisor info for VMs
"""

#Import some basic python modules
import os
import sys
import getopt
from itertools import islice, chain
import time
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
from pytwist.com.opsware.v12n import V12nVirtualServerService

#Initialize the twist
ts = twistserver.TwistServer()


# Main Script
if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='python %prog [--file "CSV filename" -s script_id -e email] Optional: [-u username -p password]')
    parser.add_option("-f", "--filter", action="store", dest="filter", metavar="filter", default="(hostname CONTAINS CTSPSCLAEMPRN01)",
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
        virtual_service = ts.v12n.V12nVirtualServerService
        hv_service = ts.v12n.V12nHypervisorService
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)

    sh_info=[]
    server_filter = Filter()
    server_filter.expression="(%s)" % (opts.filter)
    server_filter.objectType='v12n_virtual_machine'
    server_refs=virtual_service.findV12nVirtualServerRefs(server_filter)
    shvos=virtual_service.getV12nVirtualServerVOs(server_refs)
    for sh in shvos:
        print sh.detail.name

        server={}
        server['name']=sh.detail.name
        server['hypervisor']=sh.hypervisor.name
        hv_vo = hv_service.getV12nHypervisorVO(sh.hypervisor)
        hv_hw_vo = server_service.getServerHardwareVO(hv_vo.server)
        server['hypervisor_cpu_count'] = len(hv_hw_vo.cpus)
        server['hypervisor_cpu_model'] = hv_hw_vo.cpus[0].model
        sh_info.append(server)
    print sh_info
    keys=['name','hypervisor',
          'hypervisor_cpu_count',
          'hypervisor_cpu_model']
    f=open("hypervisor_info.csv",'wb')
    dict_writer=csv.DictWriter(f,keys,quoting=csv.QUOTE_ALL)
    dict_writer.writer.writerow(keys)
    dict_writer.writerows(sh_info)






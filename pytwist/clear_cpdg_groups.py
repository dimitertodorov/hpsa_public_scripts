# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4 :
# Please do not change the two lines above. See PEP 8, PEP 263.
# Dimiter Todorov - 2014
# Run a server script from pytwist. Can either run on a server with the agent. Or from the Global Shell
# If running from a server with agent, username/password is required.
# usage: python run_script_from_csv.py [--file "CSV filename" -s script_id -e email] Optional: [-u username -p password]
# The file should be a list of hostnames on which to run the script. The first line should be 'hostname' as a header
import os
import re
import subprocess
import os
import sys
import getopt
import csv
import time

from optparse import OptionParser


if (sys.platform == 'win32'):
    pytwist_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\smopylibs2')
    pylibs_dir = (os.environ['SystemDrive'] + '\\Program Files\\Opsware\\agent\\pylibs')
else:
    pytwist_dir = '/opt/opsware/pylibs2'
    pylibs_dir = '/opt/opsware/agent/pylibs2'

sys.path.append(pylibs_dir)
sys.path.append(pytwist_dir)
from pytwist import *
from pytwist.com.opsware.search import Filter
from pytwist.com.opsware.device import DeviceGroupRef
from pytwist.com.opsware.job import JobRef,JobNotification,JobSchedule,JobInfoVO
from pytwist.com.opsware.script import ServerScriptRef, ServerScriptJobArgs

ts = twistserver.TwistServer()




def default_notify(email):
    jobNotify=JobNotification()
    jobNotify.onSuccessOwner=email
    jobNotify.onFailureOwner=email
    jobNotify.onFailureRecipients=[email]
    jobNotify.onSuccessRecipients=[email]
    jobNotify.onCancelRecipients=[email]
    return jobNotify



if (__name__ == '__main__'):
    parser = OptionParser(description=__doc__, version="0.0.1",
                          usage='python %prog [--file "CSV filename" -s script_id -e email] Optional: [-u username -p password]')
    parser.add_option("-f", "--file", action="store", dest="file_name", metavar="FILE_NAME", default="itr_list.csv",
                      help="File Name")
    parser.add_option("-u", "--user", action="store", dest="username", metavar="username", default="",
                      help="User Name")
    parser.add_option("-p", "--password", action="store", dest="password", metavar="password", default="",
                      help="Password")
    parser.add_option("-g", "--group_pattern", action="store", dest="group_pattern", metavar="group_pattern", default="",
                      help="group ID to Add")

    try:
        (opts, args) = parser.parse_args(sys.argv[1:])
        if not opts.group_pattern:
            parser.error("Group Pattern Required")
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
    except:
        print "Error initializing services to HPSA"
        sys.exit(2)

    input_file=csv.DictReader(open(opts.file_name))
    server_tuple=[]
    i=0
    for row in input_file:
        i=i+1
        server_filter = Filter()
        server_filter.expression="ServerVO.hostName BEGINS_WITH %s" % row["hostname"].split(".")[0]
        server_refs=server_service.findServerRefs(server_filter)

        if(len(server_refs)==1):
            one_ref=server_refs[0]
            device_groups=server_service.getDeviceGroups(one_ref)
            device_groups_to_remove=[]
            for dg in device_groups:
                if re.match(opts.group_pattern,dg.name):
                    print "Removing %s from %s" % (one_ref,dg)
                    device_groups_to_remove.append(dg)
            if device_groups_to_remove:
                server_service.removeDeviceGroups(one_ref,device_groups_to_remove)

        else:
            print "Found %s entries for:%s" % (len(server_refs),row["hostname"])





